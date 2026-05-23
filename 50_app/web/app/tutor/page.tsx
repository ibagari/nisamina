"use client";

import { useState } from "react";

/**
 * Socratic Tutor UI surface — per D-069 + D-064 SocraticTutor.
 *
 * Demonstrates the tutor's pathway-aware scaffolding + KGRAPH prereq surfacing.
 * Production wires to chatbot orchestrator `start_tutor_session` + `next_turn`
 * via a thin API; this page shows sample dialogue.
 */

type ScaffoldLevel = "open" | "guiding" | "hinted" | "modeled" | "direct_instruct";

interface SampleTurn {
  turn_id: string;
  target_headword: string;
  scaffold_level: ScaffoldLevel;
  prompt_text: string;
  expected_response_kind: "free_text" | "multiple_choice";
  options?: string[];
}

const SCAFFOLD_LABELS: Record<ScaffoldLevel, string> = {
  open: "Open question",
  guiding: "Guided question",
  hinted: "With hint",
  modeled: "Worked example first",
  direct_instruct: "Direct instruction",
};

const SAMPLE_INITIAL_TURN: SampleTurn = {
  turn_id: "tutor.demo.buguya.1",
  target_headword: "buguya",
  scaffold_level: "open",
  prompt_text:
    "(Think about your family or community — when have you heard this word used?) What does 'buguya' mean to you? Tell me in your own words.",
  expected_response_kind: "free_text",
};

export default function TutorPage() {
  const [history, setHistory] = useState<{ role: "tutor" | "learner"; text: string }[]>([
    { role: "tutor", text: SAMPLE_INITIAL_TURN.prompt_text },
  ]);
  const [currentScaffold, setCurrentScaffold] = useState<ScaffoldLevel>("open");
  const [draft, setDraft] = useState("");

  const submit = () => {
    if (!draft.trim()) return;
    const learnerText = draft;
    setDraft("");
    setHistory((h) => [...h, { role: "learner", text: learnerText }]);

    // Demo: if response contains "thank" or similar, scaffold relaxes; else tightens
    const isCorrect = /thank|gratitude|dear/i.test(learnerText);
    const nextScaffold = isCorrect
      ? relaxScaffold(currentScaffold)
      : tightenScaffold(currentScaffold);
    setCurrentScaffold(nextScaffold);

    const nextPrompt = sampleNextPrompt(nextScaffold, isCorrect);
    setTimeout(() => {
      setHistory((h) => [...h, { role: "tutor", text: nextPrompt }]);
    }, 300);
  };

  return (
    <main id="main-content" className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">Socratic Tutor</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          A grounded AI tutor that scaffolds, not lectures. Per Reiser (2004)
          scaffolding + Kestin &amp; Miller (Harvard 2024) AI-tutor study —
          &gt;2× learning vs traditional active-learning instruction.
        </p>
        <div className="mt-3 inline-flex items-center gap-2 rounded-md border px-3 py-1 text-xs">
          <span className="text-muted-foreground">Current scaffold:</span>
          <span className="font-medium">{SCAFFOLD_LABELS[currentScaffold]}</span>
        </div>
      </header>

      <section className="mb-4 space-y-3 rounded-lg border bg-card p-4">
        {history.map((m, i) => (
          <div
            key={i}
            className={`rounded-md px-3 py-2 ${
              m.role === "tutor"
                ? "bg-primary/5 border-l-4 border-primary"
                : "bg-muted/40 ml-8"
            }`}
          >
            <div className="text-xs font-medium uppercase text-muted-foreground">
              {m.role}
            </div>
            <div className="mt-1 whitespace-pre-wrap">{m.text}</div>
          </div>
        ))}
      </section>

      <div className="flex gap-2">
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submit();
          }}
          placeholder="Type your response..."
          className="flex-1 rounded-md border px-3 py-2"
          aria-label="Your response to the tutor"
        />
        <button
          onClick={submit}
          className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
        >
          Submit
        </button>
      </div>

      <p className="mt-4 text-xs text-muted-foreground">
        🪶 Per <em>Labayayahoun Ibagari</em>: the tutor cites sources via the cite_sources MCP
        tool for every claim it makes. Garifuna terms not in the foundry are routed via
        the Commission elder neologism queue, never invented.
      </p>
    </main>
  );
}

function relaxScaffold(s: ScaffoldLevel): ScaffoldLevel {
  const order: ScaffoldLevel[] = ["open", "guiding", "hinted", "modeled", "direct_instruct"];
  const i = order.indexOf(s);
  return order[Math.max(0, i - 1)];
}

function tightenScaffold(s: ScaffoldLevel): ScaffoldLevel {
  const order: ScaffoldLevel[] = ["open", "guiding", "hinted", "modeled", "direct_instruct"];
  const i = order.indexOf(s);
  return order[Math.min(order.length - 1, i + 1)];
}

function sampleNextPrompt(scaffold: ScaffoldLevel, wasCorrect: boolean): string {
  if (wasCorrect && scaffold === "open") {
    return "Excellent. 'buguya' means 'you' (singular, affectionate). It appears in 'buguya nuani' — a warm sign-off meaning 'thank you, my dear'. Now try: how would you address a group of friends?";
  }
  if (scaffold === "guiding") {
    return "(Step by step.) 'buguya' is used in greetings and family contexts in Garifuna. Can you give an example of a phrase where you might use it?";
  }
  if (scaffold === "hinted") {
    return "(Step by step.) 'buguya' starts with the same sound as the English word — and it expresses a feeling. What feeling does it express?";
  }
  if (scaffold === "modeled") {
    return "(Step by step.) Watch this example: 'buguya nuani' means 'thank you my dear'. Now you try: what does 'buguya' mean on its own?";
  }
  return "(Step by step.) 'buguya' means 'you' (singular, with affection). When you say 'buguya nuani', you're saying 'you, my dear' — a warm, affectionate address. Repeat: 'buguya nuani'.";
}
