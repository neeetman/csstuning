#!/bin/bash
# This script is used to run the compiler benchmark in a docker container.

set -e

# Get arugments.
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <LLVM or GCC> <benchmark name> <flags>"
    exit 1
fi

compiler="$1"
benchmark="$2"

# The directory of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
BENCHMARK_DIR="$DIR/programs/$benchmark"

# Get compiler vars from config.json
config=$(cat "$BENCHMARK_DIR/config.json")
if [[ $(jq -r '.build_compiler_vars' <<< "$config") != "null" ]]; then
    build_compiler_vars=$(jq -r '.build_compiler_vars | to_entries[] | "-D\(.key)=\(.value)"' <<< "$config" | tr '\n' ' ')
else
    build_compiler_vars=""
fi

if [ "$compiler" = "GCC" ]; then
    # optflags=$(jq -r '.O1[]' "$DIR/gcc_flags.json" | sed 's/^f/-fno-/g' | tr '\n' ' ') 
    optflags="-O1 $optflags $3"
else
    optflags=$3
fi

repeat_times=$(jq -r '.repeat_times' <<< "$config")
command=$(jq -r '.command' <<< "$config")

cd $BENCHMARK_DIR
make clean
echo "make COMPILER_TYPE=$compiler MACROS=\"$build_compiler_vars\" OPTFLAGS=\"$optflags\""
/usr/bin/time -f "%e" -o tmp_compilation_time make \
    COMPILER_TYPE=$compiler \
    MACROS="$build_compiler_vars" \
    OPTFLAGS="$optflags" 
compilation_time=$(cat tmp_compilation_time)

export BENCH_REPEAT_MAIN=$repeat_times && eval "$command >tmp_outpt.tmp"

# cat tmp_result.json
result=$(cat tmp_result.json)
total_time=$(jq -r '.execution_time' <<< "$result")
avrg_time=$(echo "scale=20; $total_time / $repeat_times" | bc)
avrg_time=$(printf "%.4e" $avrg_time)

maxrss=$(jq -r '.maxrss' <<< "$result")

file_size=$(stat -c%s "$BENCHMARK_DIR/a.out")

echo "++++++++++++++++++++++++++++++++++++++++"
echo "Compilation time (s): $compilation_time"
echo "File size (bytes): $file_size"
echo "Total execution time (s): $total_time"
echo "Number of repeats: $repeat_times"
echo "Average execution time (s): $avrg_time"
# echo "Max resident set size (KB): $maxrss"

jq -r 'to_entries|map(select(.key|startswith("PAPI"))|"\(.key): \(.value|tostring)")|.[]' tmp_result.json
