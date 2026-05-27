#!/bin/bash
cd "$(dirname "$0")"
echo ""
echo " ========================================"
echo "   Book Machine Server"
echo " ========================================"
echo ""

if ! command -v node &>/dev/null; then
  echo " ERROR: Node.js is not installed."
  echo " Download it from https://nodejs.org (LTS version)"
  echo ""
  exit 1
fi

if [ ! -d "node_modules/@anthropic-ai" ]; then
  echo " Installing dependencies (first run only)..."
  echo ""
  npm install
  echo ""
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo " No ANTHROPIC_API_KEY found in your environment."
  echo " Get your key at: https://console.anthropic.com/settings/api-keys"
  echo ""
  read -rsp " Paste your Anthropic API key: " ANTHROPIC_API_KEY
  export ANTHROPIC_API_KEY
  echo ""
  echo ""
fi

echo " Starting server..."
echo ""
node book-machine-server.js
