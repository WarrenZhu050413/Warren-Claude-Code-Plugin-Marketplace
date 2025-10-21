#!/bin/bash
#
# Uninstallation script for snippets CLI
#
# Usage:
#   ./uninstall.sh           # Uninstall from /usr/local/bin
#   ./uninstall.sh ~/bin     # Uninstall from custom directory
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Default installation directory
INSTALL_DIR="${1:-/usr/local/bin}"
WRAPPER_SCRIPT="${INSTALL_DIR}/snippets"

# Check if installed
if [ ! -f "$WRAPPER_SCRIPT" ]; then
    echo -e "${RED}Error: snippets command not found at ${WRAPPER_SCRIPT}${NC}"
    echo "Already uninstalled or was never installed."
    exit 1
fi

# Check if we need sudo
SUDO=""
if [ ! -w "$WRAPPER_SCRIPT" ]; then
    SUDO="sudo"
    echo -e "${BLUE}Uninstallation requires sudo${NC}"
fi

echo -e "${BLUE}Removing snippets CLI from ${WRAPPER_SCRIPT}${NC}"

# Remove the wrapper script
$SUDO rm "$WRAPPER_SCRIPT"

echo -e "${GREEN}✓ Uninstallation successful!${NC}"
echo ""
echo "The 'snippets' command has been removed."
