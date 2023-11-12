#!/bin/env bash
set -e

# on Windows, docker run needs to be prefixed by winpty
if [ "$OSTYPE" == "msys" ]; then
    DOCKER="winpty docker"
else
    DOCKER=${DOCKER:-docker}
fi

$DOCKER stop indy-demo-postgres &>/dev/null && echo "Stopped previous postgres container" || true

if [[ $1 == 'node' ]]; then
    exit 0
fi

echo "Running from Directory:  $(pwd)"

"$(pwd)"/dependencies/von-network/manage down
"$(pwd)"/dependencies/indy-tails-server/docker/manage down

$DOCKER container stop oriondb &>/dev/null && echo "Stopped previous orion container" || true
