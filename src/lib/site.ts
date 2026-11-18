import settings from '../../site.config.json';
export const config = settings;
const target = new URL(import.meta.env.SITE_URL || settings.url);
export function url(path: string = ''): string {
  return target.pathname.replace(/\/$/, '') + '/' + path.replace(/^\/+/, '');
}
export function absolute(path: string = ''): string {
  return new URL(url(path), target.origin).href;
}

/** Static route counting only. Queries and referrers are never included. */
const counter = settings.analytics;
if (counter.provider !== 'none' && counter.provider !== 'goatcounter') {
  throw new Error('Supported analytics providers are none and goatcounter.');
}
if (counter.provider === 'goatcounter' && counter.id && !/^[a-z0-9](?:[a-z0-9-]{0,60}[a-z0-9])?$/.test(counter.id)) {
  throw new Error('Use the GoatCounter site code, without a URL.');
}
export const counterOrigin = counter.provider === 'goatcounter' && counter.id
  ? 'https://' + counter.id + '.goatcounter.com' : '';
if (settings.feedbackFormUrl && new URL(settings.feedbackFormUrl).protocol !== 'https:') {
  throw new Error('The external feedback form must use HTTPS.');
}
if (settings.publicRepositoryUrl && !/^https:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/.test(settings.publicRepositoryUrl)) {
  throw new Error('Use the HTTPS GitHub URL of the public release repository.');
}
if (settings.mailProviderPrivacyUrl) {
  const policy = new URL(settings.mailProviderPrivacyUrl);
  if (policy.protocol !== 'https:' || policy.username || policy.password) {
    throw new Error('Use a public HTTPS privacy policy URL for the verified mailbox provider.');
  }
}

export const privateMailUrl = settings.mailboxEnabled && settings.email ? `mailto:${settings.email}` : '';
export const publicIssuesUrl = !settings.feedbackFormUrl && !privateMailUrl && settings.publicRepositoryUrl
  ? settings.publicRepositoryUrl.replace(/\/$/, '') + '/issues' : '';

export function feedbackUrl(hs6 = ''): string {
  if (settings.feedbackFormUrl) return settings.feedbackFormUrl;
  if (privateMailUrl && hs6) return privateMailUrl + '?subject=' + encodeURIComponent('Origin KSA ' + hs6);
  return privateMailUrl || publicIssuesUrl;
}
