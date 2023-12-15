import docker
import json
import os
import subprocess
import time
from importlib import resources
from docker.errors import ContainerError
from pathlib import Path

from csstuning.logger import logger
from csstuning.config import config_loader
from csstuning.compiler.compiler_config_space import GCCConfigSpace, LLVMConfigSpace


class CompilerBenchmarkBase:
    AVAILABLE_WORKLOADS = [
        "cbench-automotive-bitcount",
        "cbench-security-rijndael",
        "cbench-consumer-tiff2rgba",
        "cbench-telecom-adpcm-d",
        "cbench-consumer-tiff2bw",
        "cbench-automotive-susan-e",
        "cbench-security-sha",
        "cbench-network-patricia",
        "cbench-automotive-qsort1",
        "cbench-bzip2",
        "cbench-telecom-adpcm-c",
        "cbench-automotive-susan-s",
        "cbench-consumer-jpeg-d",
        "cbench-network-dijkstra",
        "cbench-consumer-mad",
        "cbench-automotive-susan-c",
        "cbench-telecom-crc32",
        "cbench-office-stringsearch2",
        "cbench-consumer-jpeg-c",
        "cbench-security-pgp",
        "cbench-consumer-tiff2dither",
        "cbench-telecom-gsm",
        "polybench-symm",
        "polybench-2mm",
        "polybench-3mm",
        "polybench-doitgen",
        "polybench-jacobi-2d-imper",
        "polybench-gramschmidt",
        "polybench-gesummv",
        "polybench-cholesky",
        "polybench-gemver",
        "polybench-trmm",
        "polybench-mvt",
        "polybench-trisolv",
        "polybench-dynprog",
        "polybench-gemm",
        "polybench-jacobi-1d-imper",
        "polybench-durbin",
        "polybench-seidel-2d",
        "polybench-adi",
        "polybench-bicg",
        "polybench-atax",
        "polybench-medley-floyd-warshall",
        "polybench-fdtd-apml",
        "polybench-syr2k",
        "polybench-lu",
        "polybench-medley-reg-detect",
        "polybench-ludcmp",
        "polybench-fdtd-2d",
        "polybench-syrk",
    ]

    def __init__(self, workload):
        if workload not in self.AVAILABLE_WORKLOADS:
            logger.error(
                f"Workload '{workload}' is not supported. Supported workloads: {self.AVAILABLE_WORKLOADS}"
            )
            raise ValueError(f"Workload '{workload}' is not supported.")

        env_conf = config_loader.get_config()

        self.config_dir = Path(env_conf.get("compiler", "compiler_config_dir"))
        # self.AVALIABLE_WORKLOADS = self._load_available_workloads(
        #     self.config_dir / "programs.json"
        # )

        self.docker_image = env_conf.get("compiler", "compiler_image")
        self.container_name = env_conf.get("compiler", "container_name")
        self.results_dir = Path(env_conf.get("compiler", "compiler_results_dir"))

        self.debug_mode = env_conf.getboolean("general", "debug_mode")

        self.workload = workload
        self.docker_client = docker.from_env()

    @staticmethod
    def _load_available_workloads(file_path):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except Exception as e:
            raise FileNotFoundError(f"Unable to load the configuration file: {e}")

        return data["cbench"] + data["polybench"]

    def _remove_existing_container(self, container_name):
        try:
            container = self.docker_client.containers.get(container_name)
            if container.status == 'running':
                container.stop()
            container.remove(force=True)
        except docker.errors.NotFound:
            pass
        except docker.errors.DockerException as e:
            logger.error(f"Error removing container {container_name}: {e}")
            raise e

        timeout = 30
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.docker_client.containers.get(container_name)
                time.sleep(1)
            except docker.errors.NotFound:
                return
        logger.error(f"Timeout: Container {container_name} could not be removed in time.")
        raise RuntimeError(f"Timeout: Failed to remove container {container_name}.")
    
    def __del__(self):
        if hasattr(self, "docker_client"):
            self.docker_client.close()


