#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

[ -d venv ] || { python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt; }
. venv/bin/activate
[ -d frontend/node_modules ] || (cd frontend && npm install)
[ -f frontend/dist/index.html ] || (cd frontend && npm run build)

echo "Server: http://localhost:8000"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
