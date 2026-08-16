#!/bin/bash
set -e

echo "=================================================="
echo "🌾 ADTC Agri-Assistant Offline Verification Test"
echo "=================================================="

if [ ! -f "./dist/agri_assistant" ]; then
    echo "❌ Binary ./dist/agri_assistant not found! Building first..."
    pyinstaller --clean --noconfirm agri_assistant.spec
fi

echo "1. Running Executable Test Query via Pipe..."
echo -e "best weather to plant cassava\nexit" | ./dist/agri_assistant

echo ""
echo "=================================================="
echo "✅ SUCCESS: Agri-Assistant executed successfully!"
echo "=================================================="
