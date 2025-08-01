#!/bin/bash

set -eo pipefail

cd "$(dirname "$0")"
export $(cat .env)
python3 main.py