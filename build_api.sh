#!/usr/bin/env bash
set -euxo pipefail

docker build -t ${1:-ghcr.io/remember-to-remember/personal-ai-assistant-api:latest} .
