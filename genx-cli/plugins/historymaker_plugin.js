import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class HistoryMakerPlugin {
  constructor() {
    this.historymakerPath = path.join(__dirname, '../../historymaker-1');
    this.config = this.loadConfig();
  }

  loadConfig() {
    const configPath = path.join(this.historymakerPath, '.env');
    const config = {};
    
    if (fs.existsSync(configPath)) {
      const content = fs.readFileSync(configPath, 'utf8');
      content.split('\n').forEach(line => {
        const [key, value] = line.split('=');
        if (key && value) {
          config[key.trim()] = value.trim();
        }
      });
    }
    
    return config;
  }

  async runCommand(command, args = []) {
    return new Promise((resolve, reject) => {
      const process = spawn(command, args, {
        cwd: this.historymakerPath,
        stdio: 'pipe'
      });

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
        console.log(data.toString());
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
        console.error(data.toString());
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });
    });
  }

  async startServer() {
    console.log('🚀 Starting HistoryMaker-1 server...');
    try {
      await this.runCommand('npm', ['start']);
    } catch (error) {
      console.error('❌ Failed to start server:', error.message);
    }
  }

  async startDevServer() {
    console.log('🔧 Starting HistoryMaker-1 in development mode...');
    try {
      await this.runCommand('npm', ['run', 'dev']);
    } catch (error) {
      console.error('❌ Failed to start dev server:', error.message);
    }
  }

  async installDependencies() {
    console.log('📦 Installing HistoryMaker-1 dependencies...');
    try {
      await this.runCommand('npm', ['install']);
      console.log('✅ Dependencies installed successfully');
    } catch (error) {
      console.error('❌ Failed to install dependencies:', error.message);
    }
  }

  async runTests() {
    console.log('🧪 Running HistoryMaker-1 tests...');
    try {
      await this.runCommand('npm', ['test']);
    } catch (error) {
      console.error('❌ Tests failed:', error.message);
    }
  }

  async checkHealth() {
    console.log('🏥 Checking HistoryMaker-1 health...');
    try {
      const port = this.config.PORT || 3001;
      const response = await fetch(`http://localhost:${port}/health`);
      const data = await response.json();
      console.log('✅ Health check response:', data);
    } catch (error) {
      console.error('❌ Health check failed:', error.message);
    }
  }

  async getHistory(symbol = null, timeframe = null, limit = 100) {
    console.log('📊 Fetching trading history...');
    try {
      const port = this.config.PORT || 3001;
      let url = `http://localhost:${port}/api/history?limit=${limit}`;
      
      if (symbol) url += `&symbol=${symbol}`;
      if (timeframe) url += `&timeframe=${timeframe}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        console.log(`✅ Retrieved ${data.count} history entries`);
        console.table(data.data.slice(0, 10)); // Show first 10 entries
      } else {
        console.error('❌ Failed to fetch history:', data.error);
      }
    } catch (error) {
      console.error('❌ Error fetching history:', error.message);
    }
  }

  async getSymbols() {
    console.log('📈 Fetching available symbols...');
    try {
      const port = this.config.PORT || 3001;
      const response = await fetch(`http://localhost:${port}/api/data/symbols`);
      const data = await response.json();
      
      if (data.success) {
        console.log('✅ Available symbols:', data.data);
      } else {
        console.error('❌ Failed to fetch symbols:', data.error);
      }
    } catch (error) {
      console.error('❌ Error fetching symbols:', error.message);
    }
  }

  async getStats(symbol = null, timeframe = null) {
    console.log('📈 Fetching statistics...');
    try {
      const port = this.config.PORT || 3001;
      let url = `http://localhost:${port}/api/history/stats`;
      
      if (symbol) url += `?symbol=${symbol}`;
      if (timeframe) url += `${symbol ? '&' : '?'}timeframe=${timeframe}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        console.log('✅ Statistics:', data.data);
      } else {
        console.error('❌ Failed to fetch stats:', data.error);
      }
    } catch (error) {
      console.error('❌ Error fetching stats:', error.message);
    }
  }

  async exportData(symbol, timeframe, startDate, endDate, format = 'csv') {
    console.log('📤 Exporting data...');
    try {
      const port = this.config.PORT || 3001;
      const response = await fetch(`http://localhost:${port}/api/data/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          symbol,
          timeframe,
          startDate,
          endDate,
          format
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        console.log('✅ Data exported successfully');
        if (format === 'csv') {
          console.log('📄 CSV Data:');
          console.log(data.data);
        }
      } else {
        console.error('❌ Failed to export data:', data.error);
      }
    } catch (error) {
      console.error('❌ Error exporting data:', error.message);
    }
  }

  async backupData() {
    console.log('💾 Creating data backup...');
    try {
      const port = this.config.PORT || 3001;
      const response = await fetch(`http://localhost:${port}/api/data/backup`, {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (data.success) {
        console.log('✅ Backup created successfully');
        console.log('📁 Backup location:', data.data.backupPath);
        console.log('📊 Records backed up:', data.data.recordCount);
      } else {
        console.error('❌ Failed to create backup:', data.error);
      }
    } catch (error) {
      console.error('❌ Error creating backup:', error.message);
    }
  }

  showHelp() {
    console.log(`
🎯 HistoryMaker-1 CLI Plugin

Available commands:
  start              - Start the HistoryMaker-1 server
  dev                - Start in development mode
  install            - Install dependencies
  test               - Run tests
  health             - Check server health
  history [symbol]   - Get trading history (optional symbol)
  symbols            - Get available symbols
  stats [symbol]     - Get statistics (optional symbol)
  export             - Export data (interactive)
  backup             - Create data backup
  help               - Show this help

Examples:
  genx-cli --run-plugin historymaker_plugin start
  genx-cli --run-plugin historymaker_plugin history EURUSD
  genx-cli --run-plugin historymaker_plugin stats GBPUSD
  genx-cli --run-plugin historymaker_plugin export
    `);
  }

  async run(config) {
    const args = process.argv.slice(3); // Skip node, script, plugin name
    const command = args[0];

    console.log('🎯 HistoryMaker-1 Plugin');
    console.log('📁 Package path:', this.historymakerPath);
    console.log('');

    switch (command) {
      case 'start':
        await this.startServer();
        break;
      case 'dev':
        await this.startDevServer();
        break;
      case 'install':
        await this.installDependencies();
        break;
      case 'test':
        await this.runTests();
        break;
      case 'health':
        await this.checkHealth();
        break;
      case 'history':
        await this.getHistory(args[1], args[2], args[3]);
        break;
      case 'symbols':
        await this.getSymbols();
        break;
      case 'stats':
        await this.getStats(args[1], args[2]);
        break;
      case 'export':
        await this.exportData(args[1], args[2], args[3], args[4], args[5]);
        break;
      case 'backup':
        await this.backupData();
        break;
      case 'help':
      default:
        this.showHelp();
        break;
    }
  }
}

const plugin = new HistoryMakerPlugin();

function run(config) {
  return plugin.run(config);
}

export default {
  description: 'HistoryMaker-1 trading history management plugin with full CLI integration.',
  run
};