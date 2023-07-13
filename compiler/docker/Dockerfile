FROM ubuntu:focal as builder

CMD ["/bin/bash"]

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates apt-utils time bc jq  \
    && rm -rf /var/lib/apt/lists/*

# Install clang-15
RUN apt-get update \
  && apt-get install -y --no-install-recommends wget gnupg \
  && echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal-15 main" >> /etc/apt/sources.list \
  && echo "deb-src http://apt.llvm.org/focal/ llvm-toolchain-focal-15 main" >> /etc/apt/sources.list \
  && wget --no-check-certificate -O - http://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - \
  && apt-get update \
  && apt-get -y --no-install-recommends install \
    clang-15 clang-tools-15 llvm-15 lld-15 \
  && apt-get -y install cmake\
  && apt-get -y install make\
  && apt-get purge -y --auto-remove wget gnupg \
  && rm -rf /var/lib/apt/lists/* \
  && ln -s /usr/bin/clang-15 /usr/bin/clang \
  && ln -s /usr/bin/clang++-15 /usr/bin/clang++ \
  && ln -s /usr/bin/opt-15 /usr/bin/opt \
  && ln -s /usr/bin/llc-15 /usr/bin/llc \
  && ln -s /usr/bin/llvm-link-15 /usr/bin/llvm-link


COPY benchmark /benchmark