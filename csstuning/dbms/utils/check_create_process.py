import pymysql
import time
import argparse

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
        "v_votes_by_constestant_number_state",
        "v_votes_by_phone_number",
        "area_code_state",
    ],
    "tatp": ["subscriber", "special_facility", "access_info", "call_forwarding"],
}

estimated_sizes = {
    "tpcc": 17.8,
    "twitter": 7.9,
    "smallbank": 2.4,
    "sibench": 0.5,
    "voter": 0.06,
    "tatp": 6.3,
}


def get_benchmark_size(cursor, benchmark, tables):
    total_size = 0
    for table in tables:
        query = f"""
            SELECT 
                ROUND(SUM(data_length + index_length) / 1024 / 1024 / 1024, 2) AS 'size_in_gb' 
            FROM 
                tables 
            WHERE 
                table_schema = '{benchmark}' AND
                table_name = '{table}';
        """
        cursor.execute(query)
        result = cursor.fetchone()
        total_size += result["size_in_gb"] if result else 0
    return total_size


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
            while True:
                if benchmark in benchmarks:
                    tables = benchmarks[benchmark]
                    current_size = get_benchmark_size(cursor, benchmark, tables)
                    estimated_size = estimated_sizes[benchmark.upper()]
                    print(
                        f"Benchmark: {benchmark}, Current Size: {current_size} GB, Estimated Size: {estimated_size} GB"
                    )
                else:
                    print(f"Benchmark '{benchmark}' not found.")
                time.sleep(10)
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor benchmark loading progress.")
    parser.add_argument("benchmark", help="Name of the benchmark to monitor")
    args = parser.parse_args()
    main(args.benchmark.lower())
