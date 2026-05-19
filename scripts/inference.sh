#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" python infer.py "$@"
