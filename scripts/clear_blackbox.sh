#!/bin/bash
# clear_blackbox.sh
# Script to wipe Blackbox AI history and restart VSCode fresh

# Kill any running VSCode processes
pkill -f "Visual Studio Code"

# Remove Blackbox AI cache/history
rm -rf ~/.blackboxai

# Optional: remove VSCode cached extension storage
rm -rf ~/Library/Application\ Support/Code/User/globalStorage/blackboxapp.blackbox

echo "✅ Blackbox AI history cleared. Restart VSCode to use a fresh session."
