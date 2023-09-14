#!/bin/env bash
set -e

docker build -t aries-my-agent . || exit 1
docker container run --rm -it \
    -p 0.0.0.0:8000:8010 \
    -e GENESIS_URL="http://172.17.0.1:9000/genesis" \
    aries-my-agent || exit 1
