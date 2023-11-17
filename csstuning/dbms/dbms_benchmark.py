import docker
import docker.errors
import os
import time
import pymysql
import shutil
import json
from pathlib import Path
from importlib import resources

from csstuning.logger import logger
from csstuning.config import config_loader
from csstuning.dbms.dbms_config_space import MySQLConfigSpace


class MySQLBenchmark:
    AVAILABLE_WORKLOADS = [
        "tpcc",
        "twitter",
        "smallbank",
        "sibench",
        "voter",
        "seats",
        "tatp",
    ]

    def __init__(self, workload):
        if workload not in self.AVAILABLE_WORKLOADS:
            logger.error(
                f"Workload '{workload}' is not supported. Supported workloads: {self.AVAILABLE_WORKLOADS}"
            )
            raise ValueError(f"Workload '{workload}' is not supported.")

        env_config = config_loader.get_config()

        # Update to use configuration values from config_loader
        self.debug_mode = env_config.getboolean("general", "debug_mode")
        self.mysql_image = env_config.get("database", "mysql_image")
        self.mysql_container_name = env_config.get("database", "mysql_container_name")
        self.vcpus = env_config.getfloat("database", "mysql_vcpus")
        self.mem = env_config.getfloat("database", "mysql_mem")
        self.mysql_config_file = Path(env_config.get("database", "mysql_config_file"))
        self.mysql_data_dir = Path(env_config.get("database", "mysql_data_dir"))

        self.benchbase_image = env_config.get("database", "benchbase_image")
        self.benchbase_container_name = env_config.get(
            "database", "benchbase_container_name"
        )
        self.benchbase_config_dir = Path(
            env_config.get("database", "benchbase_config_dir")
        )
        self.benchbase_results_dir = Path(
            env_config.get("database", "benchbase_results_dir")
        )

        self.workload = workload
        self.config_space = MySQLConfigSpace()
        self.docker_client = docker.from_env()

        # self.initialize_benchmark_data_dir()

    # Deprecated. Directories are now created in setup.py
    def initialize_benchmark_data_dir(self):
        pass
        # self.mysql_data_dir.mkdir(parents=True, exist_ok=True)
        # self.benchbase_config_dir.mkdir(parents=True, exist_ok=True)
        # self.benchbase_results_dir.mkdir(parents=True, exist_ok=True)

        # if not any(self.mysql_data_dir.iterdir()):
        #     logger.info("Initializing MySQL data directory...")
        #     self.start_mysql_and_wait(custom_config=False, limit_resources=False)

        # # Check if the directory is empty and requires initialization
        # if not any(self.benchbase_config_dir.iterdir()):
        #     with resources.path(
        #         "cssbench.dbms.config", "benchbase"
        #     ) as pkg_benchbase_path:
        #         for item in pkg_benchbase_path.iterdir():
        #             if item.is_dir():
        #                 shutil.copytree(item, self.benchbase_config_dir / item.name)
        #             else:
        #                 shutil.copy(item, self.benchbase_config_dir / item.name)

        #     logger.info(
        #         f"Initialized benchbase data directory at {self.benchbase_config_dir}"
        #     )

    def _remove_existing_container(self, container_name):
        try:
            container = self.docker_client.containers.get(container_name)
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass
        except docker.errors.DockerException as e:
            logger.error(f"Error removing container {container_name}: {e}")

        # Some error occurred after cleanup some files. Need to fix this.
        # self._cleanup_mysql_data_dir()

    def _cleanup_mysql_data_dir(self):
        files_to_delete = ["ib_logfile"]

        if self.mysql_data_dir.exists() and self.mysql_data_dir.is_dir():
            try:
                for item in self.mysql_data_dir.iterdir():
                    if item.is_file() and any(
                        item.name.startswith(pattern) for pattern in files_to_delete
                    ):
                        item.unlink()  # Deletes the file

                logger.info(
                    f"Cleaned up specified files in MySQL data directory at {self.mysql_data_dir}"
                )
            except Exception as e:
                logger.error(f"Error cleaning up MySQL data directory: {e}")

    def _gracefully_stop_mysql_container(self, container_name):
        try:
            container = self.docker_client.containers.get(container_name)

            if container.status != "running":
                container.remove(force=True)

            logger.info(f"Sending shutdown command to MySQL container...")

            shutdown_command = "mysqladmin shutdown -u root -ppassword"
            container.exec_run(shutdown_command)

            logger.info("Waiting for MySQL container to stop...")
            timeout = 60
            start_time = time.time()
            while time.time() - start_time < timeout:
                container.reload()
                if container.status != "running":
                    break
                time.sleep(1)
            else:
                logger.warning(
                    f"Timeout waiting for MySQL container {container_name} to stop."
                )

            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass
        except docker.errors.DockerException as e:
            logger.error(
                f"Error gracefully stopping MySQL container {container_name}: {e}"
            )
            self._remove_existing_container(container_name)

    def start_mysql(self, custom_config=True, limit_resources=True):
        self._gracefully_stop_mysql_container(self.mysql_container_name)

        volumes = {
            self.mysql_data_dir: {"bind": "/var/lib/mysql", "mode": "rw"},
        }
        if custom_config and self.mysql_config_file.is_file():
            volumes[str(self.mysql_config_file)] = {
                "bind": "/etc/mysql/conf.d/custom.cnf",
                "mode": "rw",
            }

        environment = {
            "MYSQL_ROOT_PASSWORD": "password",
            "MYSQL_USER": "admin",
            "MYSQL_PASSWORD": "password",
            "MYSQL_DATABASE": "benchbase",
        }
        ports = {"3306/tcp": 3307}

        logger.info("Starting MySQL container...")
        if limit_resources:
            self.mysql_container = self.docker_client.containers.run(
                self.mysql_image,
                name=self.mysql_container_name,
                volumes=volumes,
                environment=environment,
                ports=ports,
                user=f"{os.getuid()}:{os.getgid()}",
                cpu_quota=int(self.vcpus * 100000),
                mem_limit=f"{self.mem}g",
                detach=True,
            )
        else:
            self.mysql_container = self.docker_client.containers.run(
                self.mysql_image,
                name=self.mysql_container_name,
                volumes=volumes,
                environment=environment,
                ports=ports,
                user=f"{os.getuid()}:{os.getgid()}",
                detach=True,
            )

    def start_mysql_and_wait(
        self, custom_config=True, limit_resources=True, timeout=None
    ) -> bool:
        self.start_mysql(custom_config, limit_resources)
        return self._wait_for_mysql_ready(timeout)

    def create_database(self):
        env_conf = config_loader.get_config()
        conf_dir = Path(env_conf.get("database", "dbms_config_dir"))
        load_conf_file = conf_dir / "load_data.cnf"

        try:
            shutil.copyfile(load_conf_file, self.mysql_config_file)
        except IOError as e:
            logger.error(f"Failed to copy MySQL config file for loading databse: {e}")
            raise

        if not self.start_mysql_and_wait(limit_resources=False, timeout=600):
            raise RuntimeError("Failed to start MySQL container.")

        logger.info(f"Loading database for {self.workload}...")

        volumes_mapping = {
            self.benchbase_config_dir: {
                "bind": "/benchbase/config",
                "mode": "rw",
            }
        }

        try:
            container = self.docker_client.containers.run(
                self.benchbase_image,
                name=self.benchbase_container_name,
                network_mode="host",
                volumes=volumes_mapping,
                command=[
                    "--bench",
                    self.workload,
                    "--config",
                    f"/benchbase/config/sample_{self.workload}_config.xml",
                    "--create=true",
                    "--load=true",
                ],
                detach=True,
                stdout=True,
                stderr=True,
                remove=True,
            )

            if self.debug_mode:
                for line in container.logs(stream=True, follow=True):
                    logger.info(line.strip().decode("utf-8"))
            else:
                container.wait()

        except docker.errors.DockerException as e:
            logger.error(f"Error running BenchBase container: {e}")
            raise

        logger.info("Database loaded successfully!")

        self._gracefully_stop_mysql_container(self.mysql_container_name)

    def _wait_for_mysql_ready(self, timeout=None):
        default_timeout = config_loader.get_config().getint(
            "database", "mysql_start_timeout"
        )
        timeout = timeout or default_timeout

        logger.info(f"Waiting for MySQL to start (timeout: {timeout} seconds)...")

        start_time = time.time()
        while True:
            if self._is_mysql_ready():
                logger.info("MySQL is ready!")
                return True
            if time.time() - start_time >= timeout:
                logger.error(f"MySQL is not ready after {timeout} seconds.")
                # It may be better to keep the container existing for debugging
                # self.mysql_container.stop()
                # self.mysql_container.remove()
                return False
            time.sleep(5)

    def _is_mysql_ready(self):
        try:
            if self.mysql_container.status == "exited":
                raise RuntimeError("MySQL container failed to start.")

            with pymysql.connect(
                host="127.0.0.1", port=3307, user="admin", password="password"
            ):
                return True
        except pymysql.err.OperationalError as e:
            logger.warning(f"MySQL is not ready yet: {e}. Retrying...")
            return False

    def execute_benchmark(self):
        self._remove_existing_container(self.benchbase_container_name)
        # Clean up the results directory
        for item in self.benchbase_results_dir.iterdir():
            if item.is_file():
                item.unlink()

        volumes_mapping = {
            self.benchbase_config_dir: {
                "bind": "/benchbase/config",
                "mode": "rw",
            },
            self.benchbase_results_dir: {
                "bind": "/benchbase/results",
                "mode": "rw",
            },
        }
        try:
            container = self.docker_client.containers.run(
                self.benchbase_image,
                name=self.benchbase_container_name,
                network_mode="host",
                volumes=volumes_mapping,
                command=[
                    "--bench",
                    self.workload,
                    "--config",
                    f"/benchbase/config/sample_{self.workload}_config.xml",
                    "--execute=true",
                    "--sample 1",
                    "--interval-monitor 1000",
                    "--json-histograms results/histograms.json",
                ],
                stdout=True,
                stderr=True,
                remove=True,
                detach=True,
            )

            if self.debug_mode:
                for line in container.logs(stream=True, follow=True):
                    logger.info(line.strip().decode("utf-8"))
            else:
                container.wait()

        except docker.errors.DockerException as e:
            logger.error(f"Error running BenchBase container: {e}")
            raise RuntimeError("Failed to run BenchBase.")

    def get_config_space(self) -> dict:
        return self.config_space.get_all_details()

    # def get_metrics(self, knobs):
    #     self.run()

    def run_with_random(self) -> dict:
        self.config_space.set_random_config()
        self.config_space.generate_config_file(self.mysql_config_file)

        try:
            self.start_mysql_and_wait()
            self.execute_benchmark()
            return self.parse_results()
        except Exception as e:
            logger.error(f"Error running MySQL benchmark: {e}")
            raise

    def run(self, knobs: dict) -> dict:
        self.config_space.set_current_config(knobs)
        self.config_space.generate_config_file(self.mysql_config_file)

        try:
            self.start_mysql_and_wait()
            self.execute_benchmark()
            return self.parse_results()
        except Exception as e:
            logger.error(f"Error running MySQL benchmark: {e}")
            raise
    
    def parse_results(self) -> dict:
        summary_file = None
        for item in self.benchbase_results_dir.iterdir():
            if item.is_file() and item.name.endswith(".summary.json"):
                summary_file = item

        if summary_file is None:
            logger.error(f"No results found in {self.benchbase_results_dir}")
            raise RuntimeError("No results found in the results directory.")

        result = {}
        with open(summary_file) as f:
            summary = json.load(f)
            result["latency"] = summary["Latency Distribution"][
                "95th Percentile Latency (microseconds)"
            ]
            result["throughput"] = summary["Throughput (requests/second)"]

        return result

    def __del__(self):
        if hasattr(self, "docker_client"):
            self.docker_client.close()
