#!/bin/sh
set -e

TARGET_DIR="/usr/local/bin"
BINARY_NAME="commitdev"
REPO_URL="https://github.com/WaleX-projects/commitDev/releases/download/v1.0.0/commitdev"

echo "💻 Desktop/Server environment detected."
echo "📥 Downloading $BINARY_NAME..."

# Download to a temporary file name to prevent local folder collisions
curl -L -s -o "./commitdev_temp" "$REPO_URL"

echo "⚙️ Making it executable..."
chmod +x "./commitdev_temp"

echo "🚀 Installing to $TARGET_DIR (requires sudo)..."
sudo mv "./commitdev_temp" "$TARGET_DIR/$BINARY_NAME"

echo "✨ Installation complete! Run '$BINARY_NAME --help' to test."
