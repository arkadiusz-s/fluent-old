import flask
import psycopg2

app = flask.Flask(__name__)
db = psycopg2.connect("dbname=vagrant")

# Helper Functions #############################################################
def with_cursor(f, *args):
    with db.cursor() as cur:
        return flask.jsonify(f(cur, *args))

def escape(x):
    if type(x) == long:
        return str(x)
    else:
        return x

# Functions ####################################################################
def nodes_(cur):
    cur.execute("SELECT name, address FROM nodes;")
    return cur.fetchall()

def node_address_(cur, name):
    cur.execute("""
        SELECT N.address
        FROM Nodes N
        WHERE N.name = %s;
    """, (name,))
    rows = cur.fetchall()
    assert len(rows) == 1
    return rows[0][0]

def node_bootstrap_rules_(cur, name):
    cur.execute("""
        SELECT R.rule
        FROM Nodes N, Rules R
        WHERE N.name = %s AND N.id = R.node_id AND R.is_bootstrap
        ORDER BY R.rule_number;
    """, (name,))
    return [t[0] for t in cur.fetchall()]

def node_rules_(cur, name):
    cur.execute("""
        SELECT R.rule
        FROM Nodes N, Rules R
        WHERE N.name = %s AND N.id = R.node_id AND (NOT R.is_bootstrap)
        ORDER BY R.rule_number;
    """, (name,))
    return [t[0] for t in cur.fetchall()]

def node_collection_names_(cur, name):
    cur.execute("""
        SELECT C.collection_name
        FROM Nodes N, Collections C
        WHERE N.name = %s AND N.id = C.node_id;
    """, (name,))
    return [t[0] for t in cur.fetchall()]

def node_collection_(cur, node_name, collection_name, time):
    collection = {}

    # Fetch type and column names.
    cur.execute("""
        SELECT C.collection_type, C.column_names
        FROM Nodes N, Collections C
        WHERE N.name = %s AND N.id = C.node_id AND collection_name = %s;
    """, (node_name, collection_name))
    rows = cur.fetchall()
    assert len(rows) == 1, rows
    collection["type"] = rows[0][0]
    collection["column_names"] = rows[0][1]

    # Fetch tuples.
    cur.execute("""
        SELECT *
        FROM {}_{}
        WHERE (time_inserted = %s AND time_inserted = time_deleted) OR
              (time_inserted <= %s AND (time_deleted IS NULL OR
                                        time_deleted > %s))
    """.format(node_name, collection_name), (time, time, time))
    collection["tuples"] = [[escape(x) for x in t] for t in cur.fetchall()]

    return collection

def backwards_lineage_(cur, node_name, collection_name, hash, time):
    # The time of the most recent insertion of the tuple.
    cur.execute("""
        SELECT MAX(time_inserted)
        FROM {}_{}
        WHERE hash = %s AND (
                  (time_inserted = %s AND time_inserted = time_deleted) OR
                  (time_inserted <= %s AND (time_deleted IS NULL OR
                                            time_deleted > %s))
              );
    """.format(node_name, collection_name), (hash, time, time, time))
    rows = cur.fetchall()
    assert len(rows) == 1, rows
    latest_insert_time = rows[0][0]

    # The backwards lineage.
    cur.execute("""
        SELECT
            N.name,
            L.dep_collection_name,
            L.dep_tuple_hash,
            L.dep_time
        FROM Nodes N, {}_lineage L
        WHERE N.id = L.dep_node_id AND
              L.collection_name = %s AND
              L.tuple_hash = %s AND
              time = %s;
    """.format(node_name), (collection_name, hash, latest_insert_time))
    lineage_tuples = []
    rows = [t for t in cur.fetchall()]
    for row in rows:
        t = {
            "node_name": row[0],
            "collection_name": row[1],
            "hash": escape(row[2]),
            "time": row[3],
        }

        # TODO(mwhittaker): Document.
        if t["time"] is None:
            cur.execute("""
                SELECT MAX(time_inserted)
                FROM {}_{}
                WHERE hash = %s AND time_inserted <= %s
            """.format(t["node_name"], t["collection_name"]),
            (t["hash"], latest_insert_time))
            time_rows = cur.fetchall()
            assert len(time_rows) == 1, time_rows
            t["time"] = time_rows[0][0]

        lineage_tuples.append(t)
    return lineage_tuples

# Endpoints ####################################################################
@app.route("/")
def index():
    return flask.send_file("index.html")

@app.route("/nodes")
def nodes():
    return with_cursor(nodes_)

@app.route("/node_address")
def node_address():
    node_name = flask.request.args.get("node_name", "")
    assert node_name is not None
    return with_cursor(node_address_, node_name)

@app.route("/node_bootstrap_rules")
def node_bootstrap_rules():
    node_name = flask.request.args.get("node_name", "")
    assert node_name is not None
    return with_cursor(node_bootstrap_rules_, node_name)

@app.route("/node_rules")
def node_rules():
    node_name = flask.request.args.get("node_name", "")
    assert node_name is not None
    return with_cursor(node_rules_, node_name)

@app.route("/node_collection_names")
def node_collection_names():
    node_name = flask.request.args.get("node_name", "")
    assert node_name is not None
    return with_cursor(node_collection_names_, node_name)

@app.route("/node_collection")
def node_collection():
    node_name = flask.request.args.get("node_name")
    collection_name = flask.request.args.get("collection_name")
    time = flask.request.args.get("time", type=int)
    assert node_name is not None
    assert collection_name is not None
    assert time is not None
    return with_cursor(node_collection_, node_name, collection_name, time)

@app.route("/backwards_lineage")
def backwards_lineage():
    node_name = flask.request.args.get("node_name", "")
    collection_name = flask.request.args.get("collection_name", "")
    hash = flask.request.args.get("hash", 0, type=int)
    time = flask.request.args.get("time", 0, type=int)
    assert node_name is not None
    assert collection_name is not None
    assert hash is not None
    assert time is not None
    return with_cursor(backwards_lineage_, node_name, collection_name, hash,
                       time)
