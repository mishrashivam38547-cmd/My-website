#!/usr/bin/env sh
DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if [ -x "$DIR/.venv/bin/python" ]; then
  PY="$DIR/.venv/bin/python"
else
  PY="${PYTHON:-python3}"
fi
cd "$DIR" || exit 1
exec "$PY" -m red_dragon.app "$@"
