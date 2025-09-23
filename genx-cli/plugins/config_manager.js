import fs from 'fs';
import path from 'path';
import readline from 'readline';

class ConfigManagerPlugin {
  constructor() {
    this.name = 'config_manager';
    this.description = 'Interactive configuration management for GenX CLI and trading system';
    this.version = '1.0.0';
    this.projectRoot = process.cwd();
    this.configFiles = {
      julenrc: '.julenrc',
      ampConfig: 'amp_config.json',
      envFile: '.env',
      dockerCompose: 'docker-compose.yml'
    };
  }

  async createInterface() {
    return readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async question(rl, query) {
    return new Promise((resolve) => {
      rl.question(query, resolve);
    });
  }

  async showMainMenu() {
    const rl = await this.createInterface();
    
    try {
      while (true) {
        console.clear();
        console.log('⚙️  Configuration Manager');
        console.log('=' .repeat(40));
        console.log('1. View current configurations');
        console.log('2. Edit .julenrc (CLI config)');
        console.log('3. Edit amp_config.json');
        console.log('4. Edit .env file');
        console.log('5. Edit docker-compose.yml');
        console.log('6. Create new configuration');
        console.log('7. Backup configurations');
        console.log('8. Validate configurations');
        console.log('0. Exit');
        console.log('');

        const choice = await this.question(rl, 'Select an option (0-8): ');

        switch (choice) {
          case '1':
            await this.viewConfigurations();
            break;
          case '2':
            await this.editJulenrc(rl);
            break;
          case '3':
            await this.editAmpConfig(rl);
            break;
          case '4':
            await this.editEnvFile(rl);
            break;
          case '5':
            await this.editDockerCompose(rl);
            break;
          case '6':
            await this.createNewConfig(rl);
            break;
          case '7':
            await this.backupConfigurations();
            break;
          case '8':
            await this.validateConfigurations();
            break;
          case '0':
            console.log('👋 Goodbye!');
            rl.close();
            return;
          default:
            console.log('❌ Invalid option. Please try again.');
        }

        if (choice !== '0') {
          await this.question(rl, '\nPress Enter to continue...');
        }
      }
    } finally {
      rl.close();
    }
  }

  async viewConfigurations() {
    console.log('📋 Current Configurations\n');

    for (const [name, filename] of Object.entries(this.configFiles)) {
      const filepath = path.join(this.projectRoot, filename);
      console.log(`${name.toUpperCase()}:`);
      
      if (fs.existsSync(filepath)) {
        const stats = fs.statSync(filepath);
        console.log(`  ✅ File: ${filename}`);
        console.log(`  📏 Size: ${(stats.size / 1024).toFixed(2)} KB`);
        console.log(`  🕒 Modified: ${stats.mtime.toLocaleString()}`);
        
        // Show preview for text files
        if (filename.endsWith('.json') || filename.endsWith('.yml') || filename.endsWith('.yaml') || filename.startsWith('.')) {
          try {
            const content = fs.readFileSync(filepath, 'utf-8');
            const preview = content.split('\n').slice(0, 5).join('\n');
            console.log(`  📄 Preview:\n${preview}${content.split('\n').length > 5 ? '\n    ...' : ''}`);
          } catch (error) {
            console.log(`  ❌ Error reading file: ${error.message}`);
          }
        }
      } else {
        console.log(`  ❌ File: ${filename} (not found)`);
      }
      console.log('');
    }
  }

  async editJulenrc(rl) {
    console.log('📝 Editing .julenrc Configuration\n');
    
    const filepath = path.join(this.projectRoot, this.configFiles.julenrc);
    let config = {};
    
    if (fs.existsSync(filepath)) {
      try {
        const content = fs.readFileSync(filepath, 'utf-8');
        config = JSON.parse(content);
        console.log('Current configuration loaded.');
      } catch (error) {
        console.log('❌ Error reading existing config, starting fresh.');
      }
    }

    // Edit plugins
    console.log('\n🔌 Plugins Configuration:');
    const currentPlugins = config.plugins || [];
    console.log(`Current plugins: ${currentPlugins.join(', ') || 'none'}`);
    
    const addPlugin = await this.question(rl, 'Add a new plugin? (y/n): ');
    if (addPlugin.toLowerCase() === 'y') {
      const pluginName = await this.question(rl, 'Enter plugin name: ');
      if (pluginName.trim()) {
        currentPlugins.push(pluginName.trim());
        config.plugins = currentPlugins;
      }
    }

    // Edit commands
    console.log('\n⚡ Commands Configuration:');
    const currentCommands = config.commands || {};
    console.log('Current commands:');
    Object.entries(currentCommands).forEach(([name, cmd]) => {
      console.log(`  ${name}: ${cmd}`);
    });
    
    const addCommand = await this.question(rl, 'Add a new command? (y/n): ');
    if (addCommand.toLowerCase() === 'y') {
      const cmdName = await this.question(rl, 'Enter command name: ');
      const cmdValue = await this.question(rl, 'Enter command value: ');
      if (cmdName.trim() && cmdValue.trim()) {
        config.commands[cmdName.trim()] = cmdValue.trim();
      }
    }

    // Save configuration
    try {
      fs.writeFileSync(filepath, JSON.stringify(config, null, 2));
      console.log('✅ .julenrc configuration saved successfully!');
    } catch (error) {
      console.log(`❌ Error saving configuration: ${error.message}`);
    }
  }

  async editAmpConfig(rl) {
    console.log('📝 Editing amp_config.json Configuration\n');
    
    const filepath = path.join(this.projectRoot, this.configFiles.ampConfig);
    let config = {};
    
    if (fs.existsSync(filepath)) {
      try {
        const content = fs.readFileSync(filepath, 'utf-8');
        config = JSON.parse(content);
        console.log('Current configuration loaded.');
      } catch (error) {
        console.log('❌ Error reading existing config, starting fresh.');
      }
    }

    // Basic trading configuration
    console.log('\n📊 Trading Configuration:');
    
    const apiKey = await this.question(rl, `API Key (current: ${config.api_key || 'not set'}): `);
    if (apiKey.trim()) config.api_key = apiKey.trim();
    
    const secretKey = await this.question(rl, `Secret Key (current: ${config.secret_key || 'not set'}): `);
    if (secretKey.trim()) config.secret_key = secretKey.trim();
    
    const tradingMode = await this.question(rl, `Trading Mode (demo/live) [current: ${config.trading_mode || 'demo'}]: `);
    if (tradingMode.trim()) config.trading_mode = tradingMode.trim();
    
    const riskLevel = await this.question(rl, `Risk Level (low/medium/high) [current: ${config.risk_level || 'medium'}]: `);
    if (riskLevel.trim()) config.risk_level = riskLevel.trim();

    // Save configuration
    try {
      fs.writeFileSync(filepath, JSON.stringify(config, null, 2));
      console.log('✅ amp_config.json configuration saved successfully!');
    } catch (error) {
      console.log(`❌ Error saving configuration: ${error.message}`);
    }
  }

  async editEnvFile(rl) {
    console.log('📝 Editing .env Configuration\n');
    
    const filepath = path.join(this.projectRoot, this.configFiles.envFile);
    const envExamplePath = path.join(this.projectRoot, '.env.example');
    
    let envVars = {};
    
    // Load existing .env if it exists
    if (fs.existsSync(filepath)) {
      try {
        const content = fs.readFileSync(filepath, 'utf-8');
        content.split('\n').forEach(line => {
          if (line.includes('=') && !line.startsWith('#')) {
            const [key, ...valueParts] = line.split('=');
            envVars[key.trim()] = valueParts.join('=').trim();
          }
        });
        console.log('Current .env configuration loaded.');
      } catch (error) {
        console.log('❌ Error reading existing .env, starting fresh.');
      }
    }

    // Load from .env.example if available
    if (fs.existsSync(envExamplePath)) {
      try {
        const content = fs.readFileSync(envExamplePath, 'utf-8');
        content.split('\n').forEach(line => {
          if (line.includes('=') && !line.startsWith('#')) {
            const [key, ...valueParts] = line.split('=');
            const keyName = key.trim();
            if (!envVars[keyName]) {
              envVars[keyName] = valueParts.join('=').trim();
            }
          }
        });
        console.log('Loaded template from .env.example');
      } catch (error) {
        console.log('⚠️  Could not load .env.example template');
      }
    }

    // Edit environment variables
    console.log('\n🔧 Environment Variables:');
    for (const [key, value] of Object.entries(envVars)) {
      const newValue = await this.question(rl, `${key} [current: ${value}]: `);
      if (newValue.trim()) {
        envVars[key] = newValue.trim();
      }
    }

    // Add new variables
    const addMore = await this.question(rl, '\nAdd more environment variables? (y/n): ');
    if (addMore.toLowerCase() === 'y') {
      while (true) {
        const newKey = await this.question(rl, 'Enter variable name (or empty to finish): ');
        if (!newKey.trim()) break;
        
        const newValue = await this.question(rl, `Enter value for ${newKey}: `);
        if (newValue.trim()) {
          envVars[newKey.trim()] = newValue.trim();
        }
      }
    }

    // Save .env file
    try {
      const envContent = Object.entries(envVars)
        .map(([key, value]) => `${key}=${value}`)
        .join('\n');
      
      fs.writeFileSync(filepath, envContent);
      console.log('✅ .env configuration saved successfully!');
    } catch (error) {
      console.log(`❌ Error saving .env: ${error.message}`);
    }
  }

  async editDockerCompose(rl) {
    console.log('📝 Editing docker-compose.yml Configuration\n');
    
    const filepath = path.join(this.projectRoot, this.configFiles.dockerCompose);
    
    if (!fs.existsSync(filepath)) {
      console.log('❌ docker-compose.yml not found. Creating new one...');
      
      const dockerComposeContent = `version: '3.8'

services:
  trading-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  database:
    image: postgres:15
    environment:
      POSTGRES_DB: trading_db
      POSTGRES_USER: trading_user
      POSTGRES_PASSWORD: trading_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
`;
      
      try {
        fs.writeFileSync(filepath, dockerComposeContent);
        console.log('✅ New docker-compose.yml created!');
      } catch (error) {
        console.log(`❌ Error creating docker-compose.yml: ${error.message}`);
        return;
      }
    }

    console.log('Current docker-compose.yml configuration:');
    try {
      const content = fs.readFileSync(filepath, 'utf-8');
      console.log(content);
    } catch (error) {
      console.log(`❌ Error reading docker-compose.yml: ${error.message}`);
    }
  }

  async createNewConfig(rl) {
    console.log('🆕 Create New Configuration\n');
    
    const configType = await this.question(rl, 'Configuration type (julenrc/amp/env/docker): ');
    const configName = await this.question(rl, 'Configuration name: ');
    
    if (!configName.trim()) {
      console.log('❌ Configuration name cannot be empty.');
      return;
    }

    let configContent = '';
    let filename = '';

    switch (configType.toLowerCase()) {
      case 'julenrc':
        filename = `.${configName}.rc`;
        configContent = JSON.stringify({
          name: configName,
          version: '1.0.0',
          plugins: [],
          commands: {},
          created: new Date().toISOString()
        }, null, 2);
        break;
        
      case 'amp':
        filename = `${configName}_config.json`;
        configContent = JSON.stringify({
          name: configName,
          version: '1.0.0',
          trading_mode: 'demo',
          risk_level: 'medium',
          created: new Date().toISOString()
        }, null, 2);
        break;
        
      case 'env':
        filename = `.${configName}.env`;
        configContent = `# ${configName} Environment Configuration
# Created: ${new Date().toISOString()}
NODE_ENV=development
`;
        break;
        
      case 'docker':
        filename = `docker-compose.${configName}.yml`;
        configContent = `version: '3.8'

# ${configName} Docker Configuration
# Created: ${new Date().toISOString()}

services:
  ${configName}-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=development
`;
        break;
        
      default:
        console.log('❌ Invalid configuration type.');
        return;
    }

    try {
      const filepath = path.join(this.projectRoot, filename);
      fs.writeFileSync(filepath, configContent);
      console.log(`✅ New configuration created: ${filename}`);
    } catch (error) {
      console.log(`❌ Error creating configuration: ${error.message}`);
    }
  }

  async backupConfigurations() {
    console.log('💾 Backing Up Configurations\n');
    
    const backupDir = path.join(this.projectRoot, 'config_backup');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    try {
      if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
      }
      
      const backupPath = path.join(backupDir, `backup_${timestamp}`);
      fs.mkdirSync(backupPath, { recursive: true });
      
      let backupCount = 0;
      
      for (const [name, filename] of Object.entries(this.configFiles)) {
        const sourcePath = path.join(this.projectRoot, filename);
        if (fs.existsSync(sourcePath)) {
          const destPath = path.join(backupPath, filename);
          fs.copyFileSync(sourcePath, destPath);
          backupCount++;
          console.log(`✅ Backed up: ${filename}`);
        }
      }
      
      console.log(`\n✅ Backup completed! ${backupCount} files backed up to: ${backupPath}`);
      
    } catch (error) {
      console.log(`❌ Backup failed: ${error.message}`);
    }
  }

