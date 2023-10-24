# Use a smaller base image that only has the jre, not the full jdk.
FROM eclipse-temurin:17-jre AS fullimage

LABEL org.opencontainers.image.source = "https://github.com/cmu-db/benchbase/"

# Add a containeruser that allows vscode/codespaces to map the local host user
# (often uid 1000) to some non-root user inside the container.
ARG CONTAINERUSER_UID=1000
ARG CONTAINERUSER_GID=1000
RUN groupadd --non-unique --gid ${CONTAINERUSER_GID} containergroup \
    && useradd --non-unique --create-home --no-user-group --comment 'Container User' \
        --uid ${CONTAINERUSER_UID} --gid ${CONTAINERUSER_GID} containeruser
RUN mkdir -p /benchbase/results && chown -R containeruser:containergroup /benchbase/results
USER containeruser
WORKDIR /benchbase
VOLUME /benchbase/results

# Only copy the content necessary for running (not building) benchbase over to the image.
# These files should have been built using the devcontainer by the
# build-full-image.sh script.
COPY --chown=containeruser:containergroup . /benchbase/

ENTRYPOINT ["/benchbase/entrypoint.sh"]
CMD ["--help"]