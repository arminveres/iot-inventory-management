#!/bin/env bash
set -e

START_PORT=8100
NAME_PREFIX="controller_node_"

mkdir -p logs
for ((i = 0; i < 10; i++)); do
    echo "Running node: $i"
    ./run --no-interactive --type node --port $((START_PORT + i * 10)) --name "$NAME_PREFIX$i" &>logs/node_$i.txt &
    sleep 3
done