class GCCBenchmark(CompilerBenchmarkBase):
    def __init__(self, workload):
        super().__init__(workload)
        self.config_space = GCCConfigSpace()

    def execute_benchmark(self, flags_str):
        self._remove_existing_container(self.container_name)

        # Map papi_events.txt and results directory to the container
        papi_file = self.config_dir / "papi_events.txt"
        volumes_mapping = {
            papi_file: {
                "bind": "/benchmark/utilities/papi_events.txt",
                "mode": "rw",
            },
            self.results_dir: {
                "bind": "/benchmark/results",
                "mode": "rw",
            },
        }

        try:
            container = self.docker_client.containers.run(
                self.docker_image,
                name=self.container_name,
                volumes=volumes_mapping,
                command=[
                    # "-v",
                    "GCC",
                    self.workload,
                    f"--flags={flags_str}",
                ],
                privileged=True,
                remove=True,
                detach=True,
                stdout=True,
                stderr=True,
            )

            if self.debug_mode:
                for line in container.logs(stream=True, follow=True):
                    logger.info(line.strip().decode("utf-8"))
            else:
                container.wait()

        except docker.errors.DockerException as e:
            logger.error(f"Error running BenchBase container: {e}")
            raise RuntimeError("Failed to run BenchBase.")

    def run(self, flags: dict) -> dict:
        self.config_space.set_current_config(flags)

        flags_str = self.config_space.generate_flags_str()

        try:
            self.execute_benchmark(flags_str)
            return self.parse_results()
        except Exception as e:
            logger.error(f"Error running benchmark: {e}")
            raise

    def run_with_random(self) -> dict:
        self.config_space.set_random_config()
        flags_str = self.config_space.generate_flags_str()

        try:
            self.execute_benchmark(flags_str)
            return self.parse_results()
        except Exception as e:
            logger.error(f"Error running benchmark: {e}")
            raise

    def parse_results(self) -> dict:
        try:
            with open(self.results_dir / "gcc_results.json", "r") as f:
                result = json.load(f)
        except Exception as e:
            logger.error(f"Error parsing benchmark results: {e}")
            raise RuntimeError("Failed to parse benchmark results.")

        result = result.get(self.workload, {})
        return result

    def get_config_space(self) -> dict:
        return self.config_space.get_all_details()
    
    # Deprecated
    def _run_in_local(self, benchmark, flagstr="") -> dict:
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
    def __init__(self, workload):
        super().__init__(workload)
        self.config_space = LLVMConfigSpace()

    def execute_benchmark(self, flags_str):
        self._remove_existing_container(self.container_name)

        # Map papi_events.txt and results directory to the container
        papi_file = self.config_dir / "papi_events.txt"
        volumes_mapping = {
            papi_file: {
                "bind": "/benchmark/utilities/papi_events.txt",
                "mode": "rw",
            },
            self.results_dir: {
                "bind": "/benchmark/results",
                "mode": "rw",
            },
        }

        try:
            container = self.docker_client.containers.run(
                self.docker_image,
                name=self.container_name,
                volumes=volumes_mapping,
                command=[
                    # "-v",
                    "LLVM",
                    self.workload,
                    f"--flags={flags_str}",
                ],
                privileged=True,
                remove=True,
                detach=True,
                stdout=True,
                stderr=True,
            )

            if self.debug_mode:
                for line in container.logs(stream=True, follow=True):
                    logger.info(line.strip().decode("utf-8"))
            else:
                container.wait()

        except docker.errors.DockerException as e:
            logger.error(f"Error running BenchBase container: {e}")
            raise RuntimeError("Failed to run BenchBase.")

    def run(self, flags: dict) -> dict:
        self.config_space.set_current_config(flags)
        flags_str = self.config_space.generate_flags_str()

        try:
            self.execute_benchmark(flags_str)
            return self.parse_results()
        except Exception as e:
            logger.error(f"Error running benchmark: {e}")
            raise

    def run_with_random(self) -> dict:
        self.config_space.set_random_config()
        flags_str = self.config_space.generate_flags_str()

        try:
            self.execute_benchmark(flags_str)
            return self.parse_results()
        except Exception as e:
            logger.error(f"Error running benchmark: {e}")
            raise

    def parse_results(self) -> dict:
        try:
            with open(self.results_dir / "llvm_results.json", "r") as f:
                result = json.load(f)
        except Exception as e:
            logger.error(f"Error parsing benchmark results: {e}")
            raise RuntimeError("Failed to parse benchmark results.")

        result = result.get(self.workload, {})
        return result

    def get_config_space(self) -> dict:
        return self.config_space.get_all_details()
    
    # Deprecated
    def _run_in_local(self, benchmark, flagstr="") -> dict:
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
