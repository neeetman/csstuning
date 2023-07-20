import argparse
import os
import json
import subprocess
from decimal import Decimal
import time


def shell(cmd):
    return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()


def get_benchmarks_list():
    # The directory of this script.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    benchmark_dir = os.path.join(dir_path, 'programs')

    # Get all subdirectories in the ./programs directory.
    benchmarks = [name for name in os.listdir(benchmark_dir)
                  if os.path.isdir(os.path.join(benchmark_dir, name))]
    benchmarks.sort()
    return benchmarks


def get_args():
    benchmarks = ['all'] + get_benchmarks_list()

    parser = argparse.ArgumentParser(
        description='Run the compiler benchmark in a docker container.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose')
    parser.add_argument('compiler', choices=[
                        'LLVM', 'GCC'], help='Compiler to use.')
    parser.add_argument('benchmark', choices=benchmarks,
                        help='Name of the benchmark.')
    parser.add_argument('flags', help='Flags to pass to the compiler.')
    return parser.parse_args()


def run_benchmark(benchmark, compiler, flags, verbose=False) -> dict:
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(f'Running {benchmark} with {compiler} and flags {flags}')
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    # The directory of this script.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    benchmark_dir = os.path.join(dir_path, 'programs', benchmark)

    # Get compiler vars from config.json
    with open(os.path.join(benchmark_dir, 'config.json')) as f:
        config = json.load(f)
        if 'build_compiler_vars' in config:
            build_compiler_vars = config['build_compiler_vars']
        else:
            build_compiler_vars = {}
        build_compiler_vars = ' '.join(
            f'-D{k}={v}' for k, v in build_compiler_vars.items())

    if compiler == 'GCC':
        optflags = '-O1 ' + flags
    else:
        optflags = flags

    repeat_times = config['repeat_times']
    command = config['command']

    old_dir = os.getcwd()
    os.chdir(benchmark_dir)
    print(
        f'make clean && make COMPILER_TYPE={compiler} MACROS="{build_compiler_vars}" OPTFLAGS="{optflags}"')
    subprocess.run(['make', 'clean'], stdout=subprocess.DEVNULL)
    try:
        start_time = time.time()
        if verbose:
            subprocess.run(
                ["make", f"COMPILER_TYPE={compiler}",
                    f"MACROS={build_compiler_vars}", f"OPTFLAGS={optflags}"],
            )
        else:
            subprocess.run(
                ["make", f"COMPILER_TYPE={compiler}",
                    f"MACROS={build_compiler_vars}", f"OPTFLAGS={optflags}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        compilation_time = time.time() - start_time
        print(f'Compilation time: {compilation_time}')
    except subprocess.CalledProcessError:
        print("Compilation failed")
        os.chdir(old_dir)
        return {'return': 1, 'msg': 'Compilation failed'}

    os.environ['BENCH_REPEAT_MAIN'] = str(repeat_times)
    try:
        print(f'Running {command}')
        if verbose:
            subprocess.run([command], shell=True)
        else:
            subprocess.run([command], shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("Execution failed")
        os.chdir(old_dir)
        return {'return': 1, 'msg': 'Execution failed'}

    result = {'repeat_times': repeat_times}
    with open('tmp_result.json') as f:
        resfile = json.load(f)
        total_time = float(resfile['execution_time'])
        avrg_time = total_time / repeat_times

        result['compilation_time'] = compilation_time
        result['file_size'] = os.path.getsize(
            os.path.join(benchmark_dir, 'a.out'))
        result['total_run_time'] = total_time
        result['avrg_run_time'] = avrg_time

        for k, v in resfile.items():
            if k.startswith('PAPI'):
                result[k] = v

    # maxrss = result.get('maxrss')
    os.chdir(old_dir)
    return {'return': 0, 'result': result, 'msg': 'Success'}


def print_result(result):
    if result['return'] != 0:
        print(f'Error: {result["msg"]}')
    else:
        print(f'Success: {result["msg"]}')
        print(result['result'])
        print()

def main():
    args = get_args()

    benchmarks = get_benchmarks_list()
    if args.benchmark == 'all':
        for benchmark in benchmarks:
            result = run_benchmark(
                benchmark, args.compiler, args.flags, args.verbose)
            print_result(result)

    elif args.benchmark in benchmarks:
        result = run_benchmark(
            args.benchmark, args.compiler, args.flags, args.verbose)
        print_result(result)

    else:
        print(f'Error: Invalid benchmark {args.benchmark}')


if __name__ == '__main__':
    main()
