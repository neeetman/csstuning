#!/bin/bash

set -euo pipefail

scriptdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
cd "$scriptdir/"

MYSQL_START_SCRIPT="./start_mysql.sh"
MYSQL_STOP_SCRIPT="./stop_mysql.sh"
BENCHBASE_IMAGE_NAME="dbms-benchmark:0.1"
BENCHBASE_CONTAINER_NAME="csstuning_benchbase"
BENCHBASE_CONFIG_DIR=$(readlink -f "../config/benchbase")

# Arguments for starting MySQL, e.g. --config-file <path>
MYSQL_START_ARGS="--config-file ../config/mysql/load_data.cnf"

workload="${1:-}"
if [[ -z "$workload" ]]; then
    echo -e "No benchmark type provided. Usage:\n$0 <benchmark_type>"
    exit 1
fi

# Run the script to start MySQL container with high efficiency
echo -e "\nStarting MySQL container..."
bash "$MYSQL_START_SCRIPT" $MYSQL_START_ARGS

wait_for_mysql() {
    echo -e "\nWaiting for MySQL to be ready..."
    local max_attempts=30
    local attempt_num=1
    while ! mysqladmin ping --host="127.0.0.1" --port=3307 --user="root" --password="password" --silent; do
        if ((attempt_num == max_attempts)); then
            echo "MySQL is not up after ${max_attempts} attempts, exiting."
            exit 1
        fi
        echo "Waiting for MySQL to be ready (attempt: $attempt_num)..."
        sleep 5
        ((attempt_num++))
    done
}

wait_for_mysql

echo -e "\nLoading database..."

docker run -t --rm \
    --name $BENCHBASE_CONTAINER_NAME \
    --network="host" \
    -v "$BENCHBASE_CONFIG_DIR:/benchbase/config" \
    $BENCHBASE_IMAGE_NAME \
    -b "$workload" -c "/benchbase/config/sample_${workload}_config.xml" --create=true --load=true

echo "Database loaded successfully."

bash "$MYSQL_STOP_SCRIPT"
