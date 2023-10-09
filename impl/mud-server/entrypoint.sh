#!/bin/env bash
set -e

USERNAME=arminveres
KARAF_DIR=/home/${USERNAME}/nist-mud/sdnmud-aggregator/karaf/target/assembly/bin

$KARAF_DIR/start && sleep 2

$KARAF_DIR/client "feature:install features-sdnmud"

# Add bash login for further interactive use
bash --login -i
