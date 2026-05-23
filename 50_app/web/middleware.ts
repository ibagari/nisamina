import createMiddleware from "next-intl/middleware";
import { SUPPORTED_LOCALES, DEFAULT_LOCALE } from "./i18n";

export default createMiddleware({
  locales: SUPPORTED_LOCALES,
  defaultLocale: DEFAULT_LOCALE,
  localePrefix: "as-needed",
});

export const config = {
  // Match all routes except api/static/_next/_vercel
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
