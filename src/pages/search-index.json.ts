import products from '../data/products.json';
import synonyms from '../data/synonyms.json';
import { url } from '../lib/site';
import { normalize } from '../lib/search-normalize';
import { languages } from '../lib/ui';

export function GET() {
  return Response.json(products.flatMap((product) => {
    const row = synonyms.find((entry) => product.hs6 === entry.hs6);
    const hrefs = { en: url(`en/product/${product.hs6}/`), ar: url(`ar/product/${product.hs6}/`) };
    return languages.flatMap((lang) => [
      ...(row?.[lang] ?? []).map((term) => ({ term, normalized: normalize(term), lang, isAlias: true })),
      ...[product.name[lang], product.hs6].map((term) => ({ term, normalized: normalize(term), lang, isAlias: false })),
    ]).map((entry) => ({ ...entry, hs6: product.hs6, names: product.name, hrefs }));
  }));
}
