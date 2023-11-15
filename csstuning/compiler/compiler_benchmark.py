import docker
import json
import os
import subprocess
import time
from importlib import resources
from abc import ABC, abstractmethod
from docker.errors import ContainerError
from pathlib import Path

from csstuning.logger import logger
from csstuning.config import config_loader
from csstuning.compiler.compiler_config_space import GCCConfigSpace, LLVMConfigSpace


class CompilerBenchmarkBase(ABC):
    def __init__(self):
        env_conf = config_loader.get_config()

        self.config_dir = Path(env_conf.get("compiler", "compiler_config_dir"))
        self.AVALIABLE_WORKLOADS = self._load_available_workloads(
            self.config_dir / "programs.json"
        )

        self.docker_image = env_conf.get("compiler", "docker_image")
        self.initialize()

    @staticmethod
    def _load_available_workloads(file_path):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except Exception as e:
            raise FileNotFoundError(f"Unable to load the configuration file: {e}")
        
        return data["cbench"] + data["polybench"]

    @abstractmethod
    def initialize(self) -> None:
        config_path = "cssbench.compiler.config"
        with resources.open_text(config_path, "programs.json") as json_file:
            programs_dict = json.load(json_file)
            self.benchmarks = programs_dict["cbench"] + programs_dict["polybench"]

        if self.docker_mode:
            self.client = docker.from_env()
            self.container = self.client.containers.run(
                image=self.docker_image,
                command="/bin/sleep infinity",
                # command=f"/bin/bash -c 'while true; do sleep 86400; done'",
                privileged=True,
                detach=True,
                remove=True,
            )

    def run(self, benchmark, flags={}) -> dict:
        if benchmark not in self.benchmarks:
            return {"return": 1, "msg": f"Invalid {benchmark}!"}

        flagsstr = self.preprocess_flags(flags)

        if not self.docker_mode:
            return self.run_in_local(benchmark, flagsstr)
        else:
            return self.run_in_docker(benchmark, flagsstr)

    @abstractmethod
    def preprocess_flags(self, flags={}) -> str:
        pass

    @abstractmethod
    def run_in_docker(self, benchmark, flags={}) -> dict:
        pass

    @abstractmethod
    def run_in_local(self, benchmark, flags={}) -> dict:
        pass

    def __del__(self):
        if self.docker_mode and self.container is not None:
            self.container.kill()
            self.client.close()


class GCCBenchmark(CompilerBenchmarkBase):
    def initialize(self) -> None:
        super().initialize()
        config_path = "cssbench.compiler.config"
        with resources.open_text(config_path, "gcc_flags.json") as json_file:
            gcc_flags = json.load(json_file)
            # TODO: Handle param flags
            self.flags = (
                gcc_flags["O1"] + gcc_flags["O2"] + gcc_flags["O3"] + gcc_flags["Ofast"]
            )
            self.flags_to_disable = gcc_flags["O1"]
            self.param_flags = gcc_flags["Param"]

    def preprocess_flags(self, flags={}) -> str:
        # get key,value pair in flags
        flagsstr = ""
        for key, value in flags.items():
            if key in self.flags_to_disable:
                flagsstr += f"-fno-{key[1:]} "
            elif key in self.param_flags:
                flagsstr += f"-{key}={value} "
            else:
                flagsstr += f"-{key} "

        return flagsstr

    def run_in_docker(self, benchmark, flagstr="") -> dict:
        print(f'Running benchmark {benchmark} with flags "{flagstr}"')

        try:
            output = self.container.exec_run(
                f'/bin/bash /benchmark/run.sh GCC {benchmark} "{flagstr}"', stream=True
            )
        except ContainerError as e:
            return {"return": 1, "msg": f"Error running benchmark in docker: {str(e)}"}

        for line in output.output:
            print(line.decode("utf-8"), end="")

        return {}

    def run_in_local(self, benchmark, flagstr="") -> dict:
        benchmark_path = resources.path(
            "cssbench.compiler.benchmark.programs", benchmark
        )

        config_file = benchmark_path / "config.json"
        with open(config_file, "r") as f:
            config = json.load(f)

        if "build_compiler_vars" in config:
            build_compiler_vars = config["build_compiler_vars"]
            compile_vars = " ".join(
                f"-D{var}={value}" for var, value in build_compiler_vars.items()
            )

        repeat_times = config["repeat_times"]
        cmd = config["command"]

        os.chdir(benchmark_path)
        print(f"Compiling program...")
        subprocess.run(f"make clean", shell=True)
        start = time.time()
        subprocess.run(
            f"make",
            env={
                **os.environ,
                "COMPILER_TYPE": "GCC",
                "OPTFLAGS": f"-O1 {flagstr}",
                "MACORS": compile_vars,
            },
            shell=True,
        )
        compilation_time = time.time() - start
        print(f"Compilation time: {compilation_time}")

        subprocess.run(
            cmd, env={**os.environ, "BENCH_REPEAT_MAIN": str(repeat_times)}, shell=True
        )

        with open("tmp_timer.json", "r") as f:
            result = json.load(f)

        avrg_time = result["execution_time_0"] / repeat_times
        file_size = os.stat("a.out").st_size

        print(
            f"""
        Compilation time: {compilation_time}
        Total execution time: {result['execution_time_0']}
        Number of repeats: {repeat_times}
        Average execution time: {avrg_time}
        Max resident set size: {result['maxrss']}
        File size (bytes): {file_size}
        """
        )

        return {}


