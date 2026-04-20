#!/bin/sh
# OpenClaw Core integrity Recovery Script
# Targets: Restore mangled internal paths

echo "Reverting aggressive patching to restore system integrity..."

# 1. Restore Provider Prefixes (Fixes JSON & Path Mangling)
find /app/dist -type f -not -path '*/node_modules/*' | xargs sed -i 's/ollama\//openai\//g'
echo "Phase 1: Internal paths restored to OpenAI defaults."

echo "Integracy Restored. System is now ready for surgical DNA intervention."
