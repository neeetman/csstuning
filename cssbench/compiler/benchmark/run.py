#!/usr/bin/env python3
"""
A script to run compiler benchmarks. Usage:
    
        python3 run.py [-v|--verbose] <compiler> <benchmark> <flags>

execution_time: The total time taken to execute the benchmarked code, measured in seconds.
avrg_exec_time: Average execution time, measured in seconds.
compilation_time: The time taken to compile the code, measured in seconds.
file_size: The size of the compiled executable file, measured in bytes.
maxrss: Stands for "maximum resident set size", measured in kilobytes (KB).

PAPI_TOT_CYC: The total number of CPU cycles consumed during the execution.
PAPI_TOT_INS: The total number of instructions the CPU executed.
PAPI_BR_MSP: The number of times the CPU incorrectly predicted the direction of a branch.
PAPI_BR_PRC: The number of times the CPU correctly predicted the direction of a branch.
PAPI_BR_CN: The number of conditional branch instructions.
PAPI_MEM_WCY: The number of cycles spent waiting for memory accesses.
"""

import argparse
import os
import json
import subprocess
import time
from pathlib import Path
from contextlib import contextmanager


def execute_command(cmd):
    """
    Execute a shell command and return its output.
    """
    return subprocess.check_output(cmd, shell=True).decode("utf-8").strip()


def list_benchmarks():
    """
    List all subdirectories in the ./programs directory, which are the benchmarks.
    """
    script_dir = Path(__file__).resolve().parent
    benchmark_dir = script_dir / "programs"
    return sorted(dir.name for dir in benchmark_dir.iterdir() if dir.is_dir())


def parse_arguments():
    """
    Parse command line arguments for the script.
    """
    parser = argparse.ArgumentParser(
        description="Run compiler benchmarks in a docker container."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument("compiler", choices=["LLVM", "GCC"], help="Compiler to use")
    parser.add_argument(
        "benchmark", choices=["all"] + list_benchmarks(), help="Benchmark name"
    )
    parser.add_argument("--flags", default=[], help="Compiler flags (optional)")
    return parser.parse_args()


def compile_and_run_benchmark(benchmark, compiler, flags, verbose=False):
    """
    Compile and run the specified benchmark, and gather performance data.
    """
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"Running {benchmark} with {compiler} and flags {flags}")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    script_dir = Path(__file__).resolve().parent
    benchmark_dir = script_dir / "programs" / benchmark

    try:
        with open(benchmark_dir / "config.json", "r") as f:
            config = json.load(f)

        build_compiler_vars = config.get("build_compiler_vars", {})
        compiler_vars_str = " ".join(
            f"-D{k}={v}" for k, v in build_compiler_vars.items()
        )

        optflags = "-O1 " + flags if compiler == "GCC" else flags
        repeat_times = config["repeat_times"]
        command = config["command"]

        with change_directory(benchmark_dir):
            subprocess.run(["make", "clean"], stdout=subprocess.DEVNULL, check=True)

            start_time = time.time()
            subprocess.run(
                [
                    "make",
                    f"COMPILER_TYPE={compiler}",
                    f"MACROS={compiler_vars_str}",
                    f"OPTFLAGS={optflags}",
                ],
                stdout=None if verbose else subprocess.DEVNULL,
                stderr=None if verbose else subprocess.DEVNULL,
                check=True,
            )
            compilation_time = time.time() - start_time

            os.environ["BENCH_REPEAT_MAIN"] = str(repeat_times)
            subprocess.run(
                [command],
                shell=True,
                stdout=None if verbose else subprocess.DEVNULL,
                stderr=None if verbose else subprocess.DEVNULL,
                check=True,
            )

            with open("tmp_result.json") as f:
                result = json.load(f)

            result["compilation_time"] = compilation_time
            result["file_size"] = os.path.getsize(os.path.join(benchmark_dir, "a.out"))
            result["avrg_exec_time"] = result["execution_time"] / repeat_times

            print(result)

            return result

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


@contextmanager
def change_directory(path):
    original_path = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_path)


def get_perf_event_paranoid():
    with open("/proc/sys/kernel/perf_event_paranoid", "r") as f:
        return int(f.read().strip())


def set_perf_event_paranoid(value):
    with open("/proc/sys/kernel/perf_event_paranoid", "w") as f:
        f.write(str(value))


def main():
    args = parse_arguments()

    benchmarks = list_benchmarks()

    result_dict = {}
    original_paranoid = get_perf_event_paranoid()
    try:
        set_perf_event_paranoid(0)
        if args.benchmark == "all":
            for benchmark in benchmarks:
                result = compile_and_run_benchmark(
                    benchmark, args.compiler, args.flags, args.verbose
                )
                result_dict[benchmark] = result
        elif args.benchmark in benchmarks:
            result = compile_and_run_benchmark(
                args.benchmark, args.compiler, args.flags, args.verbose
            )
            result_dict[args.benchmark] = result
        else:
            print(f"Error: Invalid benchmark {args.benchmark}")

    finally:
        set_perf_event_paranoid(original_paranoid)

    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(exist_ok=True)
    results_file = results_dir / f"{args.compiler.lower()}_results.json"
    with open(results_file, "w") as f:
        json.dump(result_dict, f, indent=4)


if __name__ == "__main__":
    main()
