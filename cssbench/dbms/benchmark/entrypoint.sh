#!/bin/bash

# fullimage docker entrypoint script

set -eu

cd /benchbase
if ! [ -d results/ ] || ! [ -w results/ ]; then
    echo "ERROR: The results directory either doesn't exist or isn't writable." >&2
fi
exec java -jar benchbase.jar $*