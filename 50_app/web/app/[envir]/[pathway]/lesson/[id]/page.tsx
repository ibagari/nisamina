"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { loadA11yPreferences, A11yPreferences } from "@/lib/learner_state";

/**
 * Per-envir/per-pathway lesson detail with primary_modality + plain_summary
 * rendering per D-065 UX research + D-066 lesson_player Step extensions.
 */

interface LessonStep {
  step_id: string;
  kind: string;
  headword_garifuna: string | null;
  prompt_text: string;
  correct_response?: string;
  primary_modality: string;
  plain_summary?: string;
}

interface LessonUnit {
  unit_id: string;
  title: string;
  steps: LessonStep[];
}

interface LessonDetail {
  lesson_id: string;
  envir: string;
  pathway: string;
  title_en: string;
  units: LessonUnit[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function LessonPage() {
  const params = useParams<{ envir: string; pathway: string; id: string }>();
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [a11y, setA11y] = useState<A11yPreferences | null>(null);
  const [stepIdx, setStepIdx] = useState(0);
  const [unitIdx, setUnitIdx] = useState(0);

  useEffect(() => {
    if (!params.envir || !params.pathway || !params.id) return;
    fetch(
      `${API_BASE}/api/v1/envir/${params.envir}/pathway/${params.pathway}/lesson/${params.id}`
    )
      .then((r) => {
        if (!r.ok) throw new Error(`API ${r.status}`);
        return r.json();
      })
      .then(setLesson)
      .catch((e) => setError(String(e)));
    setA11y(loadA11yPreferences());
  }, [params]);

  const currentUnit = lesson?.units[unitIdx];
  const currentStep = currentUnit?.steps[stepIdx];

  const next = () => {
    if (!lesson || !currentUnit) return;
    if (stepIdx + 1 < currentUnit.steps.length) {
      setStepIdx((i) => i + 1);
    } else if (unitIdx + 1 < lesson.units.length) {
      setUnitIdx((i) => i + 1);
      setStepIdx(0);
    }
  };

  return (
    <main id="main-content" className="mx-auto max-w-2xl px-4 py-8">
      {error && (
        <div className="mb-4 rounded-md border border-red-300 bg-red-50/40 p-3 text-sm">
          Failed to load lesson: {error}
        </div>
      )}
      {!lesson && !error && (
        <div className="text-muted-foreground">Loading lesson...</div>
      )}
      {lesson && currentStep && (
        <>
          <header className="mb-6">
            <div className="text-xs uppercase text-muted-foreground">
              {lesson.envir.replace(/_/g, " ")} · {lesson.pathway}
            </div>
            <h1 className="text-2xl font-bold">{lesson.title_en}</h1>
            <div className="mt-2 text-sm text-muted-foreground">
              Unit {unitIdx + 1} / {lesson.units.length} · Step {stepIdx + 1} /{" "}
              {currentUnit?.steps.length}
            </div>
          </header>

          <section className="rounded-lg border bg-card p-6">
            <div className="mb-3 inline-flex items-center gap-2 rounded-md border px-2 py-1 text-xs">
              <span className="text-muted-foreground">Modality:</span>
              <span className="font-medium">{currentStep.primary_modality}</span>
              {currentStep.headword_garifuna && (
                <>
                  <span className="text-muted-foreground">·</span>
                  <span className="font-semibold text-primary">
                    {currentStep.headword_garifuna}
                  </span>
                </>
              )}
            </div>
            <p className="text-lg leading-relaxed">{currentStep.prompt_text}</p>

            {a11y?.plain_language && currentStep.plain_summary && (
              <aside className="mt-4 rounded-md border-l-4 border-primary bg-primary/5 px-3 py-2 text-sm">
                <div className="text-xs font-medium uppercase text-primary">
                  Plain summary
                </div>
                <p>{currentStep.plain_summary}</p>
              </aside>
            )}
          </section>

          <div className="mt-6 flex justify-end gap-2">
            <button
              onClick={next}
              className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
            >
              Next step
            </button>
          </div>
        </>
      )}
    </main>
  );
}
