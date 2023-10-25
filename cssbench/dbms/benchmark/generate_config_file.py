import argparse
import os
from jinja2 import Environment, FileSystemLoader


def generate_config(template_path, output_path, config_dict):
    # Need to use PackageLoader when make this a package
    working_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(working_dir, output_path)

    env = Environment(loader=FileSystemLoader(working_dir))
    template = env.get_template(template_path)
    config = template.render(config_dict)

    with open(output_path, "w") as file:
        file.write(config)


if __name__ == "__main__":
    test_config = {
        "long_query_time": 10,
        "max_connections": 500,
        "wait_timeout": 28800,
        "interactive_timeout": 28800,
        "skip-name-resolve": True,
        "query_cache_limit": 2097152,
        "query_cache_size": 33554432,
        "query_cache_type": 0,
        "sort_buffer_size": 4194304,
        "read_rnd_buffer_size": 1048576,
        "join_buffer_size": 1048576,
        "tmp_table_size": 33554432,
        "max_heap_table_size": 33554432,
        "thread_cache_size": 50,
        "table_open_cache": 2000,
        "table_definition_cache": 1400,
        "open_files_limit": 5000,
        "binlog_cache_size": 32768,
        "key_buffer_size": 134217728,
        "thread_handling": "one-thread-per-connection",
        "thread_pool_size": 16,
        "performance_schema": True,
        "innodb_autoinc_lock_mode": 2,
        "binlog_format": "ROW",
        "innodb_flush_log_at_trx_commit": 1,
        "innodb_file_per_table": True,
        "innodb_buffer_pool_size": 1073741824,
        "innodb_redo_log_capacity": 104857600,
        "innodb_log_file_size": 268435456,
        "innodb_buffer_pool_instances": 8,
        "innodb_buffer_pool_chunk_size": 134217728,
        "innodb_log_buffer_size": 16777216,
        "innodb_stats_on_metadata": False,
        "innodb_thread_concurrency": 0,
        "read_buffer_size": 131072,
        "innodb_lock_wait_timeout": 50,
    }

    path = os.path.join(os.path.dirname(__file__), "mysql_template.cnf")
    generate_config("mysql_template.cnf", "my.cnf", test_config)

    