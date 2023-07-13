import json
import os
import sys
import subprocess
import time
from compiler.benchmarks import GCCBenchmark
from pathlib import Path


# CSSTUNING_PATH = os.environ.get("CSSTUNING_PATH")
CSSTUNING_PATH = Path(__file__).resolve().parent.parent

compiler_benchs = []

compiler_flags = {
    "gcc": [],
    "llvm": []
}

def load_compiler_contants():
    global compiler_benchs
    global compiler_flags

    constants_path = CSSTUNING_PATH/"compiler/constants"
    with open(constants_path/"gcc_flags.txt", "r") as read_file:
        compiler_flags["gcc"] = [line.strip() for line in read_file if line.strip()]

    with open(constants_path/'llvm_flags.txt', 'r') as read_file:
        compiler_flags["llvm"] = [line.strip() for line in read_file if line.strip()]

    with open(constants_path/'programs.txt', 'r') as read_file:
        compiler_benchs = [line.strip() for line in read_file if line.strip()]


def run_gcc_benchmark(benchs, flags):
    gcc_bench = GCCBenchmark()
    for b in benchs:
        gcc_bench.run(b, flags)
        
    return {"return": 0}

def handle_compiler_run(type, args):
    benchs = []
    flags = ""
    for arg in args:
        if arg.startswith("benchs="):
            benchs = arg.split('=', 1)[1].split(',')
        elif arg.startswith("flags="):
            flags = arg.split('=', 1)[1]
        else:
            return {"return": 1, "msg": "Invalid argument!",
                    "callback": print_usage, "callback_args": ["compiler"]}

    if len(benchs) == 0:
        return {"return": 1, "msg": "Missing benchmarks!",
                "callback": print_usage, "callback_args": ["compiler"]}

    for b in benchs:
        if b not in compiler_benchs:
            return {"return": 1, "msg": f"Invalid benchmark {b}!"}

    flags = flags.strip('"')
    return run_gcc_benchmark(benchs, flags)

def handle_compiler_list(type, args):
    if len(args) == 0:
        return {"return": 1, "msg": "List command needs arguments!", 
                "callback": print_usage, "callback_args": ["compiler"]}
    
    target = args[0]
    if target == "benchs":
        print("Available benchmarks:")
        print("\n".join(f"  * {b}" for b in compiler_benchs))
    elif target == "flags":
        if type == "gcc":
            print("Available flags:")
            print("\n".join( f"  * {flag}" for flag in compiler_flags["gcc"]))
        elif type == "llvm":
            print("Available flags:")
            print("\n".join( f"  * {flag}" for flag in compiler_flags["llvm"]))
    else:
        return {"return": 1, "msg": "Invalid target!",
                "callback": print_usage, "callback_args": ["compiler"]}

    return {"return": 0}

def handle_compiler(type, args):
    if type not in ["gcc", "llvm"]:
        return {"return": 1, "msg": "Invalid compiler type! Must be gcc or llvm."}

    if len(args) == 0:
        return {"return": 1, "msg": "No action passed!",
                "callback": print_usage, "callback_args": ["compiler"]} 

    load_compiler_contants()

    # Get the first argument
    action = args[0]
    if action == "list":
        return handle_compiler_list(type, args[1:])
    elif action == "run":
        return handle_compiler_run(type, args[1:])
    else:
        return {"return": 1, "msg": "Invalid action!",
                "callback": print_usage}

def handle_dbsm():
    pass

def handle(args):
    # Get the arguments passed to the script 
    if len(args) == 0:
        return {"return": 1, "msg": "No arguments passed!",
                "callback": print_usage}
    
    # Get the first argument
    software_type = args[0]
    if software_type.startswith("compiler:"):
        return handle_compiler(software_type.split(':')[1], args[1:])
    elif software_type.startswith("dbsm:"):
        return handle_dbsm(software_type.split(':')[1], args[1:])
    else:
        return {"return": 1, "msg": "Invalid software type!",
                "callback": print_usage}

def print_usage(type):
    if type == "compiler":
        print("Usage: csstuning compiler:[gcc/llvm] <command> [options]")
        print(" Commands:")
        print("   * list <benchs/flags>")
        print("   * run benchs=<benchmark programs> [flags=<compiler flags>]")
        print("       <benchmark programs> - comma separated list of benchmark programs")
        print("       <compiler flags> - quoted string of compiler flags")
        print("")
        print(" Example of compiler tunning usage:") 
        print("   $ csstuning compiler:gcc list benchs")
        print("   $ csstuning compiler:gcc run benchs=cbench-automotive-bitcount \\") 
        print("         flags=\"-ftree-loop-vectorize -ftree-partial-pre\"")      
    elif type == "dbsm":
        pass
    else:
        print("Usage: csstuning <software_type> [action]")
        print(" Software types:")   
        print("   * compiler:gcc    - GNU Compiler Collection")
        print("   * compiler:llvm   - LLVM Compiler Infrastructure")
        print("   * dbsm")
        print(" Example of compiler tunning usage:")
        print("   $ csstuning compiler:gcc run benchs=cbench-automotive-bitcount flags=\"ftree-loop-vectorize,ftree-partial-pre\"")
        print("   $ csstuning compiler:gcc list benchs")


def cli():
    # if CSSTUNING_PATH exists, then it should be a directory
    if CSSTUNING_PATH is None or not CSSTUNING_PATH.exists():
        print("CSSTUNING_PATH is not set!")
        exit(1)
    if not os.path.exists(CSSTUNING_PATH):
        print(f"Can't find benchmark path {CSSTUNING_PATH}!")
        exit(1)

    # Get the arguments passed to the script
    r = handle(sys.argv[1:])

    if r is None or "return" not in r:
        raise Exception(
            "Should always return key \'return\'!")

    if r["return"] != 0:
        # print in color red
        print(f"Error: {r['msg']}\n", file=sys.stderr)
        if "callback" in r:
            if "callback_args" not in r:
                r["callback_args"] = [""]
            r["callback"](*r["callback_args"])

    exit(int(r["return"]))

if __name__ == "__main__":
    cli()
