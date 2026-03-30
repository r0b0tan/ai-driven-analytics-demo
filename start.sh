#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# ── Backend ───────────────────────────────────────────────────────────────────
echo "-> Setting up backend…"
cd backend

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

echo "-> Starting backend on http://localhost:8000"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# ── Frontend ──────────────────────────────────────────────────────────────────
echo "-> Installing frontend dependencies…"
cd frontend

if [ ! -d node_modules ]; then
  npm install
fi

echo "-> Starting frontend on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!
cd ..

# ── Cleanup on exit ──────────────────────────────────────────────────────────
trap "echo '[stop] Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

echo ""
echo "OK Backend:  http://localhost:8000"
echo "OK Frontend: http://localhost:5173"
echo "  Press Ctrl+C to stop both."
echo ""

wait
