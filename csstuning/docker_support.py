import subprocess
from pathlib import Path


def setup_docker_compiler():
        current_dir = Path(__file__).resolve().parent.parent
        script_path = current_dir / "compiler/docker/build_docker.sh"
        subprocess.run(str(script_path), shell=True)

