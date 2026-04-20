#!/bin/sh
# OpenClaw Surgical DNA Intervention Script
# Targets: ONLY the master default constants

echo "Applying Surgical DNA Intervention..."

# 1. Master DNA Hijack (Surgical strike on the defaults file)
find /app/dist -name "defaults-*.js" | xargs sed -i 's/const DEFAULT_PROVIDER = "openai"/const DEFAULT_PROVIDER = "ollama"/g'
find /app/dist -name "defaults-*.js" | xargs sed -i 's/const DEFAULT_MODEL = "gpt-5.4"/const DEFAULT_MODEL = "mistral:7b"/g'

echo "Phase 1: Master DNA successfully hijacked to Ollama & Mistral:7b."
echo "Sovereignty Secured."
