#!/usr/bin/env python3
"""
GenX FX Deployment Verification Script
Run this on your laptop to verify deployment status and configuration
"""

import os
import sys
import json
import subprocess
import requests
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class DeploymentVerifier:
    def __init__(self):
        self.project_root = Path.cwd()
        self.verification_results = []
        self.current_check = 0
        self.total_checks = 0
        
    def log(self, message: str, status: str = "INFO"):
        """Log verification messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{status}] {message}"
        self.verification_results.append(log_entry)
        print(log_entry)
        
    def check_header(self, check: int, title: str):
        """Print check header"""
        self.current_check = check
        print(f"\n{'='*60}")
        print(f"🔍 CHECK {check}: {title}")
        print(f"{'='*60}")
        
    def check_system_info(self):
        """Check 1: System Information"""
        self.check_header(1, "System Information")
        
        try:
            # Get system information
            system_info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": sys.version,
                "current_directory": str(self.project_root),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log(f"✅ System: {system_info['platform']} {system_info['platform_version']}")
            self.log(f"✅ Architecture: {system_info['architecture']}")
            self.log(f"✅ Python: {system_info['python_version'].split()[0]}")
            self.log(f"✅ Working Directory: {system_info['current_directory']}")
            
            # Save system info
            with open("system_info.json", "w") as f:
                json.dump(system_info, f, indent=2)
            
            self.log("✅ System information saved to system_info.json")
            
        except Exception as e:
            self.log(f"❌ System info check failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    def check_amp_authentication(self):
        """Check 2: AMP Authentication"""
        self.check_header(2, "AMP Authentication")
        
        try:
            # Check if AMP auth files exist
            auth_file = self.project_root / "amp_auth.json"
            if auth_file.exists():
                with open(auth_file, 'r') as f:
                    auth_data = json.load(f)
                
                user_id = auth_data.get("user_id", "Unknown")
                expires_at = auth_data.get("expires_at", "Unknown")
                
                self.log(f"✅ AMP Authentication found")
                self.log(f"✅ User ID: {user_id}")
                self.log(f"✅ Expires: {expires_at}")
                
                # Check if session is still valid
                from datetime import datetime
                if expires_at != "Unknown":
                    expires = datetime.fromisoformat(expires_at)
                    if datetime.now() < expires:
                        self.log("✅ Session is valid")
                    else:
                        self.log("⚠️ Session has expired", "WARNING")
                
            else:
                self.log("❌ AMP authentication file not found", "ERROR")
                self.log("💡 Run: python3 -c \"from amp_auth import authenticate_user; authenticate_user('YOUR_TOKEN')\"")
                return False
                
        except Exception as e:
            self.log(f"❌ AMP authentication check failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    def check_deployment_files(self):
        """Check 3: Deployment Configuration Files"""
        self.check_header(3, "Deployment Configuration Files")
        
        required_files = {
            "Railway Backend": ["railway.json", "Dockerfile.railway", "railway.env.template"],
            "Supabase Database": ["database/schema.sql", "supabase_config.json"],
            "Oracle Cloud": ["docker-compose.oracle.yml", "oracle-deploy.sh", "oracle_config.json"],
            "Google Cloud": ["cloudbuild.yaml", "Dockerfile.gcp", "gcp_config.json"],
            "Vercel Frontend": ["vercel.json"],
            "Deployment Summary": ["deployment_summary.json"]
        }
        
        all_files_exist = True
        
        for service, files in required_files.items():
            self.log(f"\n📁 Checking {service} files:")
            service_ok = True
            
            for file in files:
                file_path = self.project_root / file
                if file_path.exists():
                    self.log(f"  ✅ {file}")
                else:
                    self.log(f"  ❌ {file} - MISSING", "ERROR")
                    service_ok = False
                    all_files_exist = False
            
            if service_ok:
                self.log(f"  ✅ {service} - All files present")
            else:
                self.log(f"  ❌ {service} - Missing files", "ERROR")
        
        return all_files_exist
    
    def check_docker_installation(self):
        """Check 4: Docker Installation"""
        self.check_header(4, "Docker Installation")
        
        try:
            # Check Docker
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✅ Docker: {result.stdout.strip()}")
            else:
                self.log("❌ Docker not found", "ERROR")
                self.log("💡 Install Docker: https://docs.docker.com/get-docker/")
                return False
            
            # Check Docker Compose
            result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✅ Docker Compose: {result.stdout.strip()}")
            else:
                self.log("❌ Docker Compose not found", "ERROR")
                self.log("💡 Install Docker Compose: https://docs.docker.com/compose/install/")
                return False
            
            # Test Docker functionality
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Docker daemon is running")
            else:
                self.log("❌ Docker daemon not running", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Docker check failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    def check_cli_tools(self):
        """Check 5: CLI Tools Installation"""
        self.check_header(5, "CLI Tools Installation")
        
        cli_tools = {
            "Railway CLI": ["railway", "--version"],
            "Google Cloud CLI": ["gcloud", "--version"],
            "Vercel CLI": ["vercel", "--version"],
            "Node.js": ["node", "--version"],
            "npm": ["npm", "--version"]
        }
        
        all_tools_available = True
        
        for tool_name, command in cli_tools.items():
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.log(f"✅ {tool_name}: {version}")
                else:
                    self.log(f"❌ {tool_name} not found", "ERROR")
                    all_tools_available = False
            except FileNotFoundError:
                self.log(f"❌ {tool_name} not found", "ERROR")
                all_tools_available = False
        
        if not all_tools_available:
            self.log("\n💡 Installation commands:")
            self.log("  Railway CLI: npm install -g @railway/cli")
            self.log("  Google Cloud CLI: curl https://sdk.cloud.google.com | bash")
            self.log("  Vercel CLI: npm install -g vercel")
            self.log("  Node.js: https://nodejs.org/")
        
        return all_tools_available
    
    def check_python_dependencies(self):
        """Check 6: Python Dependencies"""
        self.check_header(6, "Python Dependencies")
        
        try:
            # Check if requirements.txt exists
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                self.log("❌ requirements.txt not found", "ERROR")
                return False
            
            self.log("✅ requirements.txt found")
            
            # Check key dependencies
            key_dependencies = [
                "requests", "numpy", "pandas", "scikit-learn", 
                "asyncio", "aiohttp", "websockets"
            ]
            
            missing_deps = []
            for dep in key_dependencies:
                try:
                    __import__(dep)
                    self.log(f"✅ {dep}")
                except ImportError:
                    self.log(f"❌ {dep} - MISSING", "ERROR")
                    missing_deps.append(dep)
            
            if missing_deps:
                self.log(f"\n💡 Install missing dependencies:")
                self.log(f"  pip install {' '.join(missing_deps)}")
                return False
            
            self.log("✅ All key dependencies available")
            
        except Exception as e:
            self.log(f"❌ Python dependencies check failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    def check_network_connectivity(self):
        """Check 7: Network Connectivity"""
        self.check_header(7, "Network Connectivity")
        
        services = {
            "GitHub": "https://api.github.com",
            "Railway": "https://railway.app",
            "Supabase": "https://supabase.com",
            "Oracle Cloud": "https://cloud.oracle.com",
            "Google Cloud": "https://cloud.google.com",
            "Vercel": "https://vercel.com"
        }
        
        all_connected = True
        
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log(f"✅ {service_name}: Connected")
                else:
                    self.log(f"⚠️ {service_name}: Status {response.status_code}", "WARNING")
            except requests.exceptions.RequestException as e:
                self.log(f"❌ {service_name}: Connection failed - {str(e)}", "ERROR")
                all_connected = False
        
        return all_connected
    
    def check_deployment_summary(self):
        """Check 8: Deployment Summary"""
        self.check_header(8, "Deployment Summary")
        
        try:
            summary_file = self.project_root / "deployment_summary.json"
            if not summary_file.exists():
                self.log("❌ deployment_summary.json not found", "ERROR")
                return False
            
            with open(summary_file, 'r') as f:
                summary = json.load(f)
            
            self.log(f"✅ Deployment Date: {summary.get('deployment_date', 'Unknown')}")
            self.log(f"✅ AMP User: {summary.get('amp_user', 'Unknown')}")
            self.log(f"✅ Phases Completed: {summary.get('phases_completed', 0)}/{summary.get('total_phases', 0)}")
            self.log(f"✅ Total Monthly Cost: {summary.get('total_monthly_cost', 'Unknown')}")
            
            # Check services
            services = summary.get('services', {})
            for service_name, service_info in services.items():
                status = service_info.get('status', 'Unknown')
                cost = service_info.get('cost', 'Unknown')
                provider = service_info.get('provider', 'Unknown')
                
                if status == 'configured':
                    self.log(f"✅ {service_name} ({provider}): {cost} - {status}")
                else:
                    self.log(f"❌ {service_name} ({provider}): {status}", "ERROR")
            
            # Show next steps
            next_steps = summary.get('next_steps', [])
            if next_steps:
                self.log("\n📋 Next Steps:")
                for i, step in enumerate(next_steps, 1):
                    self.log(f"  {i}. {step}")
            
        except Exception as e:
            self.log(f"❌ Deployment summary check failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    def generate_verification_report(self):
        """Generate verification report"""
        self.log("\n📊 Generating verification report...")
        
        report = {
            "verification_date": datetime.now().isoformat(),
            "system_info": {},
            "checks_passed": 0,
            "checks_failed": 0,
            "total_checks": 8,
            "results": self.verification_results,
            "recommendations": []
        }
        
        # Count passed/failed checks
        for result in self.verification_results:
            if "✅" in result:
                report["checks_passed"] += 1
            elif "❌" in result:
                report["checks_failed"] += 1
        
        # Add recommendations
        if report["checks_failed"] > 0:
            report["recommendations"].append("Fix failed checks before deployment")
        if report["checks_passed"] >= 6:
            report["recommendations"].append("System is ready for deployment")
        else:
            report["recommendations"].append("Complete missing configurations before deployment")
        
        # Save report
        with open("verification_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        self.log("✅ Verification report saved to verification_report.json")
        
        return report
    
    def run_all_checks(self):
        """Run all verification checks"""
        print("🔍 GenX FX Deployment Verification")
        print("=" * 60)
        print("Running comprehensive verification checks...")
        
        checks = [
            self.check_system_info,
            self.check_amp_authentication,
            self.check_deployment_files,
            self.check_docker_installation,
            self.check_cli_tools,
            self.check_python_dependencies,
            self.check_network_connectivity,
            self.check_deployment_summary
        ]
        
        passed_checks = 0
        total_checks = len(checks)
        
        for i, check in enumerate(checks, 1):
            try:
                if check():
                    passed_checks += 1
            except Exception as e:
                self.log(f"❌ Check {i} failed with exception: {str(e)}", "ERROR")
        
        # Final summary
        print(f"\n{'='*60}")
        print("📊 VERIFICATION SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Passed: {passed_checks}/{total_checks}")
        print(f"❌ Failed: {total_checks - passed_checks}/{total_checks}")
        
        if passed_checks == total_checks:
            print("🎉 All checks passed! Your system is ready for deployment!")
        elif passed_checks >= 6:
            print("⚠️ Most checks passed. Review failed checks before deployment.")
        else:
            print("❌ Multiple checks failed. Please fix issues before deployment.")
        
        # Generate report
        report = self.generate_verification_report()
        
        return passed_checks == total_checks

def main():
    """Main verification function"""
    verifier = DeploymentVerifier()
    success = verifier.run_all_checks()
    
    if success:
        print("\n🚀 Ready to deploy! Follow the deployment guide for next steps.")
    else:
        print("\n🔧 Please fix the issues above before proceeding with deployment.")
    
    return success

if __name__ == "__main__":
    main()