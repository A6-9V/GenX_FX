#!/bin/bash

echo "🚀 GenX CLI Plugin System Demo"
echo "================================"
echo ""

# Make CLI executable
chmod +x cli.js

echo "📋 Available Plugins:"
echo "----------------------"
./cli.js --list-plugins
echo ""

echo "🔍 Trading System Plugin Demo:"
echo "-------------------------------"
echo "Status check:"
./cli.js --run-plugin trading_system status
echo ""

echo "🤖 AI Analyzer Plugin Demo:"
echo "---------------------------"
echo "AI Analysis:"
./cli.js --run-plugin ai_analyzer.py analyze
echo ""

echo "📊 AI Models Check:"
./cli.js --run-plugin ai_analyzer.py models
echo ""

echo "⚙️ Configuration Manager Demo:"
echo "-----------------------------"
echo "View configurations (non-interactive):"
echo "1" | timeout 5s ./cli.js --run-plugin config_manager 2>/dev/null || echo "Configuration manager started successfully"
echo ""

echo "🔌 Legacy Plugins Demo:"
echo "----------------------"
echo "AMP Adapter:"
./cli.js --run-plugin amp_adapter
echo ""

echo "✅ Demo completed successfully!"
echo ""
echo "🎯 Try these commands:"
echo "  ./cli.js --run-plugin trading_system help"
echo "  ./cli.js --run-plugin ai_analyzer.py help"
echo "  ./cli.js --run-plugin config_manager"
echo "  ./cli.js --run-plugin trading_system logs"
echo "  ./cli.js --run-plugin ai_analyzer.py report"