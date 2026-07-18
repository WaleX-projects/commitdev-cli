#!/usr/bin/env sh
set -e

# ==================================================
# CommitDev Installer
# ==================================================

REPO="WaleX-projects/commitdev-cli"
BINARY_NAME="commitdev"
TMP_DIR="/tmp"

# ==================================================
# Colors
# ==================================================

BOLD='\033[1m'
EMERALD='\033[38;5;48m'
DIM='\033[2m'
RED='\033[31m'
RESET='\033[0m'

echo ""
echo "${BOLD}${EMERALD}CommitDev${RESET} ${DIM}•${RESET} Installer"
echo "${DIM}──────────────────────────────────────────────────${RESET}"

# ==================================================
# Detect Platform
# ==================================================

echo ""
echo "• Detecting platform..."

OS_TYPE="$(uname -s)"
case "$OS_TYPE" in
    Linux*)
        PLATFORM="Linux"
        ASSET_NAME="commitdev-linux"
        INSTALL_DIR="/usr/local/bin"
        TMP_FILE="${TMP_DIR}/${BINARY_NAME}"
        EXE_EXT=""
        ;;
    Darwin*)
        PLATFORM="macOS"
        ASSET_NAME="commitdev-macos"
        INSTALL_DIR="/usr/local/bin"
        TMP_FILE="${TMP_DIR}/${BINARY_NAME}"
        EXE_EXT=""
        ;;
    MSYS*|MINGW*|CYGWIN*|Windows_NT*)
        PLATFORM="Windows"
        ASSET_NAME="commitdev-windows.exe"
        # Common local bin directory for Git Bash / MSYS environments
        INSTALL_DIR="/usr/bin" 
        TMP_FILE="${TMP_DIR}/${BINARY_NAME}.exe"
        EXE_EXT=".exe"
        ;;
    *)
        echo "  ${RED}✕ Unsupported operating system: ${OS_TYPE}${RESET}"
        exit 1
        ;;
esac

# Finalize binary target name
TARGET_BINARY="${BINARY_NAME}${EXE_EXT}"

echo "  ${EMERALD}✓${RESET} ${PLATFORM}"

# ==================================================
# Check Existing Installation
# ==================================================

echo ""
echo "• Checking existing installation..."

CURRENT_VERSION=""

if command -v "$BINARY_NAME" >/dev/null 2>&1; then

    CURRENT_VERSION=$("$BINARY_NAME" --version 2>/dev/null \
        | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' \
        | head -1)

    if [ -n "$CURRENT_VERSION" ]; then
        echo "  ${EMERALD}✓${RESET} Found CommitDev ${CURRENT_VERSION}"
    else
        echo "  ${DIM}›${RESET} Existing installation detected."
    fi

else

    echo "  ${DIM}›${RESET} CommitDev is not installed."

fi

# ==================================================
# Latest Release
# ==================================================

echo ""
echo "• Checking latest release..."

# Using curl with fallback to wget if not installed
if command -v curl >/dev/null 2>&1; then
    RELEASE_JSON=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest")
elif command -v wget >/dev/null 2>&1; then
    RELEASE_JSON=$(wget -qO- "https://api.github.com/repos/$REPO/releases/latest")
else
    echo "  ${RED}✕ Neither curl nor wget is installed.${RESET}"
    exit 1
fi

LATEST_VERSION=$(echo "$RELEASE_JSON" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LATEST_VERSION" ]; then
    echo "  ${RED}✕ Failed to determine the latest release.${RESET}"
    exit 1
fi

echo "  ${EMERALD}✓${RESET} ${LATEST_VERSION}"

# ==================================================
# Already Up To Date?
# ==================================================

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then

    echo ""
    echo "${DIM}──────────────────────────────────────────────────${RESET}"
    echo "${EMERALD}✓${RESET} You're already running the latest version."
    exit 0

fi

# ==================================================
# Download
# ==================================================

echo ""

if [ -n "$CURRENT_VERSION" ]; then
    echo "• Updating CommitDev..."
else
    echo "• Installing CommitDev..."
fi

echo "  ${DIM}›${RESET} Downloading release..."

DOWNLOAD_URL="https://github.com/$REPO/releases/download/$LATEST_VERSION/$ASSET_NAME"

if command -v curl >/dev/null 2>&1; then
    curl -L -f "$DOWNLOAD_URL" -o "$TMP_FILE"
else
    wget -O "$TMP_FILE" "$DOWNLOAD_URL"
fi

# Make it executable inside the temp directory (non-critical on raw Windows but safe)
chmod +x "$TMP_FILE"

echo "  ${EMERALD}✓${RESET} Download complete."

# ==================================================
# Install
# ==================================================

echo "  ${DIM}›${RESET} Installing executable..."

# Use sudo only if running on UNIX/Linux/macOS and not already root.
# Most Windows Git Bash environments don't have/need 'sudo' to write to /usr/bin.
USE_SUDO=""
if [ "$PLATFORM" != "Windows" ] && [ "$(id -u)" -ne 0 ]; then
    USE_SUDO="sudo"
fi

$USE_SUDO mv "$TMP_FILE" "$INSTALL_DIR/$TARGET_BINARY"
$USE_SUDO chmod +x "$INSTALL_DIR/$TARGET_BINARY"

echo "  ${EMERALD}✓${RESET} Installed to ${INSTALL_DIR}/${TARGET_BINARY}"

# ==================================================
# Initialize
# ==================================================

echo ""
echo "• Initializing workspace..."

"$INSTALL_DIR/$TARGET_BINARY" setup

echo "  ${EMERALD}✓${RESET} Workspace initialized."

# ==================================================
# Finished
# ==================================================

echo ""
echo "${DIM}──────────────────────────────────────────────────${RESET}"
echo "${EMERALD}✓${RESET} CommitDev ${LATEST_VERSION} is ready."
echo ""
echo "Run:"
echo ""
echo "  ${BOLD}${BINARY_NAME} login${RESET}"
echo ""
