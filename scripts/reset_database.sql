-- psql -f reset_database.sql

-- http://stackoverflow.com/questions/3327312/drop-all-tables-in-postgresql
DROP SCHEMA PUBLIC CASCADE;
CREATE SCHEMA PUBLIC;

CREATE TABLE Nodes (
    id      bigint PRIMARY KEY,
    name    text   NOT NULL,
    address text   NOT NULL
);

CREATE TABLE Collections (
    node_id           bigint  NOT NULL,
    collection_name   text    NOT NULL,
    collection_type   text    NOT NULL,
    column_names      text[]  NOT NULL,
    black_box_lineage boolean NOT NULL,
    PRIMARY KEY (node_id, collection_name)
);

CREATE TABLE Rules (
    node_id      bigint  NOT NULL,
    rule_number  integer NOT NULL,
    is_bootstrap boolean NOT NULL,
    rule         text    NOT NULL,
    PRIMARY KEY (node_id, rule_number, is_bootstrap)
);
