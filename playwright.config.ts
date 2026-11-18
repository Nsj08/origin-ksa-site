import { defineConfig } from '@playwright/test';
const target = process.env.TEST_ORIGIN || 'http://127.0.0.1:4322';
export default defineConfig({
  testDir: './tests/browser', timeout: 90000, retries: 0, workers: 2,
  reporter: [['list'],['json',{outputFile:'reports/browser-results.json'}]],
  use: {baseURL:target, trace:'retain-on-failure', reducedMotion:'reduce'},
  projects: (['chromium','webkit','firefox'] as const).flatMap(browserName =>
    [360,1280].map(width=>({name:browserName+'-'+width,use:{browserName,viewport:{width,height:width===360?740:900}}}))),
  webServer: {command:'python3 scripts/serve.py',url:target,reuseExistingServer:!process.env.CI}
});
