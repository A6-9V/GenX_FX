#!/usr/bin/env python3
"""
GenX FX Multi-Cloud Deployment Execution Script
Executes the deployment plan across multiple cloud providers
"""

import asyncio
import json
import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from amp_auth import check_auth, get_user_info, get_auth_headers

class DeploymentExecutor:
    def __init__(self):
        self.project_root = Path.cwd()
        self.deployment_log = []
        self.current_phase = 0
        self.total_phases = 5
        
    def log(self, message: str, level: str = "INFO"):
        """Log deployment messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
        
    def check_amp_auth(self) -> bool:
        """Check AMP authentication"""
        if not check_auth():
            self.log("❌ AMP authentication failed. Please authenticate first.", "ERROR")
            return False
        
        user_info = get_user_info()
        self.log(f"✅ AMP Authentication successful - User: {user_info.get('user_id', 'Unknown')}")
        return True
    
    def phase_header(self, phase: int, title: str):
        """Print phase header"""
        self.current_phase = phase
        print(f"\n{'='*60}")
        print(f"🚀 PHASE {phase}/{self.total_phases}: {title}")
        print(f"{'='*60}")
        
    async def phase_1_railway_backend(self):
        """Phase 1: Deploy Backend API to Railway"""
        self.phase_header(1, "Railway Backend API Deployment")
        
        try:
            # Check if Railway CLI is installed
            self.log("Checking Railway CLI installation...")
            try:
                result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
                if result.returncode != 0:
                    self.log("⚠️  Railway CLI not found - will create configuration files only")
                    self.log("📝 To install Railway CLI: npm install -g @railway/cli")
            except FileNotFoundError:
                self.log("⚠️  Railway CLI not found - will create configuration files only")
                self.log("📝 To install Railway CLI: npm install -g @railway/cli")
            
            # Create Railway configuration
            self.log("Creating Railway configuration...")
            railway_config = {
                "$schema": "https://railway.app/railway.schema.json",
                "build": {
                    "builder": "DOCKERFILE",
                    "dockerfilePath": "Dockerfile.railway"
                },
                "deploy": {
                    "startCommand": "python main.py",
                    "healthcheckPath": "/health",
                    "healthcheckTimeout": 300,
                    "restartPolicyType": "ON_FAILURE",
                    "restartPolicyMaxRetries": 10
                }
            }
            
            with open("railway.json", "w") as f:
                json.dump(railway_config, f, indent=2)
            
            self.log("✅ Railway configuration created")
            
            # Create environment variables template
            env_template = """# Railway Environment Variables
# Copy this to your Railway project environment variables

# Database Configuration
DATABASE_URL=postgresql://your_supabase_url
REDIS_URL=redis://your_redis_url

# API Keys
API_KEY=your_api_key
FXCM_API_KEY=your_fxcm_api_key
FXCM_SECRET_KEY=your_fxcm_secret_key

# AI/ML Configuration
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Trading Configuration
BROKER=exness
TRADING_MODE=live
RISK_PERCENTAGE=2.0

