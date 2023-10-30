FROM eclipse-temurin:17-jre AS fullimage

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install --no-install-recommends sudo vim-nox neovim less bash-completion colordiff git openssh-client jq \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Get user and group IDs from build args:
# docker build --build-arg CONTAINERUSER_UID=$(id -u) --build-arg CONTAINERUSER_GID=$(id -g)
ARG CONTAINERUSER_UID=1000
ARG CONTAINERUSER_GID=1000
RUN groupadd --non-unique --gid ${CONTAINERUSER_GID} containergroup \
    && useradd --non-unique --create-home --no-user-group --comment 'Container User' \
        --uid ${CONTAINERUSER_UID} --gid ${CONTAINERUSER_GID} containeruser \
    && mkdir -p /benchbase/results \
    && chown -R containeruser:containergroup /benchbase

USER containeruser
WORKDIR /benchbase
VOLUME /benchbase/results

COPY benchbase-mysql.tgz .
RUN tar -xzf benchbase-mysql.tgz -C /benchbase && \
    mv /benchbase/benchbase-mysql /benchbase/mysql && \ 
    rm benchbase-mysql.tgz

CMD ["/bin/bash"]