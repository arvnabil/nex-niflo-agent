#!/bin/sh
# OpenClaw Core Sovereignty Patch Script - MASTER VERSION
# Targets: Fallback Provider, Default Identity, and Core Constants

echo "Starting Global Core Amputation..."

# 1. Core Constants Fix (The Master Source)
# Targeted replace for the discovered defaults file
find /app/dist -name "defaults-*.js" | xargs sed -i 's/const DEFAULT_PROVIDER = "openai"/const DEFAULT_PROVIDER = "ollama"/g'
find /app/dist -name "defaults-*.js" | xargs sed -i 's/const DEFAULT_MODEL = "gpt-5.4"/const DEFAULT_MODEL = "mistral:7b"/g'
echo "Phase 1: Core constants hijacked to Ollama."

# 2. General Fallback Fix
find /app/dist -type f -not -path '*/node_modules/*' | xargs sed -i 's/|| "openai"/|| "ollama"/g'
echo "Phase 2: Fallback logic redirected."

# 3. Key Identity Fix
find /app/dist -type f -not -path '*/node_modules/*' | xargs sed -i 's/provider: "openai"/provider: "ollama"/g'
echo "Phase 3: Provider identity swapped."

# 4. Explicit Model String Fix
find /app/dist -type f -not -path '*/node_modules/*' | xargs sed -i 's/openai\//ollama\//g'
find /app/dist -type f -not -path '*/node_modules/*' | xargs sed -i 's/openai-codex\//ollama\//g'
echo "Phase 4: Explicit model strings sanitized."

echo "Core Sovereignty Achieved. Nex Agent is now Locally Independent."
