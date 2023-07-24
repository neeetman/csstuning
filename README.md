# CSSTuning - Configurable Software Configuration Optimization Benchmark

CSSTuning is a comprehensive benchmark tool that caters to various real-world software configuration optimization problems. It offers a simple and rapid setup process for creating a software configuration optimization environment on Linux systems, accurately replicating real software configuration challenges.

## Introduction

Optimizing software configurations is a crucial aspect of performance tuning for a wide array of applications and systems. CSSTuning aims to address this need by providing an extensive collection of benchmark scenarios, each representing authentic software configuration optimization problems. Whether you are a developer, researcher, or enthusiast, CSSTuning provides an invaluable resource for assessing and optimizing the performance of diverse software configurations.

## Overview
The following block diagram shows the rough internal structure of CSStuing:

![system_structure](https://github.com/neeetman/csstuning/assets/71478917/eef95bd0-e9d3-4a3d-9ca8-ba743e7defc1)


## Benchmark List

Compiler

Data base manage system (DBMS) //to do

Web Server //to do

Big data system //to do

## Features

- Diverse Benchmark Scenarios: CSSTuning presents a rich set of benchmark scenarios that accurately emulate real-world software configuration optimization problems for multiple software systems.
- Multi-objective Optimization: For each software system, CSSTuning incorporates various officially recognized performance evaluation metrics, allowing the construction of multi-objective optimization problems.
- Containerized Benchmarks: All benchmarks in CSSTuning are containerized, eliminating dependency issues and ensuring easy reproducibility across different environments.
- Industrial Data-driven Tuning: CSSTuning goes beyond traditional benchmarks by providing the ability to optimize software systems using real-world industrial data, making the optimization process more relevant and practical.

## installation

**Prerequisites:**

- POSIX System (i.e. Linux, MacOS)
- Docker installed
- Python 3.8+

```
pip install csstuning --user
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
