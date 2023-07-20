import subprocess
import importlib_resources as resources
from pathlib import Path


def setup_docker_compiler():
    # current_dir = Path(__file__).resolve().parent.parent
    # pkg_path = Path(pkg_resources.get_distribution("csstuning").location)
    pkg_path = resources.files('cssbenchmarks')
    script_path = pkg_path / "compiler/docker/build_docker.sh"
    subprocess.run(str(script_path), shell=True)
