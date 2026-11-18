import { test, expect } from '@playwright/test';

const marker = '<script type="application/json" id="origin-input-marker">"inert"</script>';
for (const lang of ['en', 'ar']) {
  test(lang + ' treats markup in search and URL parameters as text', async ({page}) => {
    await page.goto('/' + lang + '/');
    const requests: string[] = [];
    page.on('request', request => requests.push(request.method() + ' ' + request.url()));
    const input = page.getByRole('combobox');
    await input.fill(marker);
    await expect(page.locator('[data-empty]')).toBeVisible();
    await expect(input).toHaveValue(marker);
    await expect(page.locator('#origin-input-marker')).toHaveCount(0);
    expect(requests.every(entry => entry.startsWith('GET ') && !entry.includes('origin-input-marker'))).toBeTruthy();

    const query = new URLSearchParams({family: marker, q: marker, sort: marker});
    await page.goto('/' + lang + '/browse/?' + query);
    await expect(page.locator('#browse-family')).toBeEnabled();
    await expect(page.locator('#browse-family')).toHaveValue('all');
    await expect(page.getByRole('table')).toHaveCount(2);
    await expect(page.locator('#origin-input-marker')).toHaveCount(0);
    await expect(page.locator('body')).not.toContainText('origin-input-marker');
  });

  test(lang + ' keeps the no-JavaScript search text out of the fallback request', async ({browser, baseURL}) => {
    const context = await browser.newContext({javaScriptEnabled:false, baseURL});
    try {
      const page = await context.newPage();
      await page.goto('/' + lang + '/');
      await page.locator('#product-search').fill(marker);
      await Promise.all([page.waitForURL(url => url.pathname.endsWith('/browse/')), page.locator('.search-submit').click()]);
      expect(new URL(page.url()).searchParams.toString()).toBe('');
      await expect(page.getByRole('table')).toHaveCount(2);
    } finally {
      await context.close();
    }
  });
}
