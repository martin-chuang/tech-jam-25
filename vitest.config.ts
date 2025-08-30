import { createVitestConfig } from '@lynx-js/react/testing-library/vitest-config';
import { defineConfig, mergeConfig } from 'vitest/config';

const defaultConfig = await createVitestConfig();
const config = defineConfig({
  test: {},
});

export default mergeConfig(defaultConfig, config);
