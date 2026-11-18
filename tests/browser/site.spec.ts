import { test, expect } from '@playwright/test';
import { mkdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import settings from '../../site.config.json' with { type: 'json' };
import english from '../../src/i18n/en.json' with { type: 'json' };
import arabic from '../../src/i18n/ar.json' with { type: 'json' };
const issuesUrl = !settings.mailboxEnabled && !settings.feedbackFormUrl && settings.publicRepositoryUrl
  ? settings.publicRepositoryUrl.replace(/\/$/, '') + '/issues' : '';
const products = JSON.parse(readFileSync(new URL('../../src/data/products.json', import.meta.url), 'utf8')) as { hs6: string }[];
const pages=['','product/848180/','browse/','methods/','questions/','glossary/','about/','impact/','changelog/','privacy/','terms/','404/'];
for (const lang of ['en','ar']) {
  const copy = lang === 'ar' ? arabic : english;
  test(lang+' page types, viewport, keyboard and accessibility',async({page},info)=>{
    const axePath=process.env.AXE_PATH;
    if (!axePath) throw new Error('Set AXE_PATH to the separately installed axe-core/axe.min.js. See README.');
    const folder='reports/screenshots/'+info.project.name;
    const failures:string[]=[];
    for (const route of pages) {
      await page.goto('/'+lang+'/'+route);
      await expect(page.locator('html')).toHaveAttribute('lang',lang);
      await expect(page.locator('html')).toHaveAttribute('dir',lang==='ar'?'rtl':'ltr');
      await expect(page.locator('h1')).toHaveCount(1);
      if (!settings.mailboxEnabled) {
        await expect(page.locator('a[href^="mailto:"]')).toHaveCount(0);
        await expect(page.locator('body')).not.toContainText(settings.email);
      }
      if (route === 'about/' || route === 'privacy/') {
        const links = await page.locator('article > ul a').evaluateAll(anchors =>
          anchors.map(anchor => anchor.getAttribute('href')));
        if (route === 'about/') {
          expect(links).toEqual([settings.publicRepositoryUrl].filter(Boolean));
          const contact = page.locator('#contact');
          if (issuesUrl) {
            await expect(contact.getByRole('link', {name:copy['common.publicFeedbackLink']})).toHaveAttribute('href', issuesUrl);
            await expect(contact).toContainText(copy['common.publicFeedbackNotice']);
          }
          if (settings.mailboxEnabled) {
            await expect(contact.locator('a[href^="mailto:"]')).toHaveAttribute('href','mailto:' + settings.email);
          } else {
            await expect(contact).toContainText(copy['common.privateContactUnavailable']);
          }
        } else {
          const policyHosts = ['docs.github.com', 'dgp.sdaia.gov.sa', 'sdaia.gov.sa'];
          if (settings.mailboxEnabled && settings.mailProviderPrivacyUrl) {
            expect(links).toContain(settings.mailProviderPrivacyUrl);
            policyHosts.push(new URL(settings.mailProviderPrivacyUrl).hostname);
          }
          expect(links.map(href => new URL(href!).hostname).sort()).toEqual(policyHosts.sort());
        }
      }
      await page.keyboard.press('Tab');
      expect(await page.locator(':focus').getAttribute('href')).toBe('#main');
      await page.keyboard.press('Enter');
      await page.evaluate(()=>document.fonts.ready);
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
      if (overflow) failures.push(route+' horizontal overflow');
      if (info.project.name.startsWith('chromium')) {
        mkdirSync(folder,{recursive:true});
        await page.screenshot({path:path.join(folder,lang+'-'+(route.split('/')[0]||'home')+'.png'), fullPage:true});
      }
      const code=await import('node:fs/promises').then(fs=>fs.readFile(axePath,'utf8'));
      await page.evaluate(code);
      const results=await page.evaluate(async()=> {
        const api=(window as unknown as {axe:{run: (config:object)=>Promise<{violations:{id:string,impact:string,nodes:{target:string[]}[]}[]}>}}).axe;
        return (await api.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})).violations.filter(x=>x.impact==='serious'||x.impact==='critical');
      });
      if(results.length) failures.push(route+' '+JSON.stringify(results.map(v=>[v.id,v.nodes.map(n=>n.target)])));
    }
    expect(failures).toEqual([]);
  });
  test(lang+' search, language switch, sources, risk, report and print',async({page})=>{
    for (const [term,hs6] of [['ball valve','848180'],['مُضَخَّة غاطسة','841370'],['848130','848130'],['bal valve','848180']]) {
      await page.goto('/'+lang+'/'); const field=page.getByRole('combobox');
      await field.fill(term); await expect(page.getByRole('option').first()).toBeVisible();
      await field.press('Escape'); await expect(page.getByRole('option').first()).not.toBeVisible();
      await field.fill(''); await field.fill(term); await expect(page.getByRole('option').first()).toBeVisible();
      await field.press('ArrowDown'); await field.press('Enter');
      await expect(page).toHaveURL(new RegExp('/product/'+hs6+'/'));
    }
    const target=lang==='en'?'ar':'en';
    await page.locator('header a[lang="'+target+'"]').click();
    await expect(page).toHaveURL(new RegExp('/'+target+'/product/848180/'));
    const cards=page.locator('.answer-grid > *');
    await expect(cards).toHaveCount(4);
    if (page.viewportSize()!.width===360) {
      const box=await cards.nth(1).boundingBox();
      expect(box!.y+box!.height).toBeLessThanOrEqual(page.viewportSize()!.height);
    }
    await cards.nth(2).locator('summary').click();
    await expect(cards.nth(2).locator('details')).toHaveAttribute('open','');
    const control=page.locator('select[name=year]');
    expect(await control.locator('option').count()).toBeGreaterThan(1);
    await control.selectOption({index:1}); const year=await control.inputValue();
    const selected=page.locator('[data-chart-year="'+year+'"]');
    await expect(selected).toBeVisible(); await selected.locator('summary').click(); await expect(selected.locator('table')).toBeVisible();
    await expect(page.locator('#makers')).toBeAttached();
    const correction = page.locator('details.correction-link');
    await correction.locator('summary').click();
    if (issuesUrl) {
      const targetCopy = target === 'ar' ? arabic : english;
      await expect(correction).toContainText(targetCopy['common.publicFeedbackNotice']);
      await expect(correction.getByRole('link', {name:targetCopy['common.publicFeedbackLink']})).toHaveAttribute('href',issuesUrl);
    } else if (settings.feedbackFormUrl) {
      await expect(correction.locator('a').first()).toHaveAttribute('href',settings.feedbackFormUrl);
    } else if (settings.mailboxEnabled) {
      await expect(correction.locator('a')).toHaveAttribute('href','mailto:' + settings.email + '?subject=Origin%20KSA%20848180');
    } else {
      await expect(correction.locator('a')).toHaveCount(0);
    }
    await page.emulateMedia({media:'print'}); await expect(page.locator('h1')).toBeVisible();
  });
  test(lang+' no script and no results',async({browser,page})=>{
    const nojs=await browser.newContext({javaScriptEnabled:false,baseURL:process.env.TEST_ORIGIN||'http://127.0.0.1:4322'});
    const staticPage=await nojs.newPage();
    for (const section of ['','browse/','product/848180/']) {
      await staticPage.goto('/'+lang+'/'+section); await expect(staticPage.getByRole('heading',{level:1})).toBeVisible();
      expect((await staticPage.locator('main').innerText()).length).toBeGreaterThan(80);
      if (section === 'browse/') {
        await expect(staticPage.getByRole('table')).toHaveCount(2);
        await expect(staticPage.getByRole('columnheader')).toHaveCount(10);
        await expect(staticPage.getByRole('rowheader')).toHaveCount(products.length);
        await expect(staticPage.locator('noscript a[href="#valves"]')).toBeVisible();
      }
    }
    await nojs.close();
    await page.goto('/'+lang+'/'); await page.getByRole('combobox').fill('xxqxzzzyy');
    await expect(page.locator('[data-empty]')).toBeVisible();
    await expect(page.locator('[data-empty]').getByRole('link',{name:copy['common.request']})).toHaveAttribute('href','/'+lang+'/about/#contact');
    const result=await page.goto('/missing-resource-test/');expect(result?.status()).toBe(404);
    await expect(page.getByRole('combobox')).toBeVisible();
  });
}

