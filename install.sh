#!/usr/bin/env bash
# Install GAD (Get Analysis Done) for use with Claude Code
#
# This script:
# 1. Installs the gad Python package in editable mode
# 2. Links the GAD workflow engine to ~/.claude/get-analysis-done/
# 3. Links the slash commands to ~/.claude/commands/gad/
#
# Usage: ./install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Get Analysis Done (GAD)..."
echo ""

# 1. Install Python package
echo "→ Installing gad Python package..."
pip install -e "$SCRIPT_DIR" 2>&1 | tail -1
echo ""

# 2. Link workflow engine
GAD_ENGINE="$HOME/.claude/get-analysis-done"
if [ -L "$GAD_ENGINE" ]; then
    echo "→ Updating existing symlink: $GAD_ENGINE"
    rm "$GAD_ENGINE"
elif [ -d "$GAD_ENGINE" ]; then
    echo "→ WARNING: $GAD_ENGINE already exists as a directory."
    echo "  Back it up and re-run, or remove it manually."
    exit 1
fi
mkdir -p "$HOME/.claude"
ln -s "$SCRIPT_DIR/.gad" "$GAD_ENGINE"
echo "→ Linked workflow engine: $GAD_ENGINE -> $SCRIPT_DIR/.gad"
echo ""

# 3. Link slash commands
COMMANDS_DIR="$HOME/.claude/commands/gad"
if [ -L "$COMMANDS_DIR" ]; then
    echo "→ Updating existing symlink: $COMMANDS_DIR"
    rm "$COMMANDS_DIR"
elif [ -d "$COMMANDS_DIR" ]; then
    echo "→ WARNING: $COMMANDS_DIR already exists as a directory."
    echo "  Back it up and re-run, or remove it manually."
    exit 1
fi
mkdir -p "$HOME/.claude/commands"
ln -s "$SCRIPT_DIR/commands" "$COMMANDS_DIR"
echo "→ Linked slash commands: $COMMANDS_DIR -> $SCRIPT_DIR/commands"
echo ""

echo "Done! GAD is ready to use."
echo ""
echo "Available commands in Claude Code:"
echo "  /gad:run-analysis    — Run full analysis from physics prompt"
echo "  /gad:run-wave N      — Run a specific wave"
echo "  /gad:help            — Show all GAD commands"
