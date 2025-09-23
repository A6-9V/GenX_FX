# GenX CLI Integration with HistoryMaker-1

## Overview

This document explains the complete integration between the GenX CLI system and the HistoryMaker-1 package. The integration provides multiple ways to interact with the HistoryMaker-1 service through command-line interfaces.

## Architecture

```
GenX Project Root
├── genx-cli/                    # Main CLI system
│   ├── cli.js                   # Main CLI entry point
│   ├── historymaker-cli.js      # Dedicated HistoryMaker CLI
│   ├── plugins/                 # Plugin system
│   │   ├── historymaker_plugin.js  # HistoryMaker plugin
│   │   └── utils/
│   │       └── pluginLoader.js  # Plugin loader
│   └── CLI_INTEGRATION.md       # This documentation
├── historymaker-1/              # HistoryMaker package
│   ├── src/                     # Source code
│   ├── package.json             # Package configuration
│   └── README.md                # Package documentation
├── package.json                 # Root package configuration
└── .julenrc                     # CLI configuration
```

## CLI Access Methods

### 1. Main GenX CLI with Plugin

The HistoryMaker-1 functionality is integrated into the main GenX CLI through a plugin system.

```bash
# List all available plugins
genx-cli --list-plugins

# Run HistoryMaker plugin commands
genx-cli --run-plugin historymaker_plugin start
genx-cli --run-plugin historymaker_plugin history EURUSD
genx-cli --run-plugin historymaker_plugin export
genx-cli --run-plugin historymaker_plugin health
```

### 2. Dedicated HistoryMaker CLI

A standalone CLI specifically for HistoryMaker-1 operations.

```bash
# Direct access to HistoryMaker CLI
historymaker start
historymaker dev
historymaker history
historymaker export
historymaker health
```

### 3. Node.js Direct Execution

Execute the CLI scripts directly with Node.js.

```bash
# Execute the dedicated CLI
node genx-cli/historymaker-cli.js start
node genx-cli/historymaker-cli.js history
node genx-cli/historymaker-cli.js export

# Execute the plugin
node genx-cli/cli.js --run-plugin historymaker_plugin start
```

## Available Commands

### Server Management
- `start` - Start the HistoryMaker-1 server
- `dev` - Start in development mode with auto-reload
- `health` - Check server health status

### Package Management
- `install` - Install HistoryMaker-1 dependencies
- `setup` - Setup environment configuration
- `test` - Run HistoryMaker-1 tests

### Data Operations
- `history [symbol] [timeframe] [limit]` - Get trading history
- `symbols` - Get available trading symbols
- `export [symbol] [timeframe] [startDate] [endDate] [format]` - Export data
- `backup` - Create data backup

### Interactive Mode
- `history` (no args) - Interactive history query
- `export` (no args) - Interactive data export

## Configuration

### Environment Setup

The HistoryMaker-1 package uses environment variables for configuration:

```env
# Server Configuration
PORT=3001
NODE_ENV=development

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/historymaker

# Logging Configuration
LOG_LEVEL=info

# Security Configuration
CORS_ORIGIN=http://localhost:3000
```

### CLI Configuration (.julenrc)

The main CLI configuration includes the HistoryMaker plugin:

```json
{
  "plugins": [
    "jules_plugin",
    "codacy_plugin",
    "license_checker.py",
    "amp_adapter",
    "historymaker_plugin"
  ]
}
```

## Usage Examples

### Starting the Service

```bash
# Method 1: Main CLI with plugin
genx-cli --run-plugin historymaker_plugin start

# Method 2: Dedicated CLI
historymaker start

# Method 3: Direct execution
node genx-cli/historymaker-cli.js start
```

### Querying Trading History

```bash
# Get all history (last 100 entries)
genx-cli --run-plugin historymaker_plugin history

# Get EURUSD history
genx-cli --run-plugin historymaker_plugin history EURUSD

# Get EURUSD 1-hour history (last 50 entries)
genx-cli --run-plugin historymaker_plugin history EURUSD 1h 50

# Interactive mode
historymaker history
```

### Data Export

```bash
# Export EURUSD data for January 2024
genx-cli --run-plugin historymaker_plugin export EURUSD 1h 2024-01-01 2024-01-31 csv

# Interactive export
historymaker export
```

### Health Monitoring

```bash
# Check server health
genx-cli --run-plugin historymaker_plugin health

# Get available symbols
genx-cli --run-plugin historymaker_plugin symbols
```

## Integration with Development Workflow

### Concurrent Development

The main project's development script includes HistoryMaker-1:

```bash
# Start all services including HistoryMaker-1
npm run dev
```

This runs:
- Client (Vite) on port 5173
- Server (TypeScript) on port 3000
- Python API on port 8000
- HistoryMaker-1 on port 3001

### Package Management

```bash
# Install HistoryMaker-1 dependencies
npm run historymaker:install

# Start HistoryMaker-1 service
npm run historymaker:start

# Run HistoryMaker-1 tests
npm run historymaker:test
```

## Error Handling

The CLI provides comprehensive error handling:

1. **Server Status Checks** - Verifies if the HistoryMaker-1 server is running before making API calls
2. **Configuration Validation** - Checks for required environment variables and configuration files
3. **Network Error Handling** - Gracefully handles connection issues and API failures
4. **User Input Validation** - Validates user input for commands and parameters

## Troubleshooting

### Common Issues

1. **Server Not Running**
   ```
   ❌ Server is not running. Please start the server first.
   ```
   Solution: Run `historymaker start` or `genx-cli --run-plugin historymaker_plugin start`

2. **Dependencies Missing**
   ```
   ❌ Failed to install dependencies
   ```
   Solution: Run `historymaker install` or `npm run historymaker:install`

3. **Configuration Missing**
   ```
   ⚠️ No environment template found
   ```
   Solution: Run `historymaker setup` to create environment configuration

4. **Port Already in Use**
   ```
   ❌ Failed to start server
   ```
   Solution: Check if port 3001 is available or change PORT in .env file

### Debug Mode

Enable debug logging by setting the LOG_LEVEL environment variable:

```bash
export LOG_LEVEL=debug
historymaker start
```

## API Integration

The CLI communicates with the HistoryMaker-1 API endpoints:

- `GET /health` - Health check
- `GET /api/history` - Get trading history
- `GET /api/history/symbol/:symbol` - Get history by symbol
- `GET /api/history/latest` - Get latest entry
- `GET /api/history/stats` - Get statistics
- `GET /api/data/symbols` - Get available symbols
- `POST /api/data/export` - Export data
- `POST /api/data/backup` - Create backup

## Security Considerations

1. **Environment Variables** - Sensitive configuration is stored in .env files
2. **CORS Configuration** - API endpoints are configured with appropriate CORS settings
3. **Input Validation** - All user input is validated before processing
4. **Error Sanitization** - Error messages are sanitized to prevent information leakage

## Future Enhancements

1. **Authentication** - Add authentication to API endpoints
2. **Rate Limiting** - Implement rate limiting for API calls
3. **WebSocket Support** - Add real-time data streaming
4. **Advanced Analytics** - Add technical analysis and charting capabilities
5. **Multi-database Support** - Support for different database backends
6. **Plugin System** - Extend the plugin system for custom data sources

## Contributing

To contribute to the CLI integration:

1. Follow the existing code structure and patterns
2. Add comprehensive error handling
3. Include interactive modes for complex operations
4. Update documentation for new features
5. Add tests for new functionality

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the HistoryMaker-1 package documentation
3. Check the main project documentation
4. Create an issue in the project repository