#!/bin/sh
# OpenClaw Protocol Identity Restoration Script
# Targets: Restore all internal labels and keys to original state

echo "Restoring global protocol identity..."

# 1. Identity Revert (Fixes JSON handling and internal routing)
find /app/dist -type f -not -path '*/node_modules/*' | xargs sed -i 's/ollama/openai/g'

echo "Identity Restored. System is now ready for surgical DNA replacement."
