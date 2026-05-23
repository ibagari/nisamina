import type { Config } from "tailwindcss";

// Tailwind v4 design-token-first config
// WCAG 2.2 AA targets: ≥4.5:1 normal text contrast, ≥3:1 UI components,
// touch targets ≥44×44px (SC 2.5.8), focus indicators (SC 2.4.11)

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      colors: {
        // Garifuna-terracotta-adjacent palette (matches LMS demo styles.css)
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: { DEFAULT: "hsl(var(--card))", foreground: "hsl(var(--card-foreground))" },
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
        secondary: { DEFAULT: "hsl(var(--secondary))", foreground: "hsl(var(--secondary-foreground))" },
        muted: { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
        accent: { DEFAULT: "hsl(var(--accent))", foreground: "hsl(var(--accent-foreground))" },
        destructive: { DEFAULT: "hsl(var(--destructive))", foreground: "hsl(var(--destructive-foreground))" },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
      },
      borderRadius: {
        lg: "0.625rem",
        md: "0.5rem",
        sm: "0.375rem",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        serif: ["Iowan Old Style", "Palatino Linotype", "Georgia", "serif"],
        // Dyslexia-friendly toggle option per F-034 §1.6
        dyslexic: ["OpenDyslexic", "Lexend", "Inter", "sans-serif"],
      },
      minHeight: { tap: "2.75rem" /* 44px WCAG 2.5.8 touch */ },
      minWidth: { tap: "2.75rem" },
    },
  },
  plugins: [],
};

export default config;
