#!/usr/bin/env node

import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class HistoryMakerCLI {
  constructor() {
    this.historymakerPath = path.join(__dirname, '../historymaker-1');
    this.config = this.loadConfig();
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
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

  async question(prompt) {
    return new Promise((resolve) => {
      this.rl.question(prompt, resolve);
    });
  }

  async runCommand(command, args = [], options = {}) {
    return new Promise((resolve, reject) => {
      const process = spawn(command, args, {
        cwd: this.historymakerPath,
        stdio: options.silent ? 'pipe' : 'inherit',
        ...options
      });

      let stdout = '';
      let stderr = '';

      if (options.silent) {
        process.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        process.stderr.on('data', (data) => {
          stderr += data.toString();
        });
      }

      process.on('close', (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });
    });
  }

  async checkServerStatus() {
    try {
      const port = this.config.PORT || 3001;
      const response = await fetch(`http://localhost:${port}/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  async startServer() {
    console.log('🚀 Starting HistoryMaker-1 server...');
    
    if (await this.checkServerStatus()) {
      console.log('✅ Server is already running');
      return;
    }

    try {
      await this.runCommand('npm', ['start']);
    } catch (error) {
      console.error('❌ Failed to start server:', error.message);
    }
  }

  async startDevServer() {
    console.log('🔧 Starting HistoryMaker-1 in development mode...');
    
    if (await this.checkServerStatus()) {
      console.log('✅ Server is already running');
      return;
    }

    try {
      await this.runCommand('npm', ['run', 'dev']);
    } catch (error) {
      console.error('❌ Failed to start dev server:', error.message);
    }
  }

  async installDependencies() {
    console.log('📦 Installing HistoryMaker-1 dependencies...');
    try {
      await this.runCommand('npm', ['install'], { silent: true });
      console.log('✅ Dependencies installed successfully');
    } catch (error) {
      console.error('❌ Failed to install dependencies:', error.message);
    }
  }

  async setupEnvironment() {
    console.log('⚙️ Setting up environment...');
    
    const envPath = path.join(this.historymakerPath, '.env');
    const envExamplePath = path.join(this.historymakerPath, '.env.example');
    
    if (!fs.existsSync(envPath) && fs.existsSync(envExamplePath)) {
      fs.copyFileSync(envExamplePath, envPath);
      console.log('✅ Environment file created from template');
    } else if (fs.existsSync(envPath)) {
      console.log('✅ Environment file already exists');
    } else {
      console.log('⚠️ No environment template found');
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
    
    if (!(await this.checkServerStatus())) {
      console.log('❌ Server is not running');
      return;
    }

    try {
      const port = this.config.PORT || 3001;
      const response = await fetch(`http://localhost:${port}/health`);
      const data = await response.json();
      console.log('✅ Health check response:', data);
    } catch (error) {
      console.error('❌ Health check failed:', error.message);
    }
  }

  async interactiveHistory() {
    console.log('📊 Interactive History Query');
    
    const symbol = await this.question('Enter symbol (e.g., EURUSD) or press Enter for all: ');
    const timeframe = await this.question('Enter timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d) or press Enter for all: ');
    const limit = await this.question('Enter limit (default 100): ') || '100';
    
    await this.getHistory(symbol || null, timeframe || null, parseInt(limit));
  }

  async getHistory(symbol = null, timeframe = null, limit = 100) {
    console.log('📊 Fetching trading history...');
    
    if (!(await this.checkServerStatus())) {
      console.log('❌ Server is not running. Please start the server first.');
      return;
    }

    try {
      const port = this.config.PORT || 3001;
      let url = `http://localhost:${port}/api/history?limit=${limit}`;
      
      if (symbol) url += `&symbol=${symbol}`;
      if (timeframe) url += `&timeframe=${timeframe}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        console.log(`✅ Retrieved ${data.count} history entries`);
        if (data.data.length > 0) {
          console.table(data.data.slice(0, 10)); // Show first 10 entries
          if (data.data.length > 10) {
            console.log(`... and ${data.data.length - 10} more entries`);
          }
        }
      } else {
        console.error('❌ Failed to fetch history:', data.error);
      }
    } catch (error) {
      console.error('❌ Error fetching history:', error.message);
    }
  }

  async getSymbols() {
    console.log('📈 Fetching available symbols...');
    
    if (!(await this.checkServerStatus())) {
      console.log('❌ Server is not running. Please start the server first.');
      return;
    }

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

  async interactiveExport() {
    console.log('📤 Interactive Data Export');
    
    const symbol = await this.question('Enter symbol (e.g., EURUSD): ');
    const timeframe = await this.question('Enter timeframe (1h, 1d): ');
    const startDate = await this.question('Enter start date (YYYY-MM-DD): ');
    const endDate = await this.question('Enter end date (YYYY-MM-DD): ');
    const format = await this.question('Enter format (csv/json, default csv): ') || 'csv';
    
    await this.exportData(symbol, timeframe, startDate, endDate, format);
  }

  async exportData(symbol, timeframe, startDate, endDate, format = 'csv') {
    console.log('📤 Exporting data...');
    
    if (!(await this.checkServerStatus())) {
      console.log('❌ Server is not running. Please start the server first.');
      return;
    }

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
    
    if (!(await this.checkServerStatus())) {
      console.log('❌ Server is not running. Please start the server first.');
      return;
    }

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
🎯 HistoryMaker-1 CLI

Available commands:
  start              - Start the HistoryMaker-1 server
  dev                - Start in development mode
  install            - Install dependencies
  setup              - Setup environment configuration
  test               - Run tests
  health             - Check server health
  history            - Interactive history query
  symbols            - Get available symbols
  export             - Interactive data export
  backup             - Create data backup
  help               - Show this help

Examples:
  node historymaker-cli.js start
  node historymaker-cli.js history
  node historymaker-cli.js export
  node historymaker-cli.js health

Integration with genx-cli:
  genx-cli --run-plugin historymaker_plugin start
  genx-cli --run-plugin historymaker_plugin history EURUSD
  genx-cli --run-plugin historymaker_plugin export
    `);
  }

  async run() {
    const args = process.argv.slice(2);
    const command = args[0];

    console.log('🎯 HistoryMaker-1 CLI');
    console.log('📁 Package path:', this.historymakerPath);
    console.log('');

    try {
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
        case 'setup':
          await this.setupEnvironment();
          break;
        case 'test':
          await this.runTests();
          break;
        case 'health':
          await this.checkHealth();
          break;
        case 'history':
          await this.interactiveHistory();
          break;
        case 'symbols':
          await this.getSymbols();
          break;
        case 'export':
          await this.interactiveExport();
          break;
        case 'backup':
          await this.backupData();
          break;
        case 'help':
        default:
          this.showHelp();
          break;
      }
    } catch (error) {
      console.error('❌ Error:', error.message);
    } finally {
      this.rl.close();
    }
  }
}

// Run the CLI
const cli = new HistoryMakerCLI();
cli.run();