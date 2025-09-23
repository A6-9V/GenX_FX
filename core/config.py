"""
Centralized Configuration Manager for GenX Trading Platform
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

class Config:
    """
    A centralized class to manage all configuration for the application.
    It loads settings from a YAML file and environment variables from a .env file.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.project_root = Path(__file__).parent.parent

        # Load .env file
        self.env_path = self.project_root / '.env'
        load_dotenv(dotenv_path=self.env_path)

        # Load YAML config
        self.config_path = self.project_root / 'config.yaml'
        self._settings = self._load_yaml_config()

        self._initialized = True

    def _load_yaml_config(self) -> Dict[str, Any]:
        """Loads the YAML configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"ERROR: Configuration file not found at {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"ERROR: Error parsing YAML configuration file: {e}")
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value.
        It can access nested keys using dot notation (e.g., 'trading.symbols').
        """
        keys = key.split('.')
        value = self._settings
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_env(self, key: str, default: Any = None) -> Any:
        """Retrieves a value from the environment variables."""
        return os.getenv(key, default)

    def __getitem__(self, key: str) -> Any:
        """Allows dictionary-style access to configuration."""
        return self.get(key)

# Create a single, project-wide instance of the Config class
config = Config()

if __name__ == '__main__':
    # Example usage and testing
    print(f"Project Root: {config.project_root}")
    print(f"Config Path: {config.config_path}")
    print(f"Env Path: {config.env_path}")

    print("\n--- Testing YAML Config Access ---")
    print(f"System Name: {config.get('system.name')}")
    print(f"Trading Symbols: {config.get('trading.symbols')}")
    print(f"A non-existent key: {config.get('foo.bar', 'default_value')}")

    print("\n--- Testing .env Access ---")
    print(f"AMP Token: {config.get_env('AMP_TOKEN')}")
    print(f"Postgres User: {config.get_env('POSTGRES_USER')}")

    print("\n--- Testing Dictionary-style Access ---")
    print(f"Risk Management Config: {config['risk_management']}")
