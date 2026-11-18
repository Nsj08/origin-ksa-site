import { fileURLToPath } from 'node:url';
import { defineConfig } from 'astro/config';
import base from '../../astro.config.mjs';

const fixture = fileURLToPath(new URL('./browser-products.json', import.meta.url));

export default defineConfig({
  ...base,
  base: '/',
  vite: {
    ...base.vite,
    plugins: [{
      name: 'origin-browser-fixture',
      enforce: 'pre',
      resolveId(id) {
        if (/(?:^|\/)data\/products\.json$/.test(id)) return fixture;
      },
    }],
  },
});
