#ifndef FLUENT_TABLE_H_
#define FLUENT_TABLE_H_

#include <algorithm>
#include <iterator>
#include <set>
#include <type_traits>
#include <utility>

#include "range/v3/all.hpp"

#include "fluent/collection.h"
#include "fluent/rule_tags.h"
#include "ra/ra_util.h"

namespace fluent {

template <typename... Ts>
class Table : public Collection<Ts...> {
 public:
  explicit Table(const std::string& name) : Collection<Ts...>(name) {}

  template <typename RA>
  void Merge(const RA& ra) {
    ra::BufferRaInto(ra, &this->MutableGet());
  }

  template <typename RA>
  void DeferredMerge(const RA& ra) {
    ra::StreamRaInto(ra, &deferred_merge_);
  }

  template <typename RA>
  void DeferredDelete(const RA& ra) {
    ra::StreamRaInto(ra, &deferred_delete_);
  }

  template <typename Rhs>
  std::tuple<Table<Ts...>*, MergeTag, typename std::decay<Rhs>::type>
  operator<=(Rhs&& rhs) {
    return {this, MergeTag(), std::forward<Rhs>(rhs)};
  }

  template <typename Rhs>
  std::tuple<Table<Ts...>*, DeferredMergeTag, typename std::decay<Rhs>::type>
  operator+=(Rhs&& rhs) {
    return {this, DeferredMergeTag(), std::forward<Rhs>(rhs)};
  }

  template <typename Rhs>
  std::tuple<Table<Ts...>*, DeferredDeleteTag, typename std::decay<Rhs>::type>
  operator-=(Rhs&& rhs) {
    return {this, DeferredDeleteTag(), std::forward<Rhs>(rhs)};
  }

  void Tick() override {
    this->MutableGet().insert(
        std::make_move_iterator(std::begin(deferred_merge_)),
        std::make_move_iterator(std::end(deferred_merge_)));
    for (const std::tuple<Ts...>& t : deferred_delete_) {
      this->MutableGet().erase(t);
    }

    deferred_merge_.clear();
    deferred_delete_.clear();
  }

 private:
  std::set<std::tuple<Ts...>> deferred_merge_;
  std::set<std::tuple<Ts...>> deferred_delete_;
};

}  // namespace fluent

#endif  // FLUENT_TABLE_H_
