import type { Metadata } from "next";
import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Nisamina · Garifuna Language Platform",
  description:
    "Community-owned Garifuna language and culture learning platform built with the Garifuna Commission on Education and the Ibagari Foundation. Cayetano 1992 NGC-Belize orthography. License: Labayayahoun Ibagari · CC-BY-NC-SA 4.0.",
  applicationName: "Nisamina",
  authors: [{ name: "Ibagari Foundation" }],
  keywords: [
    "Garifuna",
    "Garínagu",
    "language learning",
    "endangered language",
    "indigenous language",
    "Cayetano 1992",
    "UNESCO IDIL",
    "CARE Principles",
    "Belize",
    "Honduras",
    "Guatemala",
    "Nicaragua",
    "St. Vincent",
    "Yurumein",
    "NYC diaspora",
  ],
};

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const messages = await getMessages();
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <NextIntlClientProvider messages={messages}>
          <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 bg-primary text-primary-foreground px-3 py-2 rounded">
            {/* SR-only skip-link; WCAG 2.4.1 */}
            Skip to main content
          </a>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
