# Use a smaller base image that only has the jre, not the full jdk.
FROM maven:3.9.3-eclipse-temurin-17 AS devcontainer

LABEL org.opencontainers.image.source = "https://github.com/cmu-db/benchbase/"

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install --no-install-recommends sudo vim-nox neovim less bash-completion colordiff git openssh-client jq \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add a containeruser that allows vscode/codespaces to map the local host user
# (often uid 1000) to some non-root user inside the container.
ARG CONTAINERUSER_UID=1000
ARG CONTAINERUSER_GID=1000
RUN groupadd --non-unique --gid ${CONTAINERUSER_GID} containergroup \
    && useradd --non-unique --create-home --no-user-group --comment 'Container User' \
        --uid ${CONTAINERUSER_UID} --gid ${CONTAINERUSER_GID} containeruser \
    && echo 'containeruser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN mkdir -p /benchbase/results && chown -R containeruser:containergroup /benchbase/results
USER containeruser
ENV MAVEN_CONFIG=/home/containeruser/.m2
WORKDIR /benchbase
VOLUME /benchbase/results

ENV SHELL=/bin/bash
ENTRYPOINT ["/bin/bash", "-l"]