// next-intl request-config — per-route locale + message resolution.
// Per F-034 §6 multilingual: English / Garifuna (cab) / Spanish / Kriol (kr).

import { getRequestConfig } from "next-intl/server";

export const SUPPORTED_LOCALES = ["en", "cab", "es", "kr"] as const;
export type Locale = (typeof SUPPORTED_LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "en";

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;
  if (!locale || !SUPPORTED_LOCALES.includes(locale as Locale)) {
    locale = DEFAULT_LOCALE;
  }
  return {
    locale,
    messages: (await import(`./messages/${locale}.json`)).default,
  };
});
