import {defineConfig} from 'astro/config';
import {readFileSync} from 'node:fs';
const settings = JSON.parse(readFileSync(new URL('./site.config.json', import.meta.url)));
const target = new URL(process.env.SITE_URL || settings.url);
export default defineConfig({
  site: target.origin,
  base: target.pathname,
  output: 'static',
  trailingSlash: 'always',
  build: { inlineStylesheets: 'never' },
  vite: { css: { transformer: 'postcss' }, build: { assetsInlineLimit: 0, cssMinify: false } },
  devToolbar: {enabled:false},
  server:{port:4321,host:'127.0.0.1'}
});
