#!/usr/bin/env node

import { loadPlugins } from './plugins/utils/pluginLoader.js';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

async function main() {
  const args = process.argv.slice(2);

  const julenrcPath = path.join(process.cwd(), '.julenrc');
  let config = {};
  if (fs.existsSync(julenrcPath)) {
    const julenrcContent = fs.readFileSync(julenrcPath, 'utf-8');
    config = JSON.parse(julenrcContent);
  }

  const plugins = await loadPlugins(config);

  if (args.length === 0 || args[0] === '--help') {
    console.log('Usage: genx-cli <command>');
    console.log('');
    console.log('Commands:');
    console.log('  --list-plugins    List all available plugins');
    console.log('  --run-plugin      Run a specific plugin');
    console.log('');
    console.log('Plugin details:');
    plugins.forEach(plugin => {
      console.log(`  ${plugin.name}: ${plugin.description}`);
    });
    return;
  }

  if (args[0] === '--list-plugins') {
    console.log('Available plugins:');
    plugins.forEach(plugin => {
      console.log(`- ${plugin.name}: ${plugin.description}`);
    });
    return;
  }

  if (args[0] === '--run-plugin') {
    const pluginName = args[1];
    if (!pluginName) {
      console.error('Error: Please specify a plugin to run.');
      return;
    }

    if (pluginName.endsWith('.py')) {
      // Handle Python plugins
      const args = process.argv.slice(3); // Get additional arguments
      const pythonArgs = ['genx-cli/plugins/' + pluginName];
      
      // Add command arguments if provided (skip the plugin name itself)
      if (args.length > 1) {
        pythonArgs.push(args[1]); // Only add the command, not the plugin name
      }
      
      console.log(`Running Python plugin: ${pluginName} with args: ${pythonArgs.join(' ')}`);
      
      const pythonProcess = spawn('python3', pythonArgs);
      pythonProcess.stdout.on('data', (data) => {
        console.log(data.toString());
      });
      pythonProcess.stderr.on('data', (data) => {
        console.error(data.toString());
      });
      
      pythonProcess.on('exit', (code) => {
        if (code !== 0) {
          console.log(`Python plugin exited with code ${code}`);
        }
      });
      return;
    }

    const plugin = plugins.find(p => p.name === pluginName);
    if (!plugin) {
      console.error(`Error: Plugin "${pluginName}" not found.`);
      return;
    }

    plugin.run(config);
    return;
  }

  if (args[0] === 'run' && args[1]) {
    const commandName = args[1];
    const command = config.commands[commandName];

    if (command) {
      const commandProcess = spawn(command, { shell: true });

      commandProcess.stdout.on('data', (data) => {
        console.log(data.toString());
      });

      commandProcess.stderr.on('data', (data) => {
        console.error(data.toString());
      });

      return;
    } else {
      console.error(`Error: Command "${commandName}" not found in .julenrc`);
      return;
    }
  }

  console.error(`Error: Unknown command "${args[0]}"`);
}

main();
