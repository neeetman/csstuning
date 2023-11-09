#!/bin/bash

set -eu

BENCHBASE_IMAGE_NAME="dbms-benchmark:0.1"
BENCHBASE_CONTAINER_NAME="benchbase"

benchbase_config_dir=""
workload=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
    --config-dir)
        benchbase_config_dir=$(readlink -f "$2")
        shift
        ;;
    --workload)
        workload="$2"
        shift
        ;;
    *)
        echo "Usage: $0 --config-dir <path> --workload <workload>"
        exit 1
        ;;
    esac
    shift
done

if [[ -z "$workload" ]]; then
    echo -e "No benchmark type provided."
    exit 1
fi

if [[ -z "$benchbase_config_dir" ]]; then
    echo -e "No benchbase config directory provided."
    exit 1
fi

function check_required_files {
    if [[ ! -d "$benchbase_config_dir" ]]; then
        echo "Benchbase configuration directory is missing."
        exit 1
    fi
}

function run_benchbase {
    echo "Run benchbase"
    docker run -t --rm \
        --name $BENCHBASE_CONTAINER_NAME \
        --network="host" \
        -v "$benchbase_config_dir:/benchbase/config" \
        $BENCHBASE_IMAGE_NAME \
        -im 1000 -b "$workload" -c "config/sample_${workload}_config.xml" --execute=true

}

scriptdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
cd "$scriptdir/"

# Ensure Benchbase configuration directory is present
check_required_files

# Start Benchbase container
run_benchbase
