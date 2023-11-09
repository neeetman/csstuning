import docker
import json
import os
import subprocess
import time
import pymysql
from importlib import resources
from abc import ABC, abstractmethod
from docker.errors import ContainerError
from pathlib import Path
from csstuning.dbms.dbms_config_space import MySQLConfigSpace


# class DBMSBenchmarkBase(ABC):
#     def __init__(self, workload, knobs_file):
#         self.workload = workload
#         self.knobs_file = knobs_file
#         self.initialize()

#     def initialize(self) -> None:
#         self.load_default_knobs()

#     @abstractmethod
#     def load_default_knobs(self):
#         pass

#     @abstractmethod
#     def run(self, benchmark, flags={}) -> dict:
#         if benchmark not in self.benchmarks:
#             return {"return": 1, "msg": f"Invalid {benchmark}!"}

#         flagsstr = self.preprocess_flags(flags)

#         if not self.docker_mode:
#             return self.run_in_local(benchmark, flagsstr)
#         else:
#             return self.run_in_docker(benchmark, flagsstr)

#     @abstractmethod
#     def preprocess_flags(self, flags={}) -> str:
#         pass

#     @abstractmethod
#     def run_in_docker(self, benchmark, flags={}) -> dict:
#         pass

#     @abstractmethod
#     def run_in_local(self, benchmark, flags={}) -> dict:
#         pass

#     def __del__(self):
#         if self.docker_mode and self.container is not None:
#             self.container.kill()
#             self.client.close()


class MySQLBenchmark:
    def __init__(self, workload, knobs_file=None):
        self.mysql_image = "mysql:5.7"
        self.vcpus = 8.0
        self.mem = 16.0  # GB
        self.gen_file_path = "/tmp/custom.cnf"

        self.workload = workload
        self.config_space = MySQLConfigSpace(knobs_file)

        self.initialize()

    def initialize(self):
        self.docker_client = docker.from_env()
        self.start_mysql()

    def start_mysql(self):
        script_path = resources.path("cssbench.dbms.docker", "start_mysql.sh")
        subprocess.run(
            [
                script_path,
                "--config-file",
                self.gen_file_path,
                "--cpus",
                str(self.vcpus),
                "--memory",
                f"{self.mem}g",
            ],
            capture_output=True,
        )

        
        self.wait_for_mysql()
        # self.mysql_container = self.docker_client.containers.run(
        # image="mysql:5.7",
        # environment={
        # "MYSQL_ROOT_PASSWORD": "password",
        # "MYSQL_USER": "admin",
        # "MYSQL_PASSWORD": "password",
        # "MYSQL_DATABASE": "benchbase"
        # },
        # detach=True,
        # ports={"3306/tcp": 3307},
        # nano_cpus=int(self.vcpus * 1e9),
        # mem_limit=f"{self.mem}g",
        # volumes={
        # self.gen_file_path: {"bind": "/etc/mysql/conf.d/custom.cnf", "mode": "ro"}
        # },
        # environment={"MYSQL_ROOT_PASSWORD": "root"},
        # )

    def is_mysql_running(self):
        # Check if the MySQL container is running
        try:
            connection = pymysql.connect(
                host="127.0.0.1", port=3307, user="admin", password="password"
            )
            connection.close()
            return True
        except pymysql.err.OperationalError:
            return False

    def wait_for_mysql(self):
        attempts = 30
        while not self.is_mysql_running():
            time.sleep(5)
            attempts -= 1

            if attempts == 0:
                raise TimeoutError("Unable to start MySQL container!")

        return True

    def apply_config(self):
        # Generate the MySQL config file
        self.config_space.generate_config_file(self.gen_file_path)

        # Restart the MySQL container

    def __del__(self):
        self.docker_client.close()
