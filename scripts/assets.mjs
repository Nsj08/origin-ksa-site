import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createCanvas, GlobalFonts } from '@napi-rs/canvas';
const read = async (path) => JSON.parse(await readFile(path, 'utf8'));
const products = await read('src/data/products.json');
const settings = await read('site.config.json');
const target = new URL(process.env.SITE_URL || settings.url);
const root = target.href.replace(/\/$/, '');
const dictionary = {en: await read('src/i18n/en.json'), ar: await read('src/i18n/ar.json')};
for (const [family, subset] of [['ibm-plex-sans','latin'], ['ibm-plex-sans-arabic','arabic']]) {
  GlobalFonts.registerFromPath('node_modules/@fontsource/' + family + '/files/' + family + '-' + subset + '-600-normal.woff2', subset === 'latin' ? 'Plex' : 'Plex Arabic');
}
await mkdir('public/og', {recursive:true});
async function shareCard(lang, product) {
  const rtl = lang === 'ar';
  const canvas = createCanvas(1200,630);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#f6f3ee'; ctx.fillRect(0,0,1200,630);
  ctx.fillStyle = '#096b69';
  for (const [x,y] of [[72,58],[84,79],[72,100]]) ctx.fillRect(x,y,56,12);
  ctx.fillStyle = '#102237'; ctx.font = '36px Plex, sans-serif';
  ctx.fillText('Origin KSA',154,99);
  ctx.fillStyle = '#096b69'; ctx.fillRect(72,150,1056,2);
  ctx.direction = rtl ? 'rtl' : 'ltr'; ctx.textAlign = rtl ? 'right' : 'left';
  const edge = rtl ? 1128 : 72;
  const title = product ? product.name[lang] : (dictionary[lang]['home.title'] || 'Origin KSA');
  ctx.font = rtl ? '65px "Plex Arabic",sans-serif' : '65px Plex,sans-serif';
  ctx.fillStyle = '#102237';
  const lines = []; let line = '';
  for (const word of title.split(/\s+/)) {
    const trial = line ? line + ' ' + word : word;
    if (line && ctx.measureText(trial).width > 1010) {lines.push(line);line=word} else line=trial;
  }
  lines.push(line);
  lines.forEach((part,i)=>ctx.fillText(part,edge,276+i*92,1050));
  ctx.direction = 'ltr'; ctx.textAlign = 'left'; ctx.fillStyle = '#096b69'; ctx.font='30px Plex,sans-serif';
  ctx.fillText(product ? 'HS ' + product.hs6 : target.hostname,72,568);
  const file = product ? lang + '-' + product.hs6 : 'site';
  await writeFile('public/og/' + file + '.png',canvas.toBuffer('image/png'));
}
await shareCard('en');
for (const lang of ['en','ar']) for (const p of products) await shareCard(lang,p);
const staticSections = ['','browse/','methods/','questions/','glossary/','about/','impact/','changelog/','privacy/','terms/'];
const routes = ['/', ...['en','ar'].flatMap(lang=>[...staticSections,...products.map(p=>'product/'+p.hs6+'/')].map(route=>'/'+lang+'/'+route))];
const escape = (v)=>v.replaceAll('&','&amp;').replaceAll('<','&lt;');
await writeFile('public/sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+routes.map(r=>'<url><loc>'+escape(root+r)+'</loc></url>').join('\n')+'</urlset>\n');
await writeFile('public/robots.txt','User-agent: *\nAllow: /\nSitemap: '+root+'/sitemap.xml\n');
