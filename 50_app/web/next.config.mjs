// Nisamina V3 web app — Next.js 15 config
// Per M-P3.UI.A — F-034 May 2026 UI standards.

import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    // Server Components default per Next.js 15 + plan v1.1 §2.2 PWA pattern
    serverActions: { bodySizeLimit: "2mb" },
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "huggingface.co" },
      // Cloudflare R2 audio/media per plan v1.1 §1.1
    ],
  },
  // WCAG 2.2 AA compliance — federal April 24 2026 deadline
  // axe-core + Lighthouse CI gates wired via scripts in package.json
};

export default withNextIntl(nextConfig);
