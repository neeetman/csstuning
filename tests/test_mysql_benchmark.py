import sys
import unittest
from pathlib import Path

from csstuning.dbms.dbms_benchmark import MySQLBenchmark

sys.path.append("/home/anshao/csstuning")


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

    def test_05_execute_benchmark(self):
        self.benchmark.start_mysql_and_wait(custom_config=False, limit_resources=False)
        self.benchmark.execute_benchmark()
        self.benchmark._gracefully_stop_mysql_container(
            self.benchmark.mysql_container_name
        )

    def test_06_set_and_run(self):
        self.benchmark.run(
            {
                "max_heap_table_size": 328537119,
                "tmp_table_size": 468968533,
                "innodb_doublewrite": "ON",
                "query_prealloc_size": 97631047,
                "innodb_thread_concurrency": 838,
                "innodb_io_capacity_max": 11333,
                "log_output": "NONE",
                "general_log": "OFF",
                "max_length_for_sort_data": 4856370,
                "innodb_buffer_pool_size": 15047652032,
                "innodb_lru_scan_depth": 7348,
                "transaction_alloc_block_size": 107241,
                "expire_logs_days": 70,
                "max_allowed_packet": 943720511,
                "key_cache_age_threshold": 26630,
                "innodb_adaptive_max_sleep_delay": 320108,
                "innodb_log_file_size": 95599929,
                "query_cache_limit": 17093664,
                "innodb_stats_transient_sample_pages": 69,
                "innodb_ft_total_cache_size": 231102789,
                "innodb_adaptive_flushing_lwm": 60,
                "div_precision_increment": 30,
                "innodb_purge_batch_size": 1674,
                "flush_time": 9,
                "transaction_prealloc_size": 6558,
                "innodb_ft_result_cache_limit": 2112482557,
                "default_week_format": 7,
                "innodb_log_write_ahead_size": 11262,
                "skip_name_resolve": "ON",
                "innodb_change_buffering": "none",
                "innodb_compression_pad_pct_max": 66,
                "join_buffer_size": 450900925,
                "lower_case_table_names": 1,
                "innodb_purge_rseg_truncate_frequency": 40,
                "net_write_timeout": 80,
                "innodb_sync_array_size": 568,
                "innodb_online_alter_log_max_size": 11765091297066850304,
                "require_secure_transport": "OFF",
                "autocommit": "OFF",
                "concurrent_insert": "AUTO",
                "innodb_ft_cache_size": 9582739,
                "session_track_gtids": "OWN_GTID",
                "innodb_change_buffer_max_size": 3,
                "innodb_flush_log_at_trx_commit": "2",
                "innodb_default_row_format": "REDUNDANT",
                "binlog_cache_size": 3867644350,
                "innodb_page_cleaners": 6,
                "table_open_cache_instances": 4,
                "session_track_schema": "OFF",
                "innodb_strict_mode": "OFF",
                "innodb_ft_min_token_size": 15,
                "innodb_undo_log_truncate": "OFF",
                "explicit_defaults_for_timestamp": "OFF",
                "innodb_sort_buffer_size": 12677083,
                "ngram_token_size": 8,
                "innodb_disable_sort_file_cache": "ON",
                "updatable_views_with_limit": "YES",
                "innodb_stats_include_delete_marked": "OFF",
                "mysql_native_password_proxy_users": "OFF",
                "innodb_use_native_aio": "OFF",
                "local_infile": "ON",
                "innodb_table_locks": "OFF",
                "log_builtin_as_identified_by_password": "OFF",
                "innodb_file_per_table": "ON",
                "innodb_max_dirty_pages_pct_lwm": 2,
                "innodb_stats_on_metadata": "OFF",
                "ft_min_word_len": 4,
                "old_passwords": "2",
                "keep_files_on_create": "OFF",
                "innodb_flush_sync": "OFF",
                "innodb_ft_enable_diag_print": "ON",
                "innodb_api_disable_rowlock": "OFF",
                "log_slave_updates": "ON",
                "innodb_cmp_per_index_enabled": "OFF",
                "net_read_timeout": 35,
                "binlog_direct_non_transactional_updates": "ON",
                "binlog_row_image": "minimal",
                "binlog_error_action": "IGNORE_ERROR",
                "slow_query_log": "ON",
                "innodb_log_files_in_group": 10,
                "automatic_sp_privileges": "OFF",
                "innodb_log_compressed_pages": "ON",
                "binlog_order_commits": "ON",
                "binlog_rows_query_log_events": "OFF",
                "innodb_adaptive_flushing": "ON",
                "log_statements_unsafe_for_binlog": "ON",
                "offline_mode": "ON",
                "binlog_format": "MIXED",
                "log_bin_use_v1_row_events": "OFF",
                "low_priority_updates": "OFF",
                "innodb_api_enable_binlog": "ON",
                "innodb_rollback_on_timeout": "ON",
                "log_syslog_include_pid": "ON",
                "delay_key_write": "OFF",
                "log_timestamps": "UTC",
                "table_definition_cache": 147987,
                "innodb_stats_auto_recalc": "ON",
                "innodb_commit_concurrency": 684,
                "show_compatibility_56": "ON",
                "query_cache_wlock_invalidate": "ON",
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
