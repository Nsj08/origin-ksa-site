export function tradeQuery(code: string, year: number): string {
  const target = new URL('https://comtradeapi.un.org/public/v1/preview/C/A/HS');
  target.search = new URLSearchParams({
    period: String(year), reporterCode: '682', flowCode: 'M', cmdCode: code,
    partner2Code: '0', customsCode: 'C00', motCode: '0', maxRecords: '500', includeDesc: 'true',
  }).toString();
  return target.href;
}
