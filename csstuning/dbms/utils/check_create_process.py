import time
import pymysql
import argparse
import threading
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
    "tpcc": 20156.17,
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


def monitor_benchmark(cursor, benchmark, stop_event):
    """Monitor a single benchmark."""
    tables = benchmarks[benchmark]
    estimated_size = estimated_sizes[benchmark]
    with tqdm(total=estimated_size, unit='MB', desc=f"Benchmark: {benchmark}") as pbar:
        while not stop_event.is_set():
            current_size = get_benchmark_size(cursor, tables)
            pbar.update(current_size - pbar.n)
            time.sleep(5)



def main():
    parser = argparse.ArgumentParser(description="Monitor benchmark loading progress.")
    parser.add_argument("benchmark", help="Name of the benchmark to monitor")
    args = parser.parse_args()
    benchmark = args.benchmark.lower()

    bench = MySQLBenchmark(benchmark)
    bench.start_mysql_and_wait()

    connection = pymysql.connect(
        host="127.0.0.1",
        port=3307,
        user="admin",
        password="password",
        db="information_schema",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    threads = []
    stop_event = threading.Event()

    try:
        with connection.cursor() as cursor:
            if benchmark == "all":
                for bench_name in benchmarks.keys():
                    thread = threading.Thread(target=monitor_benchmark, args=(cursor, bench_name, stop_event))
                    threads.append(thread)
                    thread.start()
                for thread in threads:
                    thread.join()
            elif benchmark in benchmarks:
                monitor_benchmark(cursor, benchmark, stop_event)
            else:
                print(f"Benchmark '{benchmark}' not found.")
    except KeyboardInterrupt:
        stop_event.set()
        for thread in threads:
            thread.join()
        print("\nMonitoring interrupted by user.")
    finally:
        connection.close()
        bench.gracefully_stop_container()


if __name__ == "__main__":
    main()
