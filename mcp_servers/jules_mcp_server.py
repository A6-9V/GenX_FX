#!/usr/bin/env python3
"""Jules MCP Server for GenX FX Trading System"""
import asyncio
import json
import logging
from typing import Dict, Any
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jules_cli import JulesWorkspace

logger = logging.getLogger(__name__)

class JulesMCPServer:
    def __init__(self, port: int = 8082):
        self.port = port
        self.jules_workspace = None
        self.running = False
        
    async def initialize(self):
        try:
            self.jules_workspace = JulesWorkspace()
            logger.info("Jules MCP Server initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method", "")
        params = request.get("params", {})
        
        if method == "execute_task":
            task_name = params.get("task", "")
            task_args = params.get("args", [])
            success = self.jules_workspace.execute_task(task_name, task_args)
            return {"method": method, "result": {"success": success}}
        elif method == "manage_secrets":
            action = params.get("action", "list")
            if action == "list":
                secrets_file = self.jules_workspace.secrets_dir / "secrets.json"
                if secrets_file.exists():
                    with open(secrets_file, "r") as f:
                        secrets = json.load(f)
                    return {"method": method, "result": {"secrets": list(secrets.keys())}}
                return {"method": method, "result": {"secrets": []}}
        elif method == "health_check":
            workspace_exists = (self.jules_workspace.project_root / '.jules').exists()
            return {"method": method, "result": {"status": "healthy" if workspace_exists else "unhealthy"}}
        else:
            return {"error": f"Unknown method: {method}"}
    
    async def start_server(self):
        from aiohttp import web, web_runner
        
        app = web.Application()
        app.router.add_post('/mcp', self._handle_http_request)
        app.router.add_get('/health', self._handle_health)
        
        runner = web_runner.AppRunner(app)
        await runner.setup()
        
        site = web_runner.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        self.running = True
        logger.info(f"Jules MCP Server started on port {self.port}")
        
        while self.running:
            await asyncio.sleep(1)
    
    async def _handle_http_request(self, request):
        try:
            data = await request.json()
            response = await self.handle_request(data)
            return web.json_response(response)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_health(self, request):
        return web.json_response({"status": "healthy", "service": "jules"})
    
    async def stop_server(self):
        self.running = False

async def main():
    logging.basicConfig(level=logging.INFO)
    server = JulesMCPServer()
    
    try:
        if await server.initialize():
            await server.start_server()
    except KeyboardInterrupt:
        await server.stop_server()

if __name__ == "__main__":
    asyncio.run(main())