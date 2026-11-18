import en from '../i18n/en.json';
import ar from '../i18n/ar.json';

export const languages = ['en', 'ar'] as const;
export type Language = typeof languages[number];
type Localized = Record<Language, string>;
type Dictionary = Record<string, string>;
export function t(lang: Language, key: string): string {
  const dictionary: Dictionary = lang === 'ar' ? ar : en;
  return dictionary[key] ?? key;
}

export type Partner = {
  code: string;
  name: Localized;
  value: number;
  share: number;
  unspecified: boolean;
  aggregate?: boolean;
};
export type Year = {
  year: number;
  accessed?: string | null;
  revision?: string | null;
  total: number;
  partners: Partner[];
  top1: number | null;
  top3: number | null;
  hhi: number | null;
  risk: 'low' | 'medium' | 'high' | null;
  reason: string | null;
  scenario: { low: number | null; central: number | null; high: number | null } | null;
};
export type Maker = { name: string; name_ar?: string; claim: string; claim_ar?: string; source: string; checked: string };
export type Product = {
  hs6: string;
  family: 'pumps' | 'valves';
  name: Localized;
  notes: Localized;
  years: Year[];
  source: { url: string; accessed: string | null; revision: string | null };
  makers: Maker[];
  lcgpa: {
    approved: boolean;
    status: 'pending' | 'listed' | 'not_found';
    claim?: string;
    claim_ar?: string;
    source?: string;
    document?: string;
    document_date?: string;
    page?: string;
    checked?: string;
  };
  headroom: { value: number; ratio: number } | null;
};

export function namedPartners(year: Year): Partner[] {
  return year.partners.filter((partner) => !partner.unspecified && !partner.aggregate && partner.code !== 'other')
    .sort((a, b) => b.value - a.value);
}

export function listLabel(product: Product): string {
  if (!product.lcgpa.approved) return 'product.inProgress';
  if (product.lcgpa.status === 'listed') return 'product.listed';
  if (product.lcgpa.status === 'not_found') return 'product.notFound';
  return 'product.inProgress';
}

const numberLocale = (lang: Language) => lang === 'ar' ? 'ar-SA-u-nu-latn' : 'en';
export const number = (value: number, lang: Language) => new Intl.NumberFormat(numberLocale(lang)).format(value);
export const percent = (value: number, lang: Language) => value > 0 && value < .005 ? '<1%' : new Intl.NumberFormat(numberLocale(lang), { style: 'percent', maximumFractionDigits: 0 }).format(value);
export const tableShare = (value: number, lang: Language) => new Intl.NumberFormat(numberLocale(lang), {
  style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1,
}).format(value);
export function wholeDollars(value: number, lang: Language): string {
  if (lang === 'ar') {
    const amount = new Intl.NumberFormat(numberLocale(lang), { maximumFractionDigits: 0 }).format(value);
    return `${amount} ${t(lang,'product.usd')}`;
  }
  return new Intl.NumberFormat(numberLocale(lang), {
    style: 'currency', currency: 'USD', maximumFractionDigits: 0,
  }).format(value);
}
export function money(value: number, lang: Language): string {
  const fraction = new Intl.NumberFormat(numberLocale(lang), { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const millions = value / 1_000_000;
  const amount = millions > 0 && millions < .05 ? `<${fraction.format(.1)}` : fraction.format(millions);
  return `${amount} ${t(lang,'product.usdMillion')}`;
}
