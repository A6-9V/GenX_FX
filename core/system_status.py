"""
Centralized System Status Checker for GenX Trading Platform
"""

import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from core.config import config

def get_system_status() -> Dict[str, Any]:
    """
    Gathers a comprehensive status report of the entire system.
    Combines checks from the old genx_cli and amp_monitor.
    """
    project_root = Path(__file__).parent.parent
    status = {
        'timestamp': datetime.now().isoformat(),
        'file_system': get_file_system_status(project_root),
        'dependencies': get_dependency_status(),
        'forexconnect': get_forexconnect_status(project_root),
        'amp': get_amp_status(),
    }
    return status

def get_file_system_status(project_root: Path) -> Dict[str, Any]:
    """Checks the status of key files and directories."""
    fs_status = {'directories': {}, 'files': {}}

    # Check directories
    key_dirs = ['core', 'api', 'client', 'signal_output', 'logs', 'config', 'ai_models']
    for dir_name in key_dirs:
        dir_path = project_root / dir_name
        fs_status['directories'][dir_name] = {
            'exists': dir_path.exists(),
            'path': str(dir_path),
            'items': len(list(dir_path.iterdir())) if dir_path.exists() else 0
        }

    # Check important files
    key_files = ['.env', '.env.example', 'requirements.txt', 'main.py', 'config.yaml', 'package.json']
    for file_name in key_files:
        file_path = project_root / file_name
        fs_status['files'][file_name] = {
            'exists': file_path.exists(),
            'size': file_path.stat().st_size if file_path.exists() else 0,
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() if file_path.exists() else None
        }

    return fs_status

def get_dependency_status() -> Dict[str, Any]:
    """Checks for the presence and version of key Python dependencies."""
    deps_status = {}
    dependencies = ['pandas', 'openpyxl', 'typer', 'rich']
    for dep_name in dependencies:
        try:
            module = __import__(dep_name)
            version = getattr(module, '__version__', 'N/A')
            deps_status[dep_name] = {'installed': True, 'version': version}
        except ImportError:
            deps_status[dep_name] = {'installed': False, 'version': None}
    return deps_status

def get_forexconnect_status(project_root: Path) -> Dict[str, Any]:
    """Checks the status of the ForexConnect integration."""
    fc_status = {}
    try:
        import forexconnect
        fc_status['available'] = True
        fc_status['module_path'] = forexconnect.__file__
    except ImportError:
        fc_status['available'] = False
        fc_status['module_path'] = None

    fc_env = project_root / "forexconnect_env_37"
    fc_status['env_exists'] = fc_env.exists()
    fc_status['env_path'] = str(fc_env) if fc_env.exists() else None

    return fc_status

def get_amp_status() -> Dict[str, Any]:
    """Gathers status specific to the AMP system."""
    amp_status = {
        'api_provider': config.get('amp.api_provider', 'Not set'),
        'plugins_installed': len(config.get('amp.plugins', [])),
        'services_enabled': len(config.get('amp.enabled_services', [])),
        'features': {
            'sentiment_analysis': config.get('features.sentiment_analysis', False),
            'social_signals': config.get('features.social_signals', False),
            'news_feeds': config.get('features.news_feeds', False),
            'websocket_streams': config.get('features.websocket_streams', False),
        }
    }
    # In a real scenario, we might add checks for auth, scheduler, etc.
    # from amp_auth import check_auth
    # from amp_scheduler import get_scheduler_status
    # amp_status['authentication'] = check_auth()
    # amp_status['scheduler'] = get_scheduler_status()
    return amp_status

if __name__ == '__main__':
    # Example usage and testing
    from rich.console import Console
    from rich.json import JSON

    console = Console()
    full_status = get_system_status()
    console.print(JSON(data=full_status))
