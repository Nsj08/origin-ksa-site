import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { test, expect } from '@playwright/test';

test('real product UI handles missing, stale and single-country fixture data', async ({page}, info) => {
  test.skip(info.project.name !== 'chromium-360', 'The isolated Astro fixture build runs once.');
  const out = mkdtempSync(path.join(tmpdir(), 'origin-browser-fixture-'));
  try {
    execFileSync(process.execPath, [
      'node_modules/astro/bin/astro.mjs', 'build', '--config', 'tests/fixtures/astro.browser.config.mjs',
      '--outDir', out,
    ], {env:{...process.env, SITE_URL:'https://example.invalid', ASTRO_TELEMETRY_DISABLED:'1'}});
    await page.route('https://example.invalid/**', route => {
      const pathname = new URL(route.request().url()).pathname;
      const file = pathname.endsWith('/') ? pathname + 'index.html' : pathname;
      return route.fulfill({path:path.join(out,file)});
    });
    await page.goto('https://example.invalid/en/product/848180/');
    await expect(page.getByRole('heading',{level:1})).toHaveText('Fixture valve with a single supplier');
    await expect(page.locator('.notice')).toContainText('more than two years old');
    await expect(page.locator('.answer-grid article').nth(2)).toContainText('High');
    await expect(page.locator('.bar-row:visible')).toHaveCount(1);
    await expect(page.locator('.bar-row:visible')).toContainText('100%');
    await expect(page.locator('.scenarios dd')).toHaveText(['0%','0%','0%']);
    await page.locator('select[name=year]').selectOption('2000');
    await expect(page.locator('[data-chart-year="2000"]')).toContainText('No import data for this year');
    await expect(page.locator('.bar-row:visible')).toHaveCount(0);
    await page.goto('https://example.invalid/en/product/841311/');
    await expect(page.getByRole('heading',{level:1})).toHaveText('Fixture pump with no data');
    await expect(page.locator('.answer-grid article').nth(1)).toContainText('Not checked yet');
    await expect(page.locator('[data-year-controls]')).toHaveCount(0);
  } finally {
    rmSync(out,{recursive:true,force:true});
  }
});
