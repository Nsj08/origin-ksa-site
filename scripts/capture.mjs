import {chromium} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
const origin=process.env.TEST_ORIGIN || 'http://127.0.0.1:4325';
const output=process.argv[2] || 'reports/screenshots';
const browser=await chromium.launch();
const paths=['','product/848180/','browse/','methods/','questions/','glossary/','about/','impact/','changelog/','privacy/','terms/','404/'];
try {
  for(const width of [360,1280]) {
    const page=await browser.newPage({viewport:{width,height:width===360?740:900},reducedMotion:'reduce'});
    const dir=output+'/chromium-'+width;await mkdir(dir,{recursive:true});
    for(const lang of ['en','ar']) {
      for(const p of [...paths,null]) {
        const dest=p===null?'/':'/'+lang+'/'+p;
        const response=await page.goto(origin+dest); if(!response.ok())throw Error(dest+' '+response.status());
        await page.evaluate(()=>document.fonts.ready);
        await page.screenshot({path:dir+'/'+lang+'-'+(p===null?'chooser':p.split('/')[0]||'home')+'.png',fullPage:true});
      }
    }
    await page.close();
  }
  await writeFile(output+'/capture.json',JSON.stringify({origin,captured:new Date().toISOString(),widths:[360,1280],pagesPerLanguage:paths.length+1},null,2)+'\n');
} finally {await browser.close();}