# System Configuration
LOG_LEVEL=INFO
DEBUG=false
"""
            
            with open("railway.env.template", "w") as f:
                f.write(env_template)
            
            self.log("✅ Railway environment template created")
            self.log("✅ Phase 1 completed - Railway backend ready for deployment")
            
        except Exception as e:
            self.log(f"❌ Phase 1 failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    async def phase_2_supabase_database(self):
        """Phase 2: Set up Supabase Database"""
        self.phase_header(2, "Supabase Database Setup")
        
        try:
            # Create database schema
            self.log("Creating database schema...")
            
            schema_sql = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Trading signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    entry_price DECIMAL(10,5),
    stop_loss DECIMAL(10,5),
    take_profit DECIMAL(10,5),
    confidence DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_trades INTEGER,
    win_rate DECIMAL(5,4),
    profit_loss DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI model predictions table
CREATE TABLE IF NOT EXISTS ai_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    prediction_type TEXT NOT NULL,
    confidence DECIMAL(5,4),
    prediction_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
"""
            
            with open("database/schema.sql", "w") as f:
                f.write(schema_sql)
            
            self.log("✅ Database schema created")
            
            # Create Supabase configuration
            supabase_config = {
                "project_url": "YOUR_SUPABASE_PROJECT_URL",
                "anon_key": "YOUR_SUPABASE_ANON_KEY",
                "service_role_key": "YOUR_SUPABASE_SERVICE_ROLE_KEY"
            }
            
            with open("supabase_config.json", "w") as f:
                json.dump(supabase_config, f, indent=2)
            
            self.log("✅ Supabase configuration created")
            self.log("⚠️  Please update supabase_config.json with your actual Supabase credentials")
            
        except Exception as e:
            self.log(f"❌ Phase 2 failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    async def phase_3_oracle_cloud_ai(self):
        """Phase 3: Deploy AI/ML Processing to Oracle Cloud"""
        self.phase_header(3, "Oracle Cloud AI/ML Processing")
        
        try:
            # Create Oracle Cloud deployment files
            self.log("Creating Oracle Cloud deployment files...")
            
            # Make deployment script executable
            subprocess.run(["chmod", "+x", "oracle-deploy.sh"])
            
            # Create Oracle Cloud instance configuration
            oracle_config = {
                "instance_type": "VM.Standard.A1.Flex",
                "ocpus": 2,
                "memory_in_gbs": 12,
                "os": "Canonical Ubuntu 20.04",
                "services": [
                    "ai-processor",
                    "model-server", 
                    "backtester",
                    "redis"
                ]
            }
            
            with open("oracle_config.json", "w") as f:
                json.dump(oracle_config, f, indent=2)
            
            self.log("✅ Oracle Cloud configuration created")
            self.log("⚠️  Please run: ./oracle-deploy.sh on your Oracle Cloud instance")
            
        except Exception as e:
            self.log(f"❌ Phase 3 failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    async def phase_4_google_cloud_signals(self):
        """Phase 4: Deploy Signal Processing to Google Cloud Run"""
        self.phase_header(4, "Google Cloud Run Signal Processing")
        
        try:
            # Update cloudbuild.yaml for signal processing
            self.log("Updating Google Cloud Build configuration...")
            
            gcp_config = {
                "project_id": "YOUR_GCP_PROJECT_ID",
                "region": "us-central1",
                "service_name": "genx-signals",
                "memory": "1Gi",
                "cpu": "1",
                "timeout": "3600",
                "concurrency": "80"
            }
            
            with open("gcp_config.json", "w") as f:
                json.dump(gcp_config, f, indent=2)
            
            self.log("✅ Google Cloud configuration created")
            self.log("⚠️  Please update gcp_config.json with your actual GCP project details")
            
        except Exception as e:
            self.log(f"❌ Phase 4 failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    async def phase_5_vercel_frontend(self):
        """Phase 5: Deploy Frontend to Vercel"""
        self.phase_header(5, "Vercel Frontend Deployment")
        
        try:
            # Create Vercel configuration
            self.log("Creating Vercel configuration...")
            
            vercel_config = {
                "version": 2,
                "builds": [
                    {
                        "src": "client/package.json",
                        "use": "@vercel/static-build"
                    }
                ],
                "routes": [
                    {
                        "src": "/(.*)",
                        "dest": "/client/$1"
                    }
                ]
            }
            
            with open("vercel.json", "w") as f:
                json.dump(vercel_config, f, indent=2)
            
            self.log("✅ Vercel configuration created")
            
            # Create deployment summary
            self.create_deployment_summary()
            
        except Exception as e:
            self.log(f"❌ Phase 5 failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    def create_deployment_summary(self):
        """Create deployment summary"""
        self.log("Creating deployment summary...")
        
        summary = {
            "deployment_date": datetime.now().isoformat(),
            "amp_user": get_user_info().get("user_id"),
            "phases_completed": self.current_phase,
            "total_phases": self.total_phases,
            "services": {
                "backend": {
                    "provider": "Railway",
                    "cost": "$5/month",
                    "status": "configured",
                    "files": ["railway.json", "Dockerfile.railway"]
                },
                "database": {
                    "provider": "Supabase", 
                    "cost": "FREE",
                    "status": "configured",
                    "files": ["database/schema.sql", "supabase_config.json"]
                },
                "ai_processing": {
                    "provider": "Oracle Cloud",
                    "cost": "FREE",
                    "status": "configured", 
                    "files": ["docker-compose.oracle.yml", "oracle-deploy.sh", "oracle_config.json"]
                },
                "signal_processing": {
                    "provider": "Google Cloud Run",
                    "cost": "$1-5/month",
                    "status": "configured",
                    "files": ["cloudbuild.yaml", "Dockerfile.gcp", "gcp_config.json"]
                },
                "frontend": {
                    "provider": "Vercel",
                    "cost": "FREE", 
                    "status": "configured",
                    "files": ["vercel.json"]
                }
            },
            "total_monthly_cost": "$6-10",
            "next_steps": [
                "1. Set up Oracle Cloud account and create VM instance",
                "2. Update supabase_config.json with your Supabase credentials",
                "3. Update gcp_config.json with your GCP project details",
                "4. Run ./oracle-deploy.sh on your Oracle Cloud instance",
                "5. Deploy to Railway: railway up",
                "6. Deploy to Google Cloud: gcloud builds submit",
                "7. Deploy to Vercel: vercel --prod"
            ]
        }
        
        with open("deployment_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        self.log("✅ Deployment summary created: deployment_summary.json")
    
    async def execute_full_deployment(self):
        """Execute the complete deployment plan"""
        print("🚀 GenX FX Multi-Cloud Deployment Execution")
        print("=" * 60)
        
        # Check AMP authentication
        if not self.check_amp_auth():
            return False
        
        # Execute all phases
        phases = [
            self.phase_1_railway_backend,
            self.phase_2_supabase_database,
            self.phase_3_oracle_cloud_ai,
            self.phase_4_google_cloud_signals,
            self.phase_5_vercel_frontend
        ]
        
        for i, phase in enumerate(phases, 1):
            success = await phase()
            if not success:
                self.log(f"❌ Deployment failed at phase {i}", "ERROR")
                return False
        
        # Final summary
        print(f"\n{'='*60}")
        print("🎉 DEPLOYMENT EXECUTION COMPLETED!")
        print(f"{'='*60}")
        print(f"✅ All {self.total_phases} phases completed successfully")
        print(f"📊 Total monthly cost: $6-10")
        print(f"📁 Configuration files created")
        print(f"📋 Check deployment_summary.json for next steps")
        
        return True

async def main():
    """Main execution function"""
    executor = DeploymentExecutor()
    await executor.execute_full_deployment()

if __name__ == "__main__":
    asyncio.run(main())