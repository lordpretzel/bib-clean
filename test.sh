#!/bin/bash
set -e
cd "$(dirname "$0")"
nix develop -c pytest tests/ -v