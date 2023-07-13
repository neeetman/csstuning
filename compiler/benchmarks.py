import docker
import json
import os
import subprocess
import time
from docker.errors import ContainerError
from pathlib import Path


class GCCBenchmark(object):
    def __init__(self):
        self.docker_mode = True
        self.flags = []
        self.benchmarks = []
        self.initialize()

    def initialize(self):
        current_dir = Path(__file__).resolve().parent
        
        with open(current_dir/"constants/gcc_flags.txt", "r") as read_file:
            self.flags = [line.strip() for line in read_file if line.strip()]

        with open(current_dir/"constants/programs.txt", "r") as read_file:
            self.benchmarks = [line.strip() for line in read_file if line.strip()]

        if self.docker_mode:
            self.client = docker.from_env()
            self.container = self.client.containers.run(
                image="compiler-benchmark:0.1", # Should be set through environment variable
                command=f"/bin/bash -c 'while true; do sleep 86400; done'",
                detach=True,
                remove=True
            )

    def run(self, benchmark, flags="") -> dict:
        # Still need to modify
        if benchmark not in self.benchmarks:
            return {"return": 1, "msg": f"Invalid {benchmark}!"}
        
        if not self.docker_mode:
            return self.run_in_local(benchmark, flags)
        else:
            return self.run_in_docker(benchmark, flags)
        
    def run_in_docker(self, benchmark, flags="") -> dict:
        # self.container = self.client.containers.run(
        #         image="compiler-benchmark:0.1", # Should be set through environment variable
        #         command=f"/bin/bash /benchmark/run.sh {benchmark} \"{flags}\""
        # )
        output = self.container.exec_run(f"/bin/bash /benchmark/run.sh {benchmark} \"{flags}\"", stream=True)
        for line in output.output:
            print(line.decode('utf-8').strip('\n'))

        return {}

    @staticmethod
    def run_in_local(benchmark, flags="") -> dict:
        current_dir = Path(__file__).resolve().parent
        config_file = current_dir / "benchmark/programs"/ benchmark / "config.json"

        with open(config_file, 'r') as f:
            config = json.load(f)

        if "build_compiler_vars" in config:
            build_compiler_vars = config["build_compiler_vars"]
            compile_vars = " ".join(f"-D{var}={value}" for var, value in build_compiler_vars.items())
            flags += " " + compile_vars
            
        repeat_times = config["repeat_times"]
        cmd = config["command"]

        os.chdir(config_file.parent)
        print(f"Compiling program...")
        subprocess.run(f"make clean", shell=True)
        start = time.time()
        subprocess.run(f"make", env={**os.environ, "CFLAGS_ADD": flags}, shell=True)
        compilation_time = time.time() - start
        print(f"Compilation time: {compilation_time}")

        subprocess.run(cmd, env={**os.environ, "BENCH_REPEAT_MAIN": str(repeat_times)}, shell=True)

        with open("tmp_timer.json", 'r') as f:
            result = json.load(f)
            avrg = result["execution_time_0"] / repeat_times
        
        print(f"""
        Compilation time: {compilation_time}
        Total execution time: {result['execution_time_0']}
        Average execution time: {avrg}
        Number of repeats: {repeat_times}
        Max resident set size: {result['maxrss']}
        """)

        return {}

    def __del__(self):
        if self.docker_mode:
            self.container.kill()
            self.client.close()