CMAKE_MINIMUM_REQUIRED(VERSION 3.0)

MACRO(CREATE_RA_PHYSICAL_TEST NAME)
    CREATE_NAMED_TEST(ra_physical_${NAME} ${NAME})
    TARGET_LINK_LIBRARIES(ra_physical_${NAME}
        common
        fmt)
    ADD_DEPENDENCIES(ra_physical_${NAME}
        ${FMT_PROJECT}
        ${RANGE-V3_PROJECT}
        common)
ENDMACRO(CREATE_RA_PHYSICAL_TEST)

CREATE_RA_PHYSICAL_TEST(cross_test)
CREATE_RA_PHYSICAL_TEST(filter_test)
CREATE_RA_PHYSICAL_TEST(group_by_test)
CREATE_RA_PHYSICAL_TEST(hash_join_test)
CREATE_RA_PHYSICAL_TEST(iterable_test)
CREATE_RA_PHYSICAL_TEST(map_test)
CREATE_RA_PHYSICAL_TEST(flat_map_test)
CREATE_RA_PHYSICAL_TEST(project_test)

MACRO(CREATE_RA_PHYSICAL_BENCHMARK NAME)
    CREATE_NAMED_BENCHMARK(ra_physical_${NAME} ${NAME})
    TARGET_LINK_LIBRARIES(ra_physical_${NAME}
        common
        fmt)
    ADD_DEPENDENCIES(ra_physical_${NAME}
        ${FMT_PROJECT}
        ${RANGE-V3_PROJECT}
        common)
ENDMACRO(CREATE_RA_PHYSICAL_BENCHMARK)

CREATE_RA_PHYSICAL_BENCHMARK(cross_bench)
CREATE_RA_PHYSICAL_BENCHMARK(filter_bench)
CREATE_RA_PHYSICAL_BENCHMARK(flat_map_bench)
CREATE_RA_PHYSICAL_BENCHMARK(group_by_bench)
CREATE_RA_PHYSICAL_BENCHMARK(hash_join_bench)
CREATE_RA_PHYSICAL_BENCHMARK(iterable_bench)
CREATE_RA_PHYSICAL_BENCHMARK(map_bench)
CREATE_RA_PHYSICAL_BENCHMARK(project_bench)
