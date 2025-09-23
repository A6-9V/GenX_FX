import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function loadPlugins(config) {
  const pluginDir = path.join(__dirname, '..');
  const pluginNames = config.plugins || [];
  const plugins = [];

  for (const name of pluginNames) {
    try {
      if (name.endsWith('.py')) {
        plugins.push({ 
          name,
          description: 'Python plugin',
          run: (config) => {
            // For Python plugins, we'll handle them specially in the main CLI
            console.log(`Python plugin ${name} requires special handling`);
          }
        });
      } else {
        const pluginPath = path.join(pluginDir, `${name}.js`);
        const plugin = await import(pathToFileURL(pluginPath).href);
        
        // Ensure the plugin has the required interface
        if (plugin.default && typeof plugin.default.run === 'function') {
          plugins.push({ 
            name, 
            description: plugin.default.description || 'No description',
            run: plugin.default.run
          });
        } else if (typeof plugin.run === 'function') {
          plugins.push({ 
            name, 
            description: plugin.description || 'No description',
            run: plugin.run
          });
        } else {
          console.warn(`Plugin ${name} does not have a valid run function`);
          plugins.push({ 
            name, 
            description: 'Invalid plugin',
            run: () => console.log(`Plugin ${name} is not properly configured`)
          });
        }
      }
    } catch (error) {
      console.error(`Error loading plugin "${name}":`, error);
      // Add a fallback plugin
      plugins.push({ 
        name, 
        description: 'Error loading plugin',
        run: () => console.log(`Plugin ${name} failed to load: ${error.message}`)
      });
    }
  }

  return plugins;
}
