#!/bin/sh
set -e

# Configuration
REPO="WaleX-projects/commitdev-cli"
VERSION="v1.0.4" # Or use "latest" to dynamically grab the newest version later
BINARY_NAME="commitdev"
TARGET_DIR="/usr/local/bin"

echo "🚀 Starting commitdev installer..."

# 1. Detect Operating System architecture
OS_TYPE=$(uname -s)
if [ "$OS_TYPE" = "Linux" ]; then
    ASSET_NAME="commitdev-linux"
elif [ "$OS_TYPE" = "Darwin" ]; then
    ASSET_NAME="commitdev-macos"
else
    echo "❌ Error: This install script only supports Linux and macOS. For Windows, download commitdev-windows.exe directly from GitHub Releases."
    exit 1
fi

DOWNLOAD_URL="https://github.com/$REPO/releases/download/$VERSION/$ASSET_NAME"

echo "📥 Downloading $ASSET_NAME from GitHub Releases..."
curl -L -f "$DOWNLOAD_URL" -o "/tmp/$BINARY_NAME"

echo "⚙️ Installing binary to $TARGET_DIR (requires sudo access)..."
sudo mv "/tmp/$BINARY_NAME" "$TARGET_DIR/$BINARY_NAME"
sudo chmod +x "$TARGET_DIR/$BINARY_NAME"

echo "⚡ Running app configuration initialization..."
# Run the internal app configuration you built earlier
$BINARY_NAME setup

echo "✨ Installation complete! You can now use the '$BINARY_NAME' command globally."
