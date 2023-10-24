#!/bin/bash

set -eu

scriptdir=$(dirname "$(readlink -f "$0")")
rootdir=$(readlink -f "$scriptdir/../../")

cd "$scriptdir"