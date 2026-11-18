import data from '../data/products.json';
import {tradeQuery} from './trade';
import { type Product } from './ui';

function renderCsv() {
  const rows = [
    ['hs6','product_en','product_ar','family','year','top_supplier_share','top_three_share','hhi','risk','risk_reason','scenario_low','scenario_central','scenario_high','historical_headroom_usd','historical_headroom_ratio','source','accessed','hs_revision'],
    ...(data as Product[]).flatMap((product) => product.years.map((year) => [
      product.hs6, product.name.en, product.name.ar, product.family, year.year, year.top1, year.top3, year.hhi, year.risk, year.reason,
      year.scenario?.low, year.scenario?.central, year.scenario?.high,
      year === product.years.at(-1) ? product.headroom?.value : null,
      year === product.years.at(-1) ? product.headroom?.ratio : null,
      tradeQuery(product.hs6,year.year), year.accessed ?? product.source.accessed, year.revision ?? product.source.revision,
    ])),
  ];
  const csv = '\ufeff' + rows.map((row) => row.map((cell) => '"' + String(cell ?? '').replaceAll('"','""') + '"').join(',')).join('\r\n') + '\r\n';
  return csv;
}

export const indicatorCsv = renderCsv();