test('chooser, short viewport navigation and route availability', async ({page}, info) => {
  await page.goto('/');
  await expect(page.getByRole('heading', {level:1})).toHaveCount(1);
  for (const lang of ['en','ar']) {
    const option = page.locator(`main a[hreflang="${lang}"]`);
    await expect(option).toHaveAttribute('href', `/${lang}/`);
    if (info.project.name.startsWith('chromium')) {
      const folder = 'reports/screenshots/' + info.project.name;
      mkdirSync(folder,{recursive:true});
      await option.focus();
      await page.screenshot({path:path.join(folder,lang+'-chooser.png'),fullPage:true});
    }
  }
  await page.setViewportSize({width:320,height:640});
  for (const lang of ['en','ar']) {
    await page.goto(`/${lang}/`);
    await page.evaluate(() => document.fonts.ready);
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(320);
    const nav = await page.locator('.language-switch').boundingBox();
    expect(nav!.x + nav!.width).toBeLessThanOrEqual(320);
    const search = await page.getByRole('combobox').boundingBox();
    expect(search!.y + search!.height).toBeLessThan(640);
  }
});

test('search loading, network error and retry', async ({page}) => {
  await page.goto('/en/');
  let release!: () => void;
  const delay = new Promise<void>(resolve => {release = resolve;});
  await page.route('**/search-index.json', async route => {
    await delay;
    await route.abort('internetdisconnected');
  }, {times:1});
  const search = page.getByRole('combobox');
  await search.fill('ball valve');
  await expect(page.locator('[data-loading]')).toBeVisible();
  release();
  await expect(page.locator('[data-error]')).toBeVisible();
  await expect(page.locator('[data-error] a')).toHaveAttribute('href','/en/browse/');
  await search.fill('check valve');
  await expect(page.getByRole('option').first()).toHaveAttribute('href','/en/product/848130/');
});

