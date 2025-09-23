#!/usr/bin/env python3
"""
Setup Fortress Notes Firebase/Google Cloud Connection
"""

import subprocess
import json
from pathlib import Path

def setup_firebase_project():
    """Setup Firebase project connection"""
    print("SETTING UP FORTRESS NOTES PROJECT")
    print("=" * 40)
    
    # Update Firebase config
    firebaserc = {
        "projects": {
            "default": "fortress-notes-omrjz"
        }
    }
    
    with open(".firebaserc", "w") as f:
        json.dump(firebaserc, f, indent=2)
    
    print("SUCCESS: Updated .firebaserc")
    
    # Test Firebase CLI
    try:
        result = subprocess.run("firebase --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Firebase CLI: {result.stdout.strip()}")
        else:
            print("WARNING: Firebase CLI not installed")
    except:
        print("WARNING: Firebase CLI not available")
    
    return True

def update_deployment_configs():
    """Update deployment configurations"""
    print("\nUPDATING DEPLOYMENT CONFIGS")
    print("=" * 40)
    
    # Update deployment links
    deployment_links = Path("deployment_links.md")
    if deployment_links.exists():
        content = deployment_links.read_text()
        content = content.replace("genx-467217", "fortress-notes-omrjz")
        deployment_links.write_text(content)
        print("SUCCESS: Updated deployment_links.md")
    
    # Update docker-compose files
    docker_files = ["docker-compose.yml", "docker-compose.production.yml"]
    for file_name in docker_files:
        file_path = Path(file_name)
        if file_path.exists():
            content = file_path.read_text()
            content = content.replace("genx-467217", "fortress-notes-omrjz")
            file_path.write_text(content)
            print(f"SUCCESS: Updated {file_name}")

def test_connection():
    """Test connection to Fortress Notes project"""
    print("\nTESTING CONNECTION")
    print("=" * 40)
    
    # Test Firebase project
    try:
        result = subprocess.run("firebase projects:list", shell=True, capture_output=True, text=True)
        if "fortress-notes-omrjz" in result.stdout:
            print("SUCCESS: Fortress Notes project found")
        else:
            print("INFO: Need to authenticate with Firebase")
    except:
        print("INFO: Firebase CLI authentication needed")
    
    # Test Google Cloud
    try:
        result = subprocess.run("gcloud config get-value project", shell=True, capture_output=True, text=True)
        current_project = result.stdout.strip()
        if current_project == "fortress-notes-omrjz":
            print("SUCCESS: Google Cloud project set correctly")
        else:
            print(f"INFO: Current GCloud project: {current_project}")
            print("INFO: Run: gcloud config set project fortress-notes-omrjz")
    except:
        print("INFO: Google Cloud CLI not available")

def main():
    """Main setup function"""
    print("FORTRESS NOTES PROJECT SETUP")
    print("=" * 50)
    print("Project ID: fortress-notes-omrjz")
    print("Project Number: 723463751699")
    print("Auth UID: VK3on8vDcPaonpumb3jgDSiCGug1")
    print("=" * 50)
    
    # Setup Firebase
    setup_firebase_project()
    
    # Update configs
    update_deployment_configs()
    
    # Test connection
    test_connection()
    
    print("\nNEXT STEPS:")
    print("1. Run: firebase login")
    print("2. Run: gcloud auth login")
    print("3. Run: gcloud config set project fortress-notes-omrjz")
    print("4. Test: firebase deploy --project fortress-notes-omrjz")

if __name__ == "__main__":
    main()