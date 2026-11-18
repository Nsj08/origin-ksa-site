import { expect, test } from '@playwright/test';

for (const lang of ['en', 'ar']) {
  test(`${lang} search asks for the pump type when water is the only use given`, async ({ page }) => {
    await page.goto(`/${lang}/`);
    const input = page.getByRole('combobox');
    const message = page.locator('[data-empty] p');
    const refinement = await page.locator('origin-search').getAttribute('data-water');

    for (const term of ['مضخات ماء', 'مضخة موية', 'طرمبة للموية', '٢ بوصة طرمبات المويه', 'water pump 2"', '2 inch water pumps']) {
      await input.fill(term);
      await expect(message).toBeVisible();
      await expect(message).toHaveText(refinement!);
      await expect(page.getByRole('option')).toHaveCount(0);
    }
    await input.press('Enter');
    await expect(page).toHaveURL(`/${lang}/`);
    await expect(message).toHaveText(refinement!);

    for (const term of ['fire pumps', 'مضخات الحريق']) {
      await input.fill(term);
      const result = page.getByRole('option');
      await expect(result).toHaveCount(1);
      await expect(result).toHaveAttribute('href', `/${lang}/product/841370/`);
    }
  });

  test(`${lang} ball valve plurals and sizes resolve to 848180 with keyboard navigation`, async ({ page }) => {
    await page.goto(`/${lang}/`);
    const input = page.getByRole('combobox');
    const result = page.getByRole('option');
    for (const term of [
      'صمامات كروية', 'محابس كروية', 'صمام كروي ٢٥ مم', '٢٥ مم محابس كروية',
      'ball valves', '2 inch ball valve', 'ball valve 1/2 inch', '1-1/2 inch ball valve',
      'ball valve 2"', '2″ ball valve', 'ball valve 2.5 in', 'ball valve (2 in.)',
    ]) {
      await input.fill(term);
      await expect(result).toHaveCount(1);
      await expect(result).toHaveAttribute('href', `/${lang}/product/848180/`);
    }

    await input.press('Escape');
    await expect(result).not.toBeVisible();
    await input.press('ArrowDown');
    await expect(input).toHaveAttribute('aria-activedescendant', 'product-result-848180');
    await input.press('Enter');
    await expect(page).toHaveURL(`/${lang}/product/848180/`);
  });
}
