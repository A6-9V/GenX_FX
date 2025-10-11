import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['services/server/tests/**/*.test.ts', 'chrome-extension/tests/**/*.test.js'],
  },
});
