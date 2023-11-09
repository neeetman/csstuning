#!/bin/bash

set -eu
scriptdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
cd "$scriptdir/"

DIRECTORY=$scriptdir
FILE_PATTERN="*.xml"

NEW_PORT="${1:-3307}"

if ! [[ $NEW_PORT =~ ^[0-9]+$ ]]; then
    echo "Error: Port number must be a valid integer."
    exit 1
fi

REGEX_PATTERN="jdbc:mysql:\/\/localhost:[0-9]+\/benchbase"

# Process all files that match the FILE_PATTERN in the DIRECTORY
find "$DIRECTORY" -type f -name "$FILE_PATTERN" -exec sed -i -E "s/$REGEX_PATTERN/jdbc:mysql:\/\/localhost:$NEW_PORT\/benchbase/g" {} \;

echo "All files have been updated to use port $NEW_PORT for JDBC connections."