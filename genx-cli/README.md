# GenX CLI Plugin System

A powerful and extensible command-line interface for the GenX FX trading platform with a comprehensive plugin architecture.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Make CLI executable
chmod +x genx-cli/cli.js

# Run CLI
./genx-cli/cli.js --help

# List available plugins
./genx-cli/cli.js --list-plugins

# Run a specific plugin
./genx-cli/cli.js --run-plugin trading_system status
```

## 🔌 Available Plugins

### Core Plugins

#### 1. **Trading System Plugin** (`trading_system`)
Comprehensive trading system management and monitoring.

**Commands:**
- `status` - Check system status and health
- `start` - Start the trading system
- `logs` - View recent trading logs
- `help` - Show help information

**Usage:**
```bash
./genx-cli/cli.js --run-plugin trading_system status
./genx-cli/cli.js --run-plugin trading_system start
./genx-cli/cli.js --run-plugin trading_system logs
```

#### 2. **AI Analyzer Plugin** (`ai_analyzer.py`)
AI-powered trading analysis and insights using Python.

**Commands:**
- `analyze` - Analyze trading data and AI models
- `models` - Check AI models status
- `performance` - Analyze system performance
- `report` - Generate comprehensive analysis report

**Usage:**
```bash
./genx-cli/cli.js --run-plugin ai_analyzer.py analyze
./genx-cli/cli.js --run-plugin ai_analyzer.py models
./genx-cli/cli.js --run-plugin ai_analyzer.py report
```

#### 3. **Configuration Manager Plugin** (`config_manager`)
Interactive configuration management for CLI and trading system.

**Features:**
- View current configurations
- Edit `.julenrc`, `amp_config.json`, `.env`, `docker-compose.yml`
- Create new configurations
- Backup and restore configurations
- Validate configuration files

**Usage:**
```bash
./genx-cli/cli.js --run-plugin config_manager
```

#### 4. **Legacy Plugins**
- `jules_plugin` - Jules integration
- `codacy_plugin` - Code quality analysis
- `license_checker.py` - License validation
- `amp_adapter` - AMP AI Coder integration

## 🛠️ Plugin Development

### Creating JavaScript Plugins

Create a new file in `genx-cli/plugins/` with the following structure:

```javascript
// my_plugin.js
function run(config) {
  console.log('Running My Plugin...');
  // Your plugin logic here
}

export default {
  description: 'Description of my plugin',
  run
};
```

### Creating Python Plugins

Create a new Python file in `genx-cli/plugins/` with the following structure:

```python
#!/usr/bin/env python3
"""
My Python Plugin for GenX CLI
"""

import sys

def run(command="help"):
    if command == "help":
        print("My Plugin Help")
    elif command == "execute":
        print("Executing my plugin...")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    run(command)
```

### Plugin Configuration

Add your plugin to `.julenrc`:

```json
{
  "plugins": [
    "my_plugin",
    "my_python_plugin.py"
  ]
}
```

## ⚙️ Configuration

### .julenrc
Main CLI configuration file containing:
- Plugin list
- Custom commands
- Git configuration
- Environment settings

### amp_config.json
Trading system configuration:
- API keys
- Trading parameters
- Risk management settings
- System preferences

### .env
Environment variables for the trading system.

### docker-compose.yml
Docker services configuration.

## 📋 CLI Commands

### Basic Commands
```bash
# Show help
./genx-cli/cli.js --help

# List plugins
./genx-cli/cli.js --list-plugins

# Run plugin
./genx-cli/cli.js --run-plugin <plugin_name> [command]

# Run custom command
./genx-cli/cli.js run <command_name>
```

### Plugin Commands
Each plugin can have its own subcommands:

```bash
# Trading system status
./genx-cli/cli.js --run-plugin trading_system status

# AI analysis
./genx-cli/cli.js --run-plugin ai_analyzer.py analyze

# Configuration management
./genx-cli/cli.js --run-plugin config_manager
```

## 🔧 Advanced Features

### Plugin Auto-discovery
The CLI automatically discovers and loads plugins from the `plugins/` directory.

### Configuration Inheritance
Plugins can access and modify CLI configuration through the config parameter.

### Error Handling
Robust error handling with detailed error messages and fallback options.

### Logging
Comprehensive logging system for debugging and monitoring.

## 🚀 Deployment

### Local Development
```bash
# Clone repository
git clone <your-repo>

# Install dependencies
npm install

# Run CLI
./genx-cli/cli.js --help
```

### Production Deployment
```bash
# Build and package
npm run build

# Deploy to production
# Copy genx-cli/ directory to production server
# Ensure proper permissions
chmod +x genx-cli/cli.js
```

## 📊 Monitoring and Logs

### Log Files
- CLI logs: `logs/cli.log`
- Trading logs: `logs/trading.log`
- Plugin logs: `logs/plugins.log`

### Status Monitoring
Use the trading system plugin to monitor system health:
```bash
./genx-cli/cli.js --run-plugin trading_system status
```

## 🆘 Troubleshooting

### Common Issues

1. **Plugin not found**
   - Check plugin name in `.julenrc`
   - Verify plugin file exists in `plugins/` directory

2. **Permission denied**
   - Ensure CLI is executable: `chmod +x genx-cli/cli.js`

3. **Configuration errors**
   - Validate configuration files
   - Use config manager plugin to fix issues

4. **Python plugin errors**
   - Check Python installation
   - Verify plugin dependencies

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=genx-cli:*
./genx-cli/cli.js --run-plugin <plugin_name>
```

## 🤝 Contributing

### Adding New Plugins
1. Create plugin file in `genx-cli/plugins/`
2. Follow plugin structure guidelines
3. Add to `.julenrc` configuration
4. Test thoroughly
5. Submit pull request

### Plugin Guidelines
- Follow naming conventions
- Include comprehensive error handling
- Provide clear help documentation
- Use consistent output formatting
- Handle configuration gracefully

## 📚 API Reference

### Plugin Interface
```javascript
export default {
  description: 'Plugin description',
  run: (config) => {
    // Plugin implementation
  }
}
```

### Configuration Object
```javascript
{
  plugins: ['plugin1', 'plugin2'],
  commands: {
    custom: 'command string'
  },
  git: {
    github: { username, token },
    gitlab: { username, token }
  }
}
```

## 🔒 Security

### API Keys
- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement proper key rotation

### Permissions
- Restrict CLI access to authorized users
- Use proper file permissions
- Implement audit logging

## 📈 Performance

### Optimization Tips
- Use async/await for I/O operations
- Implement caching for expensive operations
- Minimize file system calls
- Use streaming for large files

### Monitoring
- Track plugin execution time
- Monitor memory usage
- Log performance metrics

## 🌟 Future Enhancements

- Plugin marketplace
- Auto-update system
- Advanced analytics
- Machine learning integration
- Cloud deployment tools
- Mobile CLI app

---

For more information, visit the [GenX FX Documentation](https://docs.genxfx.com) or contact the development team.
