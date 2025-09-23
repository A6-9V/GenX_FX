import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

class TradingSystemPlugin {
  constructor() {
    this.name = 'trading_system';
    this.description = 'Advanced trading system management and monitoring';
    this.version = '1.0.0';
    this.config = {};
  }

  async loadConfig() {
    try {
      const configPath = path.join(process.cwd(), 'amp_config.json');
      if (fs.existsSync(configPath)) {
        const configContent = fs.readFileSync(configPath, 'utf-8');
        this.config = JSON.parse(configContent);
      }
    } catch (error) {
      console.error('Error loading config:', error.message);
    }
  }

  async checkSystemStatus() {
    console.log('🔍 Checking trading system status...\n');
    
    const checks = [
      { name: 'Python Environment', check: () => this.checkPythonEnv() },
      { name: 'Dependencies', check: () => this.checkDependencies() },
      { name: 'Configuration Files', check: () => this.checkConfigFiles() },
      { name: 'Database Connection', check: () => this.checkDatabase() },
      { name: 'Trading Services', check: () => this.checkTradingServices() }
    ];

    for (const check of checks) {
      try {
        await check.check();
      } catch (error) {
        console.log(`❌ ${check.name}: Failed - ${error.message}`);
      }
    }
  }

  async checkPythonEnv() {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python3', ['--version']);
      pythonProcess.stdout.on('data', (data) => {
        console.log(`✅ Python Environment: ${data.toString().trim()}`);
        resolve();
      });
      pythonProcess.stderr.on('data', (data) => {
        reject(new Error(data.toString().trim()));
      });
    });
  }

  async checkDependencies() {
    const requirementsPath = path.join(process.cwd(), 'requirements.txt');
    if (fs.existsSync(requirementsPath)) {
      console.log('✅ Dependencies: requirements.txt found');
      
      // Check if virtual environment is active
      if (process.env.VIRTUAL_ENV) {
        console.log(`   Virtual Environment: ${process.env.VIRTUAL_ENV}`);
      } else {
        console.log('   ⚠️  No virtual environment detected');
      }
    } else {
      console.log('❌ Dependencies: requirements.txt not found');
    }
  }

  async checkConfigFiles() {
    const configFiles = [
      '.env',
      'amp_config.json',
      'docker-compose.yml'
    ];

    for (const file of configFiles) {
      const filePath = path.join(process.cwd(), file);
      if (fs.existsSync(filePath)) {
        const stats = fs.statSync(filePath);
        console.log(`✅ ${file}: Found (${(stats.size / 1024).toFixed(1)} KB)`);
      } else {
        console.log(`❌ ${file}: Not found`);
      }
    }
  }

  async checkDatabase() {
    try {
      // Check if database files exist
      const dbDir = path.join(process.cwd(), 'database');
      if (fs.existsSync(dbDir)) {
        const dbFiles = fs.readdirSync(dbDir);
        console.log(`✅ Database: Found ${dbFiles.length} database files`);
      } else {
        console.log('⚠️  Database: Database directory not found');
      }
    } catch (error) {
      console.log(`❌ Database: ${error.message}`);
    }
  }

  async checkTradingServices() {
    const services = [
      { name: 'Main Trading Loop', file: 'main.py' },
      { name: 'Signal Output', dir: 'signal_output' },
      { name: 'Expert Advisors', dir: 'expert-advisors' },
      { name: 'Logs', dir: 'logs' }
    ];

    for (const service of services) {
      if (service.file) {
        const filePath = path.join(process.cwd(), service.file);
        if (fs.existsSync(filePath)) {
          console.log(`✅ ${service.name}: ${service.file} found`);
        } else {
          console.log(`❌ ${service.name}: ${service.file} not found`);
        }
      } else if (service.dir) {
        const dirPath = path.join(process.cwd(), service.dir);
        if (fs.existsSync(dirPath)) {
          const items = fs.readdirSync(dirPath);
          console.log(`✅ ${service.name}: ${service.dir} (${items.length} items)`);
        } else {
          console.log(`❌ ${service.name}: ${service.dir} not found`);
        }
      }
    }
  }

  async startTrading() {
    console.log('🚀 Starting trading system...\n');
    
    try {
      // Check if main.py exists and is runnable
      const mainPath = path.join(process.cwd(), 'main.py');
      if (!fs.existsSync(mainPath)) {
        throw new Error('main.py not found');
      }

      console.log('Starting main trading loop...');
      const tradingProcess = spawn('python3', [mainPath], {
        stdio: 'inherit',
        cwd: process.cwd()
      });

      tradingProcess.on('error', (error) => {
        console.error('❌ Failed to start trading system:', error.message);
      });

      tradingProcess.on('exit', (code) => {
        if (code === 0) {
          console.log('✅ Trading system stopped successfully');
        } else {
          console.log(`⚠️  Trading system stopped with code ${code}`);
        }
      });

    } catch (error) {
      console.error('❌ Error starting trading system:', error.message);
    }
  }

  async viewLogs() {
    console.log('📋 Recent trading logs:\n');
    
    const logsDir = path.join(process.cwd(), 'logs');
    if (!fs.existsSync(logsDir)) {
      console.log('No logs directory found');
      return;
    }

    try {
      const logFiles = fs.readdirSync(logsDir)
        .filter(file => file.endsWith('.log'))
        .sort((a, b) => {
          const aPath = path.join(logsDir, a);
          const bPath = path.join(logsDir, b);
          return fs.statSync(bPath).mtime.getTime() - fs.statSync(aPath).mtime.getTime();
        });

      if (logFiles.length === 0) {
        console.log('No log files found');
        return;
      }

      // Show the most recent log file
      const latestLog = logFiles[0];
      const logPath = path.join(logsDir, latestLog);
      const logContent = fs.readFileSync(logPath, 'utf-8');
      
      console.log(`📄 Latest log: ${latestLog}`);
      console.log('─'.repeat(50));
      
      // Show last 20 lines
      const lines = logContent.split('\n').filter(line => line.trim());
      const lastLines = lines.slice(-20);
      lastLines.forEach(line => console.log(line));
      
    } catch (error) {
      console.error('Error reading logs:', error.message);
    }
  }

  async showHelp() {
    console.log(`
🤖 Trading System Plugin - Available Commands

Commands:
  status          - Check system status and health
  start           - Start the trading system
  logs            - View recent trading logs
  help            - Show this help message

Examples:
  genx-cli --run-plugin trading_system status
  genx-cli --run-plugin trading_system start
  genx-cli --run-plugin trading_system logs

Plugin Info:
  Name: ${this.name}
  Version: ${this.version}
  Description: ${this.description}
`);
  }

  async run(config) {
    await this.loadConfig();
    
    // Get command from process.argv since this is called from the main CLI
    const args = process.argv.slice(2); // Skip node and script
    let command = 'help';
    
    // Find the command after --run-plugin trading_system
    const pluginIndex = args.findIndex(arg => arg === 'trading_system');
    if (pluginIndex !== -1 && args[pluginIndex + 1]) {
      command = args[pluginIndex + 1];
    }

    switch (command) {
      case 'status':
        await this.checkSystemStatus();
        break;
      case 'start':
        await this.startTrading();
        break;
      case 'logs':
        await this.viewLogs();
        break;
      case 'help':
      default:
        await this.showHelp();
        break;
    }
  }
}

const plugin = new TradingSystemPlugin();

export default {
  description: plugin.description,
  run: (config) => plugin.run(config)
};