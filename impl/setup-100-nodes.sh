#!/bin/env bash
set -e

for ((i = 0; i < 10; i++)); do
    echo "Running node: $i"
    ./run --no-interactive --type node --port $((8000 + i * 10)) --name "node_$i" &>logs/node_$i.txt &
    sleep 3
done
