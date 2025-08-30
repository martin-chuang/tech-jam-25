import { pluginQRCode } from '@lynx-js/qrcode-rsbuild-plugin';
import { pluginReactLynx } from '@lynx-js/react-rsbuild-plugin';
import { defineConfig } from '@lynx-js/rspeedy';
import { pluginTypeCheck } from '@rsbuild/plugin-type-check';

export default defineConfig({
  plugins: [
    pluginQRCode(),
    pluginReactLynx(),
    pluginTypeCheck(),
  ],
  environments: {
    web: {
      output: {
        assetPrefix: '/',
      },
    },
    lynx: {},
  },
});
