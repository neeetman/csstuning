import sys
import unittest
from pathlib import Path

from csstuning.dbms.dbms_benchmark import MySQLBenchmark

# sys.path.append("/home/anshao/csstuning")


class TestMySQLBenchmark(unittest.TestCase):
    def setUp(self):
        self.benchmark = MySQLBenchmark(workload="twitter")
        print("\n" + "=" * 50)
        print(f"Starting Test：{self._testMethodName}")
        print("=" * 50)

    def test_01_initialization(self):
        self.assertTrue(
            Path(self.benchmark.mysql_data_dir).exists(),
            "MySQL data directory was not created.",
        )
        self.assertTrue(
            Path(self.benchmark.benchbase_config_dir).exists(),
            "BenchBase data directory was not created.",
        )

    def test_02_start_mysql(self):
        result = self.benchmark.start_mysql_and_wait(
            custom_config=False, limit_resources=False
        )
        self.assertTrue(result)

    def test_03_stop_mysql(self):
        self.benchmark.start_mysql_and_wait(custom_config=False, limit_resources=False)
        self.benchmark._gracefully_stop_mysql_container(
            self.benchmark.mysql_container_name
        )

    # def test_04_create_database(self):
    #     self.benchmark.create_database()

    # def test_05_execute_benchmark(self):
    #     self.benchmark.start_mysql_and_wait(custom_config=False, limit_resources=False)
    #     self.benchmark.execute_benchmark()
    #     self.benchmark._gracefully_stop_mysql_container(
    #         self.benchmark.mysql_container_name
    #     )

    def test_06_set_and_run(self):
        self.benchmark.run(
            {
                "max_heap_table_size": 328537119,
                "tmp_table_size": 468968533,
                "innodb_doublewrite": "ON",
                "query_prealloc_size": 97631047,
                "innodb_thread_concurrency": 8,
                "innodb_io_capacity_max": 11333,
                "log_output": "NONE",
                "general_log": "OFF",
                "max_length_for_sort_data": 4856370,
                "innodb_buffer_pool_size": 15047652032,
                "innodb_lru_scan_depth": 7348,
            }
        )

    def tearDown(self):
        # Clean up resources after each test
        self.benchmark._gracefully_stop_mysql_container(
            self.benchmark.mysql_container_name
        )
        print("=" * 50)
        print(f"Finished Test：{self._testMethodName}")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    unittest.main()
