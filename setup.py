import os
import shutil
from pathlib import Path
from importlib import resources
from setuptools import setup, find_packages
from setuptools.command.install import install


class CustomInstall(install):
    def run(self):
        install.run(self)

        default_prefix = os.path.expanduser("~")
        install_prefix = os.environ.get("CSSTUNING_PREFIX", default_prefix)
        csstuning_dir = Path(install_prefix, ".csstuning")

        install_info_file = Path(default_prefix, ".csstuing.ini")
        with open(install_info_file, "w") as file:
            file.write("[DEFAULT]\n")
            file.write(f"CSSTUNING_PREFIX={install_prefix}\n")
            file.write(f"CSSTUNING_DIR={csstuning_dir}\n")

        csstuning_dir.mkdir(parents=True, exist_ok=True)

        # copy default config file
        setup_dir = Path(__file__).parent
        default_conf_path = setup_dir / "csstuning/config/default.conf"
        target_conf_path = csstuning_dir / "default.conf"
        shutil.copy(default_conf_path, target_conf_path)

        self.initialize_compiler_data_dir(csstuning_dir)
        self.initialize_dbms_data_dir(csstuning_dir)

        self.setup_dockers()

    def initialize_compiler_data_dir(self, csstuning_dir):
        setup_dir = Path(__file__).parent
        compiler_config_dir = csstuning_dir / "compiler/config"

        compiler_config_source = setup_dir / "cssbench/compiler/config"
        copy_all(compiler_config_source, compiler_config_dir)

        print(f"Initialized compiler benchmark data directory at {csstuning_dir}/compiler")

    def initialize_dbms_data_dir(self, csstuning_dir):
        setup_dir = Path(__file__).parent
        dbms_config_dir = csstuning_dir / "dbms/config"
        mysql_data_dir = csstuning_dir / "dbms/mysql_data"
        benchbase_config_dir = csstuning_dir / "dbms/benchbase_data/config"
        benchbase_results_dir = csstuning_dir / "dbms/benchbase_data/results"

        mysql_data_dir.mkdir(parents=True, exist_ok=True)
        benchbase_config_dir.mkdir(parents=True, exist_ok=True)
        benchbase_results_dir.mkdir(parents=True, exist_ok=True)

        # Copy without overwriting the existing config files 
        # if not any(benchbase_config_dir.iterdir()):
        #     benchbase_source_path = setup_dir / "cssbench/dbms/config/benchbase"
        #     copy_all(benchbase_source_path, benchbase_config_dir)

        # Copy and overwrite the existing config files
        benchbase_source_path = setup_dir / "cssbench/dbms/config/benchbase"
        copy_all(benchbase_source_path, benchbase_config_dir)
        
        dbms_config_source = setup_dir / "cssbench/dbms/config/mysql"
        copy_all(dbms_config_source, dbms_config_dir)

        print(f"Initialized dbms benchmark data directory at {csstuning_dir}/dbms")

    def setup_dockers(self):
        pass


def copy_all(src_path, dst_path):
    """
    Copies all files and directories from src_path to dst_path.

    :param src_path: Source directory (Path object).
    :param dst_path: Destination directory (Path object).
    """
    src_path = Path(src_path)
    dst_path = Path(dst_path)

    # Ensure the source directory exists
    if not src_path.exists():
        print(f"Source path {src_path} does not exist.")
        return

    # Create the destination directory if it doesn't exist
    dst_path.mkdir(parents=True, exist_ok=True)

    for item in src_path.iterdir():
        if item.is_dir():
            shutil.copytree(item, dst_path / item.name, dirs_exist_ok=True)
        else:
            shutil.copy(item, dst_path / item.name)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="csstuning",
    version="0.0.1",
    author="An Shao",
    author_email="anshaohac@gmail.com",
    description="Configurable Software System Tuning Benchmark",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neeetman/csstuning",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "csstuning=csstuning.kernel:cli",
            "csstuning_dbms_init=csstuning.kernel:load_dbms_database"
        ]
    },
    install_requires=["docker", "pymysql"],
    zip_safe=False,
    cmdclass={
        'install': CustomInstall,
    },
)
