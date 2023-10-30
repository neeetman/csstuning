import docker
import time

class MySQLBenchmark:
    def __init__(self, docker_image="mysql:latest"):
        self.docker_image = docker_image
        self.client = docker.from_env()
        self.container = self.client.containers.run(
            image=self.docker_image,
            command="--default-authentication-plugin=mysql_native_password",
            environment={"MYSQL_ROOT_PASSWORD": "password"},
            detach=True,
            remove=True
        )

    def run(self, query):
        start = time.time()
        result = self.container.exec_run(
            f"mysql -uroot -ppassword -e '{query}'",
            stream=True
        )
        execution_time = time.time() - start

        for line in result.output:
            print(line.decode('utf-8'), end='')

        return execution_time

    def __del__(self):
        self.container.kill()
        self.client.close()