test('browse filter, descending supplier shares, and CSV download', async ({page,request}) => {
  await page.goto('/ar/browse/?family=valves');
  await expect(page.locator('#pumps')).toBeHidden();
  await expect(page.locator('#valves')).toBeVisible();
  await expect(page.getByRole('columnheader')).toHaveCount(5);
  const codes = page.locator('#valves [data-code]');
  const initialOrder = await codes.evaluateAll(rows => rows.map(row => row.getAttribute('data-code')));
  await page.locator('#browse-sort').selectOption('share');
  const shares = await page.locator('#valves [data-share]').evaluateAll(rows =>
    rows.map(row => Number(row.getAttribute('data-share'))));
  expect(shares.length).toBeGreaterThan(1);
  expect(shares).toEqual([...shares].sort((a,b) => b-a));
  await page.locator('#browse-sort').selectOption('name');
  expect(await codes.evaluateAll(rows => rows.map(row => row.getAttribute('data-code')))).toEqual(initialOrder);
  await page.locator('#browse-family').selectOption('pumps');
  await expect(page.locator('#valves')).toBeHidden();
  await expect(page.locator('#pumps')).toBeVisible();
  const csv = await request.get('/indicators.csv');
  expect(csv.ok()).toBe(true);
  expect(await csv.text()).toContain('"top_supplier_share"');
});

test('English and Arabic print summaries fit one A4 page', async ({page, browserName}, info) => {
  test.skip(browserName !== 'chromium' || !info.project.name.endsWith('-360'), 'PDF is supported in Chromium; the mobile project checks both locales.');
  await page.emulateMedia({media:'print'});
  for (const lang of ['en','ar']) {
    for (const {hs6} of products) {
      const route = `/${lang}/product/${hs6}/`;
      await page.goto(route);
      await page.evaluate(() => document.fonts.ready);
      const pdf = await page.pdf({format:'A4', preferCSSPageSize:true});
      expect.soft(pdf.toString('latin1'), route).toMatch(/\/Count 1\b/);
    }
  }
});