class LLVMBenchmark(CompilerBenchmarkBase):
    def initialize(self) -> None:
        super().initialize()
        # pkg_path = Path(pkg_resources.get_distribution("csstuning").location)

        config_path = "cssbench.compiler.config"
        with resources.open_text(config_path, "llvm_passes.json") as json_file:
            llvm_passes = json.load(json_file)
            self.flags = (
                llvm_passes["analysis_passes"] + llvm_passes["transform_passes"]
            )
            self.analysis_flags = llvm_passes["analysis_passes"]

    def preprocess_flags(self, flags={}) -> str:
        flag_list = flags.keys()
        # Reorder the flag_list so that analysis passes comes before transform passes
        # Use double pointer
        left = 0
        right = len(flag_list) - 1
        while left < right:
            if flag_list[left] in self.analysis_flags:
                left += 1
            else:
                flag_list[left], flag_list[right] = flag_list[right], flag_list[left]
                right -= 1

        flagsstr = " ".join(f"-{flag}" for flag in flag_list)

        return flagsstr

    def run_in_docker(self, benchmark, flagstr="") -> dict:
        print(f'Running benchmark {benchmark} with flags "{flagstr}"')
        output = self.container.exec_run(
            f'/bin/bash /benchmark/run.sh LLVM {benchmark} "{flagstr}"', stream=True
        )

        for line in output.output:
            print(line.decode("utf-8"), end="")

        return {}

    def run_in_local(self, benchmark, flagstr="") -> dict:
        # pkg_path = Path(pkg_resources.get_distribution("csstuning").location)
        pkg_path = resources.files("cssbench")
        benchmark_path = pkg_path / "compiler/benchmark/programs" / benchmark
        config_file = benchmark_path / "config.json"

        with open(config_file, "r") as f:
            config = json.load(f)

        if "build_compiler_vars" in config:
            build_compiler_vars = config["build_compiler_vars"]
            compile_vars = " ".join(
                f"-D{var}={value}" for var, value in build_compiler_vars.items()
            )

        repeat_times = config["repeat_times"]
        cmd = config["command"]

        os.chdir(config_file.parent)
        print(f"Compiling program...")
        subprocess.run(f"make clean", shell=True)
        start = time.time()
        subprocess.run(
            f"make",
            env={
                **os.environ,
                "COMPILER_TYPE": "LLVM",
                "OPTFLAGS": flagstr,
                "MACORS": compile_vars,
            },
            shell=True,
        )

        compilation_time = time.time() - start
        print(f"Compilation time: {compilation_time}")

        subprocess.run(
            cmd, env={**os.environ, "BENCH_REPEAT_MAIN": str(repeat_times)}, shell=True
        )

        with open("tmp_timer.json", "r") as f:
            result = json.load(f)

        avrg_time = result["execution_time_0"] / repeat_times
        file_size = os.stat("a.out").st_size

        print(
            f"""
            Compilation time: {compilation_time}
            Total execution time: {result['execution_time_0']}
            Number of repeats: {repeat_times}
            Average execution time: {avrg_time}
            Max resident set size: {result['maxrss']}
            File size (bytes): {file_size}
        """
        )

        return {}
