#!/usr/bin/env sh
set -e

# ==================================================
# CommitDev Installer
# ==================================================

REPO="WaleX-projects/commitdev-cli"

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

case "$(uname -s)" in
    Linux*)
        PLATFORM="Linux"
        ASSET_NAME="commitdev-linux"
        BINARY_NAME="commitdev"
        INSTALL_DIR="/usr/local/bin"
        TMP_FILE="/tmp/commitdev"
        ;;
    Darwin*)
        PLATFORM="macOS"
        ASSET_NAME="commitdev-macos"
        BINARY_NAME="commitdev"
        INSTALL_DIR="/usr/local/bin"
        TMP_FILE="/tmp/commitdev"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        PLATFORM="Windows (Git Bash)"
        ASSET_NAME="commitdev-windows.exe"
        BINARY_NAME="commitdev.exe"
        INSTALL_DIR="/usr/bin"
        TMP_FILE="/tmp/commitdev.exe"
        ;;
    *)
        echo "  ${RED}✕ Unsupported operating system or shell environment.${RESET}"
        exit 1
        ;;
esac

echo "  ${EMERALD}✓${RESET} ${PLATFORM}"

# ==================================================
# Check Write Permissions & Setup Sudo
# ==================================================

USE_SUDO=""
if [ "$PLATFORM" != "Windows (Git Bash)" ]; then
    # If we don't have write access to the directory, prep 'sudo'
    if [ ! -w "$INSTALL_DIR" ]; then
        if command -v sudo >/dev/null 2>&1; then
            USE_SUDO="sudo"
        else
            echo "  ${RED}✕ Write permission denied for $INSTALL_DIR and sudo is not available.${RESET}"
            exit 1
        fi
    fi
fi

# ==================================================
# Check Existing Installation
# ==================================================

echo ""
echo "• Checking existing installation..."

CURRENT_VERSION=""

if command -v "$BINARY_NAME" >/dev/null 2>&1; then

    CURRENT_VERSION=$("$BINARY_NAME" --version \
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

LATEST_VERSION=$(curl -fsSL \
"https://api.github.com/repos/$REPO/releases/latest" \
| grep '"tag_name":' \
| sed -E 's/.*"([^"]+)".*/\1/')

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

curl -L -f "$DOWNLOAD_URL" -o "$TMP_FILE"

chmod +x "$TMP_FILE"

echo "  ${EMERALD}✓${RESET} Download complete."

# ==================================================
# Install
# ==================================================

echo "  ${DIM}›${RESET} Installing executable..."

$USE_SUDO mv "$TMP_FILE" "$INSTALL_DIR/$BINARY_NAME"
$USE_SUDO chmod +x "$INSTALL_DIR/$BINARY_NAME"

echo "  ${EMERALD}✓${RESET} Installed to ${INSTALL_DIR}/${BINARY_NAME}"

# ==================================================
# Initialize
# ==================================================

echo ""
echo "• Initializing workspace..."

"$INSTALL_DIR/$BINARY_NAME" setup

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
echo "  ${BOLD}commitdev login${RESET}"
echo ""
