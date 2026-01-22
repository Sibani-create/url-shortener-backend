#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Start the server
# We use --host 0.0.0.0 because cloud servers need to listen on all ports, not just localhost
# We use $PORT because Render assigns a random port number dynamically
uvicorn app.main:app --host 0.0.0.0 --port $PORT