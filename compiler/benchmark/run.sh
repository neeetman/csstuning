#!/bin/bash
# This script is used to run the compiler benchmark in a docker container.

set -e

# Get arugments.
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <benchmark name> <flags>"
    exit 1
fi

benchmark="$1"

# The directory of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
BENCHMARK_DIR="$DIR/programs/$benchmark"

# Get compiler vars from config.json
config=$(cat "$BENCHMARK_DIR/config.json")
if [[ $(jq -r '.build_compiler_vars' <<< "$config") != "null" ]]; then
    build_compiler_vars=$(jq -r '.build_compiler_vars | to_entries[] | "-D\(.key)=\(.value)"' <<< "$config")
    cflags="$build_compiler_vars $2"
else
    cflags="$2"
fi

repeat_times=$(jq -r '.repeat_times' <<< "$config")
command=$(jq -r '.command' <<< "$config")

cd $BENCHMARK_DIR
make clean
/usr/bin/time -f "%e" -o tmp_compilation_time make CFLAGS_ADD="$cflags"
compilation_time=$(cat tmp_compilation_time)

export BENCH_REPEAT_MAIN=$repeat_times && eval "$command"

result=$(cat tmp_timer.json)
total_time=$(jq -r '.execution_time_0' <<< "$result")
avrg_time=$(echo "scale=20; $total_time / $repeat_times" | bc)

maxrss=$(jq -r '.maxrss' <<< "$result")

echo "Compilation time: $compilation_time"
echo "Total execution time: $total_time"
echo "Number of repeats: $repeat_times"
echo "Average execution time: $avrg_time"
echo "Max resident set size (KB): $maxrss"