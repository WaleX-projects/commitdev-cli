#!/bin/sh
set -e

# Configuration
REPO="WaleX-projects/commitdev-cli"
VERSION="v1.1.3"
BINARY_NAME="commitdev"
TARGET_DIR="/usr/local/bin"

# CommitDev Color System from Screenshot_2026-06-29-14-47-05-440_com.android.chrome.jpg
BOLD='\033[1m'
EMERALD='\033[38;5;48m' # Rich mint/emerald brand color
GREEN='\033[32m'
DIM='\033[2m'           # Secondary slate grey hints
RESET='\033[0m'

echo ""
echo "${BOLD}${EMERALD}CommitDev${RESET} ${DIM}•${RESET} Installer"
echo "${DIM}──────────────────────────────────────────────────${RESET}"

# Operating System detection block
OS_TYPE=$(uname -s)
if [ "$OS_TYPE" = "Linux" ]; then
    ASSET_NAME="commitdev-linux"
elif [ "$OS_TYPE" = "Darwin" ]; then
    ASSET_NAME="commitdev-macos"
else
    echo "  ${DIM}✕ Error:${RESET} This install script only supports Linux and macOS."
    exit 1
fi

DOWNLOAD_URL="https://github.com/$REPO/releases/download/$VERSION/$ASSET_NAME"

echo "  ${DIM}›${RESET} Downloading platform asset: ${BOLD}$ASSET_NAME${RESET}"
curl -L -s -f "$DOWNLOAD_URL" -o "/tmp/$BINARY_NAME"

echo "  ${DIM}›${RESET} Moving binary to $TARGET_DIR ${DIM}(requires system privileges)${RESET}"
sudo mv "/tmp/$BINARY_NAME" "$TARGET_DIR/$BINARY_NAME"
sudo chmod +x "$TARGET_DIR/$BINARY_NAME"

echo "  ${EMERALD}✓${RESET} Binary installed globally successfully"
echo ""

echo "${BOLD}Initializing CLI Workspace:${RESET}"
$BINARY_NAME setup
