#!/usr/bin/env bash

set -euo pipefail

docker-compose up -d --build
./scripts/verify-demo.sh
