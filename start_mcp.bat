@echo off
echo Starting GenX FX MCP Servers...
start "Gemini MCP" python mcp_servers/gemini_mcp_server.py
start "Jules MCP" python mcp_servers/jules_mcp_server.py
echo MCP Servers started on ports 8081 and 8082