#!/usr/bin/env bash
# Install git-lfs to ~/.local/bin on macOS when brew/port unavailable.
# Idempotent: exits 0 if already installed.
set -euo pipefail

if command -v git-lfs >/dev/null 2>&1; then
    echo "[ok] git-lfs already on PATH: $(which git-lfs)"
    git-lfs version
    exit 0
fi

VERSION="3.5.1"
ARCH=$(uname -m)
case "$ARCH" in
    arm64) ZIP="git-lfs-darwin-arm64-v${VERSION}.zip" ;;
    x86_64) ZIP="git-lfs-darwin-amd64-v${VERSION}.zip" ;;
    *) echo "[abort] unsupported arch: $ARCH"; exit 1 ;;
esac

DEST="$HOME/.local/bin"
mkdir -p "$DEST"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "[info] downloading git-lfs v${VERSION} for darwin-${ARCH}..."
curl -sL -o "$TMP/git-lfs.zip" \
    "https://github.com/git-lfs/git-lfs/releases/download/v${VERSION}/${ZIP}"

unzip -q "$TMP/git-lfs.zip" -d "$TMP/extracted"
BIN=$(find "$TMP/extracted" -name git-lfs -type f -perm -u+x | head -1)
if [[ -z "$BIN" ]]; then
    echo "[abort] git-lfs binary not found in zip"
    exit 1
fi

cp "$BIN" "$DEST/git-lfs"
chmod +x "$DEST/git-lfs"
echo "[ok] installed to $DEST/git-lfs"
"$DEST/git-lfs" version

if ! echo "$PATH" | tr ':' '\n' | grep -qx "$DEST"; then
    echo "[warn] $DEST is not on PATH — add it to your shell rc:"
    echo '       export PATH="$HOME/.local/bin:$PATH"'
fi
