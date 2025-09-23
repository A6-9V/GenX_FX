#!/usr/bin/env python3
"""
GenX FX Trading System - Simplified Main Entry Point
For testing Google Cloud Build deployment
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
import signal
import json
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleGenXTradingSystem:
    """Simplified GenX Trading System for testing"""
    
    def __init__(self):
        self.is_running = False
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Simple GenX Trading System initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.is_running = False
    
    async def run_live_trading(self):
        """Run live trading signal generation"""
        logger.info("🚀 Starting Simple Live Trading Mode")
        
        try:
            self.is_running = True
            
            logger.info("✅ Simple live trading started successfully")
            logger.info("📊 This is a test deployment for Google Cloud Build")
            
            # Keep running until shutdown
            while self.is_running:
                await asyncio.sleep(5)
                logger.info("System running... Press Ctrl+C to stop")
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error in live trading mode: {e}")
        finally:
            logger.info("Live trading stopped")
    
    def print_system_info(self):
        """Print system information"""
        logger.info("=== GenX FX Trading System ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Environment: {os.environ.get('AMP_ENV', 'development')}")
        logger.info("================================")

async def main():
    """Main entry point"""
    logger.info("Starting GenX FX Trading System...")
    
    # Create and run the trading system
    trading_system = SimpleGenXTradingSystem()
    trading_system.print_system_info()
    
    # Run live trading
    await trading_system.run_live_trading()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)