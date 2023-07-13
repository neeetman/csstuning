from setuptools import setup, find_packages

setup(
    name="csstuning",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    # package_data={
    #     "compiler": ["constants/**", "benchmark/**", "docker/**"],
    # },
    entry_points={
        "console_scripts": [
            "csstuning=csstuning.kernel:cli",
            "csstuning_setup_docker=csstuning.docker_support:setup_docker_compiler",
        ]
    }
)