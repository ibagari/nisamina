/**
 * Open Badges 3.0 display — per D-069 + D-068 open_badges.py.
 *
 * Visualizes the learner's earned credentials. Production wires this to a
 * thin API that serves issued credentials from the engine; this page shows
 * sample data demonstrating the JSON-LD payload structure.
 */

interface SampleBadge {
  assertion_id: string;
  badge_id: string;
  name: string;
  description: string;
  achievement_kind:
    | "lesson_completion"
    | "mastery_milestone"
    | "cultural_protocol_acknowledgment"
    | "teacher_cpd_completion"
    | "cohort_graduation";
  issued_on: string;
  envir: string;
  evidence_narrative: string;
  cultural_protocol_authority: string | null;
}

const SAMPLE_BADGES: SampleBadge[] = [
  {
    assertion_id: "urn:uuid:sample-001",
    badge_id: "badge.lesson.greetings.day1",
    name: "Day 1 — Greetings",
    description: "Completed the Day 1 Greetings lesson with ≥85% accuracy.",
    achievement_kind: "lesson_completion",
    issued_on: "2026-05-23T10:00:00Z",
    envir: "belize",
    evidence_narrative: "Learner completed 4 units, scored 18/20 across all checks.",
    cultural_protocol_authority: null,
  },
  {
    assertion_id: "urn:uuid:sample-002",
    badge_id: "badge.mastery.body_parts",
    name: "Mastery — Body Parts",
    description: "Reached Bloom-mastery threshold (≥85%) on the 10-headword body-parts set.",
    achievement_kind: "mastery_milestone",
    issued_on: "2026-05-21T15:30:00Z",
    envir: "belize",
    evidence_narrative: "BKT belief ≥0.85 on all 10 headwords across 3 spaced reviews.",
    cultural_protocol_authority: null,
  },
];

const KIND_LABELS: Record<SampleBadge["achievement_kind"], string> = {
  lesson_completion: "Lesson completion",
  mastery_milestone: "Mastery milestone",
  cultural_protocol_acknowledgment: "Cultural acknowledgment",
  teacher_cpd_completion: "Teacher CPD",
  cohort_graduation: "Cohort graduation",
};

export default function BadgesPage() {
  return (
    <main id="main-content" className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">My Badges</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Verifiable digital credentials per Open Badges 3.0 (1EdTech) + W3C
          Verifiable Credentials Data Model 2.0. Each badge carries an
          attribution chain back to its source citation.
        </p>
      </header>

      {SAMPLE_BADGES.length === 0 ? (
        <p className="text-muted-foreground">
          No badges yet — complete a lesson or mastery milestone to earn your first.
        </p>
      ) : (
        <ol className="space-y-4">
          {SAMPLE_BADGES.map((b) => (
            <li
              key={b.assertion_id}
              className="rounded-lg border bg-card p-5"
            >
              <header className="mb-3 flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-2xl">
                  {b.achievement_kind === "lesson_completion" ? "✓"
                    : b.achievement_kind === "mastery_milestone" ? "★"
                    : b.achievement_kind === "cultural_protocol_acknowledgment" ? "🪶"
                    : b.achievement_kind === "teacher_cpd_completion" ? "🎓"
                    : "◆"}
                </div>
                <div className="flex-1">
                  <h2 className="font-semibold leading-tight">{b.name}</h2>
                  <div className="text-xs text-muted-foreground">
                    {KIND_LABELS[b.achievement_kind]} · {b.envir} · {new Date(b.issued_on).toLocaleDateString()}
                  </div>
                </div>
              </header>
              <p className="mb-2 text-sm">{b.description}</p>
              <details className="text-xs">
                <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                  Evidence + credential details
                </summary>
                <div className="mt-2 space-y-1 rounded-md bg-muted/40 p-3 font-mono">
                  <div><strong>Evidence:</strong> {b.evidence_narrative}</div>
                  <div><strong>Assertion:</strong> <code>{b.assertion_id}</code></div>
                  <div><strong>Badge class:</strong> <code>{b.badge_id}</code></div>
                  {b.cultural_protocol_authority && (
                    <div>
                      <strong>Cultural authority:</strong> {b.cultural_protocol_authority}
                    </div>
                  )}
                </div>
              </details>
            </li>
          ))}
        </ol>
      )}
    </main>
  );
}
