#!/bin/sh
set -e

# Configuration
REPO="WaleX-projects/commitdev-cli"
BINARY_NAME="commitdev"
TARGET_DIR="/usr/local/bin"

# CommitDev Color System 
BOLD='\033[1m'
EMERALD='\033[38;5;48m' 
DIM='\033[2m'           
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

# ─── SMART VERSION DETECTION ───
# Hits GitHub's API to find your latest published release tag automatically
echo "  ${DIM}›${RESET} Checking latest release version..."
VERSION=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$VERSION" ]; then
    echo "  ${DIM}✕ Error:${RESET} Could not resolve latest release version. Falling back to API redirect..."
    DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/$ASSET_NAME"
else
    echo "  ${DIM}›${RESET} Found active release: ${BOLD}$VERSION${RESET}"
    DOWNLOAD_URL="https://github.com/$REPO/releases/download/$VERSION/$ASSET_NAME"
fi

echo "  ${DIM}›${RESET} Downloading platform asset: ${BOLD}$ASSET_NAME${RESET}"
# Download to /tmp safely
curl -L -f "$DOWNLOAD_URL" -o "/tmp/$BINARY_NAME" || {
    echo "  ${DIM}✕ Error:${RESET} Failed to download binary asset from $DOWNLOAD_URL."
    echo "            Ensure your GitHub Actions workflow finished and uploaded the asset."
    exit 1
}

echo "  ${DIM}›${RESET} Moving binary to $TARGET_DIR ${DIM}(requires system privileges)${RESET}"
sudo mv "/tmp/$BINARY_NAME" "$TARGET_DIR/$BINARY_NAME"
sudo chmod +x "$TARGET_DIR/$BINARY_NAME"

echo "  ${EMERALD}✓${RESET} Binary installed globally successfully"
echo ""

echo "${BOLD}Initializing CLI Workspace:${RESET}"
# Execute with full path to prevent any shell hashing delay issues
"$TARGET_DIR/$BINARY_NAME" setup
