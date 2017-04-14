#include "fluent/fluent_builder.h"

#include <cstddef>

#include <chrono>
#include <tuple>
#include <utility>

#include "glog/logging.h"
#include "gtest/gtest.h"
#include "zmq.hpp"

#include "fluent/infix.h"
#include "lineagedb/connection_config.h"
#include "lineagedb/noop_client.h"
#include "ra/all.h"

namespace fluent {

TEST(FluentBuilder, SimpleBuildCheck) {
  zmq::context_t context(1);
  lineagedb::ConnectionConfig conf;
  auto f =
      fluent<lineagedb::NoopClient>("name", "inproc://yolo", &context, conf)
          .table<std::string, int>("t", {{"x", "y"}})
          .scratch<std::string, int>("s", {{"x", "y"}})
          .channel<std::string, int>("c", {{"addr", "x"}})
          .stdin()
          .stdout()
          .periodic("p", std::chrono::milliseconds(100))
          .RegisterRules(
              [](auto& t, auto& s, auto& c, auto& in, auto& out, auto& p) {
                using namespace fluent::infix;
                (void)in.Iterable();
                (void)p.Iterable();
                auto rule_a = t <= s.Iterable();
                auto rule_b = t += s.Iterable();
                auto rule_c = t -= s.Iterable();
                auto rule_d = s <= s.Iterable();
                auto rule_e = c <= s.Iterable();
                auto rule_f = out <= (s.Iterable() | ra::project<0>());
                auto rule_g = out += (s.Iterable() | ra::project<0>());
                return std::make_tuple(rule_a, rule_b, rule_c, rule_d, rule_e,
                                       rule_f, rule_g);
              });
}

}  // namespace fluent

int main(int argc, char** argv) {
  google::InitGoogleLogging(argv[0]);
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
