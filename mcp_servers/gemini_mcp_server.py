#!/usr/bin/env python3
"""Gemini MCP Server for GenX FX Trading System"""
import asyncio
import json
import logging
from typing import Dict, Any
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class GeminiMCPServer:
    def __init__(self, port: int = 8081):
        self.port = port
        self.gemini_service = None
        self.running = False
        
    async def initialize(self):
        try:
            self.gemini_service = GeminiService()
            await self.gemini_service.initialize()
            logger.info("Gemini MCP Server initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method", "")
        params = request.get("params", {})
        
        if method == "analyze_sentiment":
            text_data = params.get("text_data", [])
            result = await self.gemini_service.analyze_market_sentiment(text_data)
            return {"method": method, "result": result, "timestamp": datetime.now().isoformat()}
        elif method == "generate_signals":
            market_data = params.get("market_data", {})
            news_data = params.get("news_data", [])
            result = await self.gemini_service.analyze_trading_signals(market_data, news_data)
            return {"method": method, "result": result, "timestamp": datetime.now().isoformat()}
        elif method == "health_check":
            healthy = await self.gemini_service.health_check()
            return {"method": method, "result": {"status": "healthy" if healthy else "unhealthy"}}
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
        logger.info(f"Gemini MCP Server started on port {self.port}")
        
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
        return web.json_response({"status": "healthy", "service": "gemini"})
    
    async def stop_server(self):
        self.running = False

async def main():
    logging.basicConfig(level=logging.INFO)
    server = GeminiMCPServer()
    
    try:
        if await server.initialize():
            await server.start_server()
    except KeyboardInterrupt:
        await server.stop_server()

if __name__ == "__main__":
    asyncio.run(main())