#!/usr/bin/env python3
"""
AI Analyzer Plugin for GenX CLI
Provides AI-powered analysis and insights for the trading system
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalyzerPlugin:
    def __init__(self):
        self.name = "ai_analyzer"
        self.description = "AI-powered trading analysis and insights"
        self.version = "1.0.0"
        self.project_root = Path.cwd()
        
    def load_config(self):
        """Load configuration from amp_config.json"""
        config_path = self.project_root / "amp_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in amp_config.json")
                return {}
        return {}
    
    def analyze_trading_data(self):
        """Analyze trading data and provide insights"""
        print("🤖 AI Analyzer - Trading Data Analysis")
        print("=" * 50)
        
        # Check for signal output files
        signal_dir = self.project_root / "signal_output"
        if signal_dir.exists():
            signal_files = list(signal_dir.glob("*.csv"))
            if signal_files:
                print(f"📊 Found {len(signal_files)} signal files")
                
                # Analyze the most recent file
                latest_file = max(signal_files, key=lambda x: x.stat().st_mtime)
                print(f"📈 Latest signals: {latest_file.name}")
                
                try:
                    with open(latest_file, 'r') as f:
                        lines = f.readlines()
                        if len(lines) > 1:  # Has data beyond header
                            print(f"   Signals count: {len(lines) - 1}")
                            
                            # Simple analysis
                            if len(lines) > 10:
                                print("   📊 Signal volume: High")
                            elif len(lines) > 5:
                                print("   📊 Signal volume: Medium")
                            else:
                                print("   📊 Signal volume: Low")
                        else:
                            print("   📊 No signals found")
                except Exception as e:
                    print(f"   ❌ Error reading file: {e}")
            else:
                print("📊 No signal files found")
        else:
            print("📊 Signal output directory not found")
    
    def check_ai_models(self):
        """Check AI models and their status"""
        print("\n🧠 AI Models Status")
        print("-" * 30)
        
        # Check for AI model files
        ai_dirs = ["ai_models", "models", "ml_models"]
        models_found = False
        
        for dir_name in ai_dirs:
            ai_dir = self.project_root / dir_name
            if ai_dir.exists():
                model_files = list(ai_dir.glob("*.pkl")) + list(ai_dir.glob("*.h5")) + list(ai_dir.glob("*.joblib"))
                if model_files:
                    print(f"✅ {dir_name}: {len(model_files)} models found")
                    for model in model_files[:3]:  # Show first 3
                        print(f"   - {model.name}")
                    models_found = True
                else:
                    print(f"⚠️  {dir_name}: Directory exists but no models found")
        
        if not models_found:
            print("❌ No AI models found in common directories")
    
    def analyze_performance(self):
        """Analyze system performance metrics"""
        print("\n⚡ Performance Analysis")
        print("-" * 30)
        
        # Check log files for performance metrics
        logs_dir = self.project_root / "logs"
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            if log_files:
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                print(f"📋 Latest log: {latest_log.name}")
                
                # Check log file size
                size_mb = latest_log.stat().st_size / (1024 * 1024)
                print(f"   Size: {size_mb:.2f} MB")
                
                # Check if log is growing (indicates active system)
                if size_mb > 1:
                    print("   📈 Log activity: High (system appears active)")
                elif size_mb > 0.1:
                    print("   📈 Log activity: Medium")
                else:
                    print("   📈 Log activity: Low")
            else:
                print("📋 No log files found")
        else:
            print("📋 Logs directory not found")
    
    def generate_report(self):
        """Generate comprehensive AI analysis report"""
        print("\n📋 Generating AI Analysis Report...")
        print("=" * 50)
        
        config = self.load_config()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "plugin": self.name,
            "version": self.version,
            "analysis": {}
        }
        
        # Collect analysis data
        try:
            # Trading data analysis
            signal_dir = self.project_root / "signal_output"
            if signal_dir.exists():
                signal_files = list(signal_dir.glob("*.csv"))
                report["analysis"]["signals"] = {
                    "count": len(signal_files),
                    "latest": signal_files[0].name if signal_files else None
                }
            
            # AI models
            ai_models = []
            for dir_name in ["ai_models", "models", "ml_models"]:
                ai_dir = self.project_root / dir_name
                if ai_dir.exists():
                    models = list(ai_dir.glob("*.pkl")) + list(ai_dir.glob("*.h5"))
                    ai_models.extend([str(m) for m in models])
            
            report["analysis"]["ai_models"] = ai_models
            
            # System health
            logs_dir = self.project_root / "logs"
            if logs_dir.exists():
                log_files = list(logs_dir.glob("*.log"))
                report["analysis"]["logs"] = {
                    "count": len(log_files),
                    "total_size_mb": sum(f.stat().st_size for f in log_files) / (1024 * 1024)
                }
            
            # Save report
            report_path = self.project_root / "ai_analysis_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"✅ Report generated: {report_path}")
            print(f"📊 Analysis completed at: {report['timestamp']}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def show_help(self):
        """Show plugin help information"""
        help_text = f"""
🤖 AI Analyzer Plugin v{self.version}

Commands:
  analyze          - Analyze trading data and AI models
  models           - Check AI models status
  performance      - Analyze system performance
  report           - Generate comprehensive analysis report
  help             - Show this help message

Examples:
  genx-cli --run-plugin ai_analyzer.py analyze
  genx-cli --run-plugin ai_analyzer.py models
  genx-cli --run-plugin ai_analyzer.py report

Description: {self.description}
        """
        print(help_text)
    
    def run(self, command="help"):
        """Main plugin entry point"""
        try:
            if command == "analyze":
                self.analyze_trading_data()
                self.check_ai_models()
            elif command == "models":
                self.check_ai_models()
            elif command == "performance":
                self.analyze_performance()
            elif command == "report":
                self.generate_report()
            elif command == "help":
                self.show_help()
            else:
                print(f"❌ Unknown command: {command}")
                self.show_help()
                
        except Exception as e:
            logger.error(f"Plugin error: {e}")
            print(f"❌ Plugin error: {e}")

def main():
    """Main function for direct execution"""
    plugin = AIAnalyzerPlugin()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "help"
    
    plugin.run(command)

if __name__ == "__main__":
    main()