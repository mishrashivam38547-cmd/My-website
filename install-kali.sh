#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 not found. On Kali: sudo apt update && sudo apt install python3 python3-venv python3-tk"
  exit 1
fi
python3 -m venv .venv || { echo "venv creation failed. Install python3-venv and retry."; exit 1; }
.venv/bin/python -m pip install --upgrade pip
chmod +x run.sh
cat > red-dragon <<'EOF'
#!/usr/bin/env sh
DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec "$DIR/run.sh" "$@"
EOF
chmod +x red-dragon
echo "Installed. Run: ./run.sh  (GUI: ./run.sh --gui)"
