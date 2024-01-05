import argparse
import time

import pymysql
from tqdm import tqdm

from csstuning.dbms.dbms_benchmark import MySQLBenchmark

benchmarks = {
    "tpcc": [
        "warehouse",
        "district",
        "customer",
        "item",
        "stock",
        "oorder",
        "history",
        "order_line",
        "new_order",
    ],
    "twitter": ["user_profiles", "tweets", "follows", "added_tweets", "followers"],
    "smallbank": ["accounts", "checking", "savings"],
    "sibench": ["sitest"],
    "voter": [
        "contestants",
        "votes",
        "v_votes_by_contestant_number_state",
        "v_votes_by_phone_number",
        "area_code_state",
    ],
    "tatp": ["subscriber", "special_facility", "access_info", "call_forwarding"],
}

estimated_sizes = {
    "sibench": 0.02,
    "voter": 0.09,
    "smallbank": 2362.86,
    "twitter": 6325.08,
    "tatp": 6731.00,
    "tpcc": 20237.19,
}


def get_benchmark_size(cursor, tables):
    total_size = 0
    for table in tables:
        query = f"""
            SELECT
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'size_in_mb' 
            FROM 
                tables 
            WHERE 
                table_schema = 'benchbase' AND
                table_name = '{table}';
        """
        cursor.execute(query)
        result = cursor.fetchone()
        if result and result["size_in_mb"] is not None:
            total_size += result["size_in_mb"]
        else:
            total_size += 0
    return float(total_size)


def main():
    parser = argparse.ArgumentParser(description="Monitor benchmark loading progress.")
    parser.add_argument("benchmark", help="Name of the benchmark to monitor")
    args = parser.parse_args()
    benchmark = args.benchmark.lower()

    if benchmark != "all":
        bench = MySQLBenchmark(benchmark)
    else:
        bench = MySQLBenchmark("tpcc")
    
    need_stop = False
    if bench._is_mysql_ready() == False:
        bench.start_mysql_and_wait(custom_config=False, limit_resources=False)
        need_stop = True

    connection = pymysql.connect(
        host="127.0.0.1",
        port=3307,
        user="admin",
        password="password",
        db="information_schema",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            if benchmark == "all":
                pbar_dict = {}
                for bench_name in benchmarks.keys():
                    estimated_size = estimated_sizes[bench_name]
                    pbar_dict[bench_name] = tqdm(
                        total=estimated_size, unit="MB", desc=f"{bench_name}"
                    )

                try:
                    while True:
                        for bench_name, pbar in pbar_dict.items():
                            current_size = get_benchmark_size(
                                cursor, benchmarks[bench_name]
                            )
                            pbar.update(current_size - pbar.n)
                        time.sleep(5)
                except KeyboardInterrupt:
                    print("\nMonitoring interrupted by user.")
                    for pbar in pbar_dict.values():
                        pbar.close()

            elif benchmark in benchmarks:
                estimated_size = estimated_sizes[benchmark]
                with tqdm(
                    total=estimated_size, unit="MB", desc=f"{benchmark}"
                ) as pbar:
                    try:
                        while True:
                            current_size = get_benchmark_size(
                                cursor, benchmarks[benchmark]
                            )
                            pbar.update(current_size - pbar.n)
                            time.sleep(5)
                    except KeyboardInterrupt:
                        print(
                            f"\nMonitoring of benchmark '{benchmark}' was interrupted by user."
                        )
            else:
                print(f"Benchmark '{benchmark}' not found.")
    finally:
        connection.close()
        if need_stop:
            bench.gracefully_stop_container()


if __name__ == "__main__":
    main()
