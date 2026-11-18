function normalizeCharacters(value: string): string {
  return value.normalize('NFKC').toLowerCase()
    .replace(/[\u064b-\u065f\u0670\u0640]/g, '')
    .replace(/[أإآٱ]/g, 'ا')
    .replace(/[ىی]/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/[٠-٩۰-۹]/g, (digit) => String(digit.charCodeAt(0) - (digit >= '۰' ? 0x6f0 : 0x660)));
}

function normalizeSeparators(value: string): string {
  return value.replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
}

export function normalize(value: string): string {
  return normalizeSeparators(normalizeCharacters(value));
}

const sizeValue = String.raw`(?:\d+(?:\s*[- ]\s*\d+)?\s*[/⁄]\s*\d+|\d+(?:[.,٫]\d+)?)`;
const sizeUnit = String.raw`(?:mm|inches|inch|in|ملم|مم|بوصه|بوصات)`;
// NFKC folds the inch symbol (double prime) into two single primes.
const inchMark = String.raw`(?:["“”]|′′)`;
const leadingSize = new RegExp(String.raw`^${sizeValue}\s*(?:${inchMark}|${sizeUnit}(?=[^\p{L}\p{N}]|$))`, 'u');
const size = String.raw`${sizeValue}\s*(?:${sizeUnit}|${inchMark})`;
const trailingSize = new RegExp(String.raw`(?:^|[^\p{L}\p{N}])${size}[^\p{L}\p{N}]*$`, 'u');

export function normalizeSearchQuery(value: string): string {
  const query = normalizeCharacters(value).trim();
  return normalizeSeparators(query.replace(leadingSize, '').replace(trailingSize, ''));
}

const genericWaterPumps = new Set([
  'water pump', 'water pumps',
  ...['مضخة', 'مضخات', 'طرمبة', 'طرمبات'].flatMap(noun =>
    ['ماء', 'مياه', 'موية', 'ميه'].flatMap(water =>
      [water, 'ال' + water, 'ل' + water, 'لل' + water].map(form => `${noun} ${form}`)
    )
  ),
].map(normalize));

export function isGenericWaterPump(query: string): boolean {
  return genericWaterPumps.has(query);
}
