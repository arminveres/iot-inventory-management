#!/bin/env bash
set -e

HOST_IP=$(./scripts/getDockerHost.sh)
LEDGER_URL="http://$HOST_IP:9000"
GENESIS_URL="$LEDGER_URL/genesis"

agent_name=$1
port=$2
portrange="$2-$((port + 9))"
# echo "$portrange"

docker build -t aries-my-agent . || exit 1
docker container run --rm -it \
    --network=host \
    -p 0.0.0.0:"$portrange":"$portrange" \
    -e LEDGER_URL="$LEDGER_URL" \
    -e GENESIS_URL="$GENESIS_URL" \
    aries-my-agent "$agent_name" \
    --wallet-type askar \
    --port "$port" \
    --did-exchange \
    --reuse-connections
