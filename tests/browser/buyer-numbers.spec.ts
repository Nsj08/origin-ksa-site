import { test, expect } from '@playwright/test';
import products from '../../src/data/products.json' with { type: 'json' };

const product = products.find(({hs6}) => hs6 === '848180')!;
const moneyText = (value: number, lang: 'en' | 'ar') => {
  const rounded = Math.round(value).toLocaleString('en-US');
  return lang === 'ar' ? `${rounded} دولار أمريكي` : `$${rounded}`;
};
const shareText = (value: number, lang: 'en' | 'ar') => `${(value * 100).toFixed(1)}${lang === 'ar' ? '٪' : '%'}`;

for (const lang of ['en', 'ar'] as const) {
  test(`buyer tables display whole dollars and one decimal for shares in ${lang}`, async ({page}) => {
    const latest = product.years.at(-1)!;
    await page.goto(`/${lang}/product/${product.hs6}/`);
    const cards = page.locator('.answer-grid article');
    await expect(cards).toHaveCount(4);
    await expect(cards.nth(2).getByRole('heading')).toHaveText(lang === 'ar'
      ? 'إلى أي مدى تعتمد الواردات على دول قليلة؟'
      : 'Do imports rely on a few countries?');
    const evidence = cards.nth(2).locator('summary');
    await evidence.focus();
    await evidence.press('Enter');
    await expect(cards.nth(2).locator('details')).toHaveJSProperty('open', true);

    const trend = page.locator('.trend-pair + details');
    await trend.locator('summary').click();
    const latestTrend = trend.locator('tbody tr').last();
    await expect(latestTrend.locator('td').nth(0)).toHaveText(moneyText(latest.total, lang));
    await expect(latestTrend.locator('td').nth(1)).toHaveText(shareText(latest.top1!, lang));

    for (const year of [latest, product.years.at(-2)!]) {
      await page.locator('select[name="year"]').selectOption(String(year.year));
      const imports = page.locator(`[data-chart-year="${year.year}"] details`);
      await imports.locator('summary').click();
      const first = imports.locator('tbody tr').first();
      await expect(first.locator('td').nth(0)).toHaveText(moneyText(year.partners[0].value, lang));
      await expect(first.locator('td').nth(1)).toHaveText(shareText(year.partners[0].share, lang));
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(await page.evaluate(() => innerWidth));

    await page.goto(`/${lang}/browse/`);
    const productRow = page.locator(`tr[data-code="${product.hs6}"]`);
    await expect(productRow.locator('td').nth(1)).toContainText(shareText(latest.top1!, lang));

    await page.goto(`/${lang}/methods/`);
    const exampleRow = page.locator('.methods-table').first().locator('tbody tr').first();
    const topPartner = latest.partners.filter(p => !p.unspecified && !p.aggregate && p.code !== 'other')
      .sort((a, b) => b.value - a.value)[0];
    await expect(exampleRow.locator('td').nth(0)).toHaveText(moneyText(topPartner.value, lang));
    await expect(exampleRow.locator('td').nth(1)).toHaveText(shareText(topPartner.share, lang));
  });
}
