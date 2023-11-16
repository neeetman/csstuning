# CSSTuning - Configurable Software Configuration Optimization Benchmark

CSSTuning is a comprehensive benchmark tool that caters to various real-world software configuration optimization problems. It offers a simple and rapid setup process for creating a software configuration optimization environment on Linux systems, accurately replicating real software configuration challenges.

## Introduction

Optimizing software configurations is a crucial aspect of performance tuning for a wide array of applications and systems. CSSTuning aims to address this need by providing an extensive collection of benchmark scenarios, each representing authentic software configuration optimization problems. Whether you are a developer, researcher, or enthusiast, CSSTuning provides an invaluable resource for assessing and optimizing the performance of diverse software configurations.

## Overview
The following block diagram shows the rough internal structure of CSStuing:

![CSSTuning System Structure](https://github.com/neeetman/csstuning/assets/71478917/35c04aeb-b942-46e8-8eb5-abd8507027ab)


## Benchmark List

- **Compiler**
- **Database Management System (DBMS)**
- **Web Server** *(In progress)*
- **Big Data System** *(In progress)*

### Key Features

- **Varied Benchmark Scenarios**: Emulates real-world software configuration optimization challenges across multiple systems.
- **Multi-objective Optimization**: Features diverse performance metrics, facilitating the creation of comprehensive optimization problems.
- **Containerized Benchmarks**: Guarantees easy reproducibility and resolves dependency issues by containerizing all benchmarks.
- **Industrial Data-driven Tuning**: Utilizes real-world data for practical and relevant optimization.

## Installation

**Prerequisites:**
- Python >= 3.8
- Docker
- Supported on POSIX Systems (Linux, MacOS)

**Setup Steps:**

1. **Install and configure Docker:**
   ```bash
   sudo groupadd docker
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Clone repository and install package:**
```
git clone https://github.com/neeetman/csstuning.git && cd csstuning
pip install .
```

3. **Build images:**
```
./cssbench/compiler/docker/build_docker.sh
./cssbench/dbms/docker/build_docker.sh
```

4. **Optional: Load Database for DBMS benchmark:**
```
csstuing_dbms_load -h
```


## Usage

### 1.Compiler Benchmarks

/*Use via command line*/

**GCC compiler**

```
# View the available benchmarks for GCC #
csstuning compiler:gcc list benchs
# View the available flags for GCC #
csstuning compiler:gcc list flags
# Help command #
csstuning --help
# Run GCC with specific benchmark and flags #
csstuning compiler:gcc run benchs=cbench-automotive-bitcount flags="ftree-loop-vectorize,ftree-partial-pre"
```

**LLVM compiler**

```
# View the available benchmarks for LLVM #
csstuning compiler:llvm cc list benchs
# View the available flags for LLVM #
csstuning compiler:llvm list flags
# Help command #
csstuning --help
# Run LLVM with specific benchmark and flags #
csstuning compiler:llvm run benchs=cbench-automotive-bitcount flags="vetor-combine"
```

# Use in python #

### 2.DBMS Benchmarks
