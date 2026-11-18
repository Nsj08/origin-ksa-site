import {indicatorCsv} from '../lib/indicators';
export function GET() {
  return new Response(indicatorCsv, {headers:{'content-type':'text/csv; charset=utf-8'}});
}
