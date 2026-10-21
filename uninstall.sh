#!/usr/bin/env sh
set -eu
DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
echo "This removes the project's .venv and generated launcher only."
printf "Continue? [y/N] "
read ans || true
case "$ans" in y|Y|yes|YES) rm -rf "$DIR/.venv"; rm -f "$DIR/red-dragon"; echo "Removed. Source files and reports were kept.";; *) echo "Cancelled.";; esac