  async validateConfigurations() {
    console.log('🔍 Validating Configurations\n');
    
    const results = [];
    
    for (const [name, filename] of Object.entries(this.configFiles)) {
      const filepath = path.join(this.projectRoot, filename);
      const result = { name, filename, valid: false, errors: [] };
      
      if (!fs.existsSync(filepath)) {
        result.errors.push('File does not exist');
        results.push(result);
        continue;
      }
      
      try {
        if (filename.endsWith('.json')) {
          const content = fs.readFileSync(filepath, 'utf-8');
          JSON.parse(content);
          result.valid = true;
        } else if (filename.endsWith('.yml') || filename.endsWith('.yaml')) {
          // Basic YAML validation (check if file can be read)
          const content = fs.readFileSync(filepath, 'utf-8');
          if (content.trim()) {
            result.valid = true;
          } else {
            result.errors.push('File is empty');
          }
        } else if (filename.startsWith('.')) {
          // .env file validation
          const content = fs.readFileSync(filepath, 'utf-8');
          const lines = content.split('\n');
          let hasValidContent = false;
          
          for (const line of lines) {
            if (line.includes('=') && !line.startsWith('#')) {
              hasValidContent = true;
              break;
            }
          }
          
          if (hasValidContent) {
            result.valid = true;
          } else {
            result.errors.push('No valid environment variables found');
          }
        } else {
          result.valid = true;
        }
      } catch (error) {
        result.errors.push(error.message);
      }
      
      results.push(result);
    }
    
    // Display results
    console.log('Validation Results:');
    console.log('─'.repeat(50));
    
    for (const result of results) {
      if (result.valid) {
        console.log(`✅ ${result.filename}: Valid`);
      } else {
        console.log(`❌ ${result.filename}: Invalid`);
        result.errors.forEach(error => {
          console.log(`   - ${error}`);
        });
      }
    }
    
    const validCount = results.filter(r => r.valid).length;
    const totalCount = results.length;
    
    console.log(`\n📊 Summary: ${validCount}/${totalCount} configurations are valid`);
  }

  async run() {
    console.log('🚀 Starting Configuration Manager...\n');
    await this.showMainMenu();
  }
}

const plugin = new ConfigManagerPlugin();

export default {
  description: plugin.description,
  run: (config) => plugin.run()
};