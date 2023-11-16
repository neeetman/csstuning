FROM ubuntu:focal as builder

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates apt-utils time bc jq wget gnupg cmake make build-essential python3\
    && echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal-15 main" >> /etc/apt/sources.list \
    && echo "deb-src http://apt.llvm.org/focal/ llvm-toolchain-focal-15 main" >> /etc/apt/sources.list \
    && wget --no-check-certificate -O - http://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - \
    && apt-get update \
    && apt-get -y --no-install-recommends install \
    clang-15 clang-tools-15 llvm-15 lld-15 libpolly-15-dev \
    && ln -s /usr/bin/clang-15 /usr/bin/clang \
    && ln -s /usr/bin/clang++-15 /usr/bin/clang++ \
    && ln -s /usr/bin/opt-15 /usr/bin/opt \
    && ln -s /usr/bin/llc-15 /usr/bin/llc \
    && ln -s /usr/bin/llvm-as-15 /usr/bin/llvm-as \
    && ln -s /usr/bin/llvm-link-15 /usr/bin/llvm-link \
    && apt-get purge -y --auto-remove wget gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY benchmark /benchmark

ENV PAPI_DIR=/benchmark/utilities/papi \
    POLYBENCH_DIR=/benchmark/utilities/polybench
ENV LD_LIBRARY_PATH=${PAPI_DIR}/lib:${POLYBENCH_DIR}/lib:${LD_LIBRARY_PATH}

WORKDIR /benchmark

RUN /bin/bash /benchmark/init.sh

ENTRYPOINT ["python3", "/benchmark/run.py"]
