import sys
import pymysql
import time
import argparse
from tqdm import tqdm

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
    "tpcc": 17.8 * 1024,
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

def main(benchmark):
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
            if benchmark in benchmarks:
                tables = benchmarks[benchmark]
                estimated_size = estimated_sizes[benchmark]
                with tqdm(total=estimated_size, unit='MB', desc=f"Benchmark: {benchmark}") as pbar:
                    while True:
                        current_size = get_benchmark_size(cursor, tables)
                        pbar.update(current_size - pbar.n)
                        time.sleep(5)
            else:
                print(f"Benchmark '{benchmark}' not found.")
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor benchmark loading progress.")
    parser.add_argument("benchmark", help="Name of the benchmark to monitor")
    args = parser.parse_args()
    main(args.benchmark.lower())