/**
 * Lexicon + learning-chart browse.
 *
 * Per D-069: shows the engine's chart catalog summary (29/29 ChartSubject
 * coverage; 40 charts; 182 pending neologisms routed via Commission elder).
 * Production wires this to a thin API that serves catalog from the Python
 * `build_seed_catalog()`; this page currently shows static curated data
 * to demonstrate the surface.
 */

interface ChartSummary {
  chart_id: string;
  title_en: string;
  subject: string;
  tier: "public" | "institutional" | "elder_gated";
  item_count: number;
  pending_neologisms: number;
  grade_bands: string[];
}

// Sample (production: serve from API call to PythonEngine)
const SAMPLE_CHARTS: ChartSummary[] = [
  {
    chart_id: "chart.alphabet.ngc",
    title_en: "Garifuna NGC Alphabet",
    subject: "alphabet",
    tier: "public",
    item_count: 22,
    pending_neologisms: 0,
    grade_bands: ["PreK", "K"],
  },
  {
    chart_id: "chart.numbers.1_10",
    title_en: "Numbers 1–10",
    subject: "numbers",
    tier: "public",
    item_count: 10,
    pending_neologisms: 0,
    grade_bands: ["PreK", "K", "G1-G2"],
  },
  {
    chart_id: "chart.body_parts.basic",
    title_en: "Body Parts",
    subject: "body_parts",
    tier: "public",
    item_count: 10,
    pending_neologisms: 0,
    grade_bands: ["PreK", "K", "G1-G2"],
  },
  {
    chart_id: "chart.family.kinship_basic",
    title_en: "Family Kinship",
    subject: "family_kinship",
    tier: "public",
    item_count: 13,
    pending_neologisms: 2,
    grade_bands: ["PreK", "K", "G1-G2"],
  },
  {
    chart_id: "chart.food.garifuna_caribbean",
    title_en: "Food — hudutu · sere · ereba",
    subject: "food",
    tier: "public",
    item_count: 9,
    pending_neologisms: 2,
    grade_bands: ["K", "G1-G2", "G3-G5"],
  },
  {
    chart_id: "chart.cycle.water",
    title_en: "Water Cycle (NGSS-aligned)",
    subject: "process_cycles",
    tier: "public",
    item_count: 6,
    pending_neologisms: 5,
    grade_bands: ["G1-G2", "G3-G5", "G6-G9"],
  },
  {
    chart_id: "chart.dance_music.cultural",
    title_en: "Dance + music (Garifuna ICH)",
    subject: "dance_music",
    tier: "elder_gated",
    item_count: 6,
    pending_neologisms: 3,
    grade_bands: ["G1-G2", "G3-G5", "G6-G9"],
  },
  {
    chart_id: "chart.cycle.garifuna_cultural",
    title_en: "Garifuna Cultural Cycle (ICH)",
    subject: "process_cycles",
    tier: "elder_gated",
    item_count: 5,
    pending_neologisms: 3,
    grade_bands: ["G3-G5", "G6-G9", "G10-G12"],
  },
];

export default function LexiconPage() {
  return (
    <main id="main-content" className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Lexicon + Learning Charts</h1>
        <p className="mt-2 text-muted-foreground">
          Browse the canonical Garifuna lexicon + 40 trilingual learning charts across
          29 subjects (covers ALPHABET · NUMBERS · BODY · KINSHIP · FOOD · ANIMALS ·
          PLANTS · CYCLES · CULTURAL HERITAGE).
        </p>
        <div className="mt-3 inline-flex gap-2 rounded-md border bg-muted/40 px-3 py-1.5 text-xs">
          <span>40 charts</span>
          <span>·</span>
          <span>29 / 29 subjects</span>
          <span>·</span>
          <span>182 pending neologisms (routed to Commission elder)</span>
        </div>
      </header>

      <div className="mb-4 rounded-md border border-amber-300 bg-amber-50/40 p-3 text-sm dark:border-amber-700 dark:bg-amber-950/30">
        <strong>Elder-gated content</strong>: some charts (dance, music, ceremony)
        require Commission elder authority — those charts surface a referral, not
        specifics. Per <em>Labayayahoun Ibagari</em> + F-031 Commission stewardship.
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SAMPLE_CHARTS.map((c) => (
          <ChartCard key={c.chart_id} chart={c} />
        ))}
      </div>
    </main>
  );
}

function ChartCard({ chart }: { chart: ChartSummary }) {
  const tierBadge =
    chart.tier === "elder_gated"
      ? { label: "Elder-gated", classes: "bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-100" }
      : chart.tier === "institutional"
        ? { label: "Institutional", classes: "bg-blue-100 text-blue-900 dark:bg-blue-900/40 dark:text-blue-100" }
        : { label: "Public", classes: "bg-emerald-100 text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-100" };

  return (
    <article className="rounded-lg border bg-card p-4 transition hover:shadow-md">
      <header className="mb-2 flex items-start justify-between gap-2">
        <h2 className="text-sm font-semibold leading-tight">{chart.title_en}</h2>
        <span
          className={`shrink-0 rounded-full px-2 py-0.5 text-xs ${tierBadge.classes}`}
        >
          {tierBadge.label}
        </span>
      </header>
      <dl className="space-y-1 text-xs text-muted-foreground">
        <div>
          <dt className="inline">Items:</dt>
          <dd className="inline ml-1">{chart.item_count}</dd>
        </div>
        <div>
          <dt className="inline">Pending Garifuna terms:</dt>
          <dd className="inline ml-1">{chart.pending_neologisms}</dd>
        </div>
        <div>
          <dt className="inline">Grade bands:</dt>
          <dd className="inline ml-1">{chart.grade_bands.join(" · ")}</dd>
        </div>
      </dl>
    </article>
  );
}
