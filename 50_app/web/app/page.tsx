import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

export default function HomePage() {
  const t = useTranslations();
  return (
    <main id="main-content" className="min-h-screen">
      <header className="border-b border-border bg-secondary">
        <div className="container py-6">
          <p className="text-muted-foreground text-sm">{t("platform.name")} — Phase 3</p>
          <h1 className="font-serif text-4xl md:text-5xl text-foreground mt-2">
            {t("home.title")}
          </h1>
          <p className="text-muted-foreground mt-3 max-w-2xl">
            {t("home.subtitle")}
          </p>
          <div className="flex flex-wrap gap-3 mt-6">
            <a
              href="/onboarding"
              className={cn(
                "inline-flex items-center justify-center rounded-md bg-primary text-primary-foreground",
                "px-5 py-2.5 text-sm font-medium",
                "hover:bg-primary/90 transition-colors",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              )}
            >
              I&apos;m new — show me where to begin
            </a>
            <a
              href="/lexicon"
              className={cn(
                "inline-flex items-center justify-center rounded-md border border-border bg-background",
                "px-5 py-2.5 text-sm font-medium",
                "hover:bg-muted transition-colors",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              )}
            >
              {t("home.cta_explore")}
            </a>
            <a
              href="/tutor"
              className={cn(
                "inline-flex items-center justify-center rounded-md border border-border bg-background",
                "px-5 py-2.5 text-sm font-medium",
                "hover:bg-muted transition-colors",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              )}
            >
              Try the Socratic Tutor
            </a>
          </div>
          <div className="flex flex-wrap gap-2 mt-6 text-xs">
            <span className="inline-block rounded bg-card text-card-foreground border border-border px-2.5 py-1">
              {t("footer.commission")}
            </span>
            <span className="inline-block rounded bg-card text-card-foreground border border-border px-2.5 py-1">
              Cayetano 1992 NGC-Belize
            </span>
            <span className="inline-block rounded bg-primary text-primary-foreground px-2.5 py-1">
              {t("platform.license")}
            </span>
          </div>
        </div>
      </header>

      <section className="container py-12" aria-labelledby="modes-heading">
        <h2 id="modes-heading" className="font-serif text-2xl mb-6">
          Three modes
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(["learner", "practitioner", "heritage"] as const).map((mode) => (
            <article
              key={mode}
              className="bg-card border border-border rounded-lg p-5 hover:border-primary transition-colors"
            >
              <h3 className="font-serif text-lg">{t(`mode.${mode}`)}</h3>
              <p className="text-muted-foreground text-sm mt-2">
                {mode === "learner" && "K-12 + university curriculum-aligned lessons with SRS vocabulary + gamification (M-P3.C)"}
                {mode === "practitioner" && "Full lexicon browser + Cayetano normalize + citation chain (M-P3.UI.B)"}
                {mode === "heritage" && "Heritage + diaspora conversation practice + St. Vincent Yurumein learner path (F-031)"}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section
        className="container py-12 border-t border-border"
        aria-labelledby="cultural-protocol-heading"
      >
        <h2 id="cultural-protocol-heading" className="font-serif text-2xl mb-4">
          {t("cultural_protocol.title")}
        </h2>
        <blockquote className="bg-secondary border-l-4 border-primary px-5 py-4 rounded text-foreground">
          {t("cultural_protocol.principle")}
        </blockquote>
      </section>

      <footer className="border-t border-border bg-foreground text-background mt-12">
        <div className="container py-8 grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
          <div>
            <h3 className="font-serif text-base text-background mb-2">
              {t("footer.attribution_chain")}
            </h3>
            <ul className="space-y-1 opacity-90">
              <li>{t("footer.commission")}</li>
              <li>Cayetano + Stochl + Suazo + et al. (foundry V0.2 contributors)</li>
              <li>Gleisner + Quevedo + Idiáquez (religious anthropology)</li>
              <li>Pratap + Meta AI (MMS-tts-cab voice)</li>
            </ul>
          </div>
          <div>
            <h3 className="font-serif text-base text-background mb-2">
              {t("footer.license")}
            </h3>
            <ul className="space-y-1 opacity-90">
              <li>{t("platform.license")}</li>
              <li>{t("footer.foundation")}</li>
            </ul>
          </div>
          <div>
            <h3 className="font-serif text-base text-background mb-2">
              Authority chain
            </h3>
            <ul className="space-y-1 opacity-90">
              <li>Director: Wamaraga (Shaka Magarada)</li>
              <li>Commission president: Darius Avila</li>
              <li>NGC president: Sheena Zuniga</li>
              <li>{t("footer.foundation")}</li>
            </ul>
          </div>
        </div>
        <div className="container text-center pb-6 opacity-85">
          <p><em>Buguya nuani Wamaraga.</em></p>
        </div>
      </footer>
    </main>
  );
}
