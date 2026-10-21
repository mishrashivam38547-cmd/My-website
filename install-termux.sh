#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v python >/dev/null 2>&1; then
  echo "Python missing. Run: pkg update && pkg install python"
  exit 1
fi
python -m venv .venv || { echo "Virtual environment creation failed."; exit 1; }
chmod +x run.sh
if ! command -v termux-wifi-scaninfo >/dev/null 2>&1; then
  echo "Optional nearby Wi-Fi scanning: pkg install termux-api"
  echo "Install the Termux:API Android app too; grant permissions. Root is not required."
fi
echo "Installed. Run: ./run.sh"
echo "GUI is generally unavailable in a normal Termux session; terminal mode is supported."
