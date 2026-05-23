"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  OnboardingAnswers,
  Envir,
  resolvePathway,
  answersToProfile,
  saveLearnerState,
  Pathway,
} from "@/lib/learner_state";

/**
 * Narrative HL onboarding wizard (per D-065 research UX gap #1; Carreira-Kagan 2018).
 *
 * 4 screens:
 *   1. Family/community speaker signal → has_heritage_speaker_family
 *   2. Self-reported proficiency → self_reported_proficiency
 *   3. Envir selection → envir
 *   4. Confirmation that NAMES the pathway in encouraging language
 *
 * Identity-aware not proficiency-shaming (per Carreira-Kagan + Polinsky-Kagan
 * continuum). No quiz; no leaderboard; no streak pressure.
 */

type Step = 1 | 2 | 3 | 4;

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>(1);
  const [answers, setAnswers] = useState<Partial<OnboardingAnswers>>({});

  const next = () => setStep((s) => (s < 4 ? ((s + 1) as Step) : s));
  const back = () => setStep((s) => (s > 1 ? ((s - 1) as Step) : s));

  const setFamily = (v: OnboardingAnswers["family_speaks"]) =>
    setAnswers((a) => ({ ...a, family_speaks: v }));
  const setProf = (v: OnboardingAnswers["self_proficiency"]) =>
    setAnswers((a) => ({ ...a, self_proficiency: v }));
  const setEnvir = (v: Envir) => setAnswers((a) => ({ ...a, envir: v }));

  // Compute pathway preview once we have all 3 answers
  const previewPathway: Pathway | null =
    answers.family_speaks && answers.self_proficiency && answers.envir
      ? resolvePathway(answersToProfile(answers as OnboardingAnswers, "en"))
      : null;

  const begin = () => {
    if (!answers.family_speaks || !answers.self_proficiency || !answers.envir) return;
    const completedAnswers = answers as OnboardingAnswers;
    const profile = answersToProfile(completedAnswers, "en");
    const pathway = resolvePathway(profile);
    saveLearnerState({ profile, answers: completedAnswers, pathway });
    router.push(`/${completedAnswers.envir}/${pathway}`);
  };

  return (
    <main id="main-content" className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Welcome — let&apos;s find where you are</h1>
        <p className="mt-2 text-muted-foreground">
          A few questions help us shape your path. There are no wrong answers.
        </p>
        <div className="mt-4 flex gap-2" aria-label="Progress">
          {[1, 2, 3, 4].map((n) => (
            <div
              key={n}
              className={`h-2 flex-1 rounded ${
                n <= step ? "bg-primary" : "bg-muted"
              }`}
              aria-current={n === step ? "step" : undefined}
            />
          ))}
        </div>
      </header>

      {step === 1 && (
        <fieldset className="space-y-3">
          <legend className="mb-2 text-xl font-semibold">
            Who in your life speaks Garifuna?
          </legend>
          <OnboardingRadio
            name="family_speaks"
            value="family_fluent"
            label="A family member speaks it fluently"
            current={answers.family_speaks}
            onChange={(v) => setFamily(v as OnboardingAnswers["family_speaks"])}
          />
          <OnboardingRadio
            name="family_speaks"
            value="family_some"
            label="A family member speaks some, mostly with elders"
            current={answers.family_speaks}
            onChange={(v) => setFamily(v as OnboardingAnswers["family_speaks"])}
          />
          <OnboardingRadio
            name="family_speaks"
            value="community"
            label="People in my community speak it"
            current={answers.family_speaks}
            onChange={(v) => setFamily(v as OnboardingAnswers["family_speaks"])}
          />
          <OnboardingRadio
            name="family_speaks"
            value="none_yet"
            label="I'm learning fresh — no Garifuna around me yet"
            current={answers.family_speaks}
            onChange={(v) => setFamily(v as OnboardingAnswers["family_speaks"])}
          />
        </fieldset>
      )}

      {step === 2 && (
        <fieldset className="space-y-3">
          <legend className="mb-2 text-xl font-semibold">
            How comfortable are you with Garifuna right now?
          </legend>
          <p className="mb-3 text-sm text-muted-foreground">
            Be honest — listening and speaking are different. Choose what fits.
          </p>
          <OnboardingRadio
            name="self_proficiency"
            value="none"
            label="I don't know any Garifuna yet"
            current={answers.self_proficiency}
            onChange={(v) => setProf(v as OnboardingAnswers["self_proficiency"])}
          />
          <OnboardingRadio
            name="self_proficiency"
            value="receptive"
            label="I understand some when others speak; I don't speak it much"
            current={answers.self_proficiency}
            onChange={(v) => setProf(v as OnboardingAnswers["self_proficiency"])}
          />
          <OnboardingRadio
            name="self_proficiency"
            value="conversational"
            label="I can have a basic conversation"
            current={answers.self_proficiency}
            onChange={(v) => setProf(v as OnboardingAnswers["self_proficiency"])}
          />
          <OnboardingRadio
            name="self_proficiency"
            value="fluent"
            label="I speak Garifuna comfortably; I want to read + write better"
            current={answers.self_proficiency}
            onChange={(v) => setProf(v as OnboardingAnswers["self_proficiency"])}
          />
        </fieldset>
      )}

      {step === 3 && (
        <fieldset className="space-y-3">
          <legend className="mb-2 text-xl font-semibold">Which community is yours?</legend>
          <p className="mb-3 text-sm text-muted-foreground">
            Each Garifuna community has its own variations — we&apos;ll honor yours.
          </p>
          {(
            [
              ["belize", "Belize"],
              ["honduras", "Honduras"],
              ["guatemala", "Guatemala"],
              ["nicaragua", "Nicaragua"],
              ["svg_yurumein", "Saint Vincent + the Grenadines (Yurumein)"],
              ["garicomm", "Pan-Garifuna (no single community)"],
              ["diaspora", "I'm in the diaspora (US/UK/elsewhere)"],
            ] as [Envir, string][]
          ).map(([envir, label]) => (
            <OnboardingRadio
              key={envir}
              name="envir"
              value={envir}
              label={label}
              current={answers.envir}
              onChange={(v) => setEnvir(v as Envir)}
            />
          ))}
        </fieldset>
      )}

      {step === 4 && previewPathway && (
        <section className="space-y-4 rounded-lg border bg-muted/30 p-6">
          <h2 className="text-2xl font-semibold">Your path</h2>
          {previewPathway === "heritage" && (
            <p>
              You&apos;re on the <strong>Heritage path</strong> — we&apos;ll start with what
              your family already gave you. The pace honors your asymmetric strengths
              (often strong listening; we&apos;ll build speaking + reading from there).
            </p>
          )}
          {previewPathway === "novice" && (
            <p>
              You&apos;re on the <strong>Novice path</strong> — step by step, we&apos;ll
              build this together. Examples first; then practice; then connect to
              your everyday life.
            </p>
          )}
          {previewPathway === "l1_maintainer" && (
            <p>
              You&apos;re on the <strong>L1-maintainer path</strong> — strong oral
              foundation; we&apos;ll deepen literacy, register, and academic Garifuna
              alongside the cultural roots you already carry.
            </p>
          )}
          <p className="text-sm text-muted-foreground">
            You can change your path any time from Settings. The platform never
            judges your starting point.
          </p>
        </section>
      )}

      <div className="mt-8 flex gap-2">
        {step > 1 && (
          <button
            onClick={back}
            className="rounded-md border px-4 py-2 hover:bg-muted"
          >
            Back
          </button>
        )}
        <div className="flex-1" />
        {step < 4 && (
          <button
            onClick={next}
            disabled={!canAdvance(step, answers)}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:opacity-40"
          >
            Next
          </button>
        )}
        {step === 4 && previewPathway && (
          <button
            onClick={begin}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
          >
            Begin learning
          </button>
        )}
      </div>
    </main>
  );
}

function canAdvance(step: Step, answers: Partial<OnboardingAnswers>): boolean {
  if (step === 1) return !!answers.family_speaks;
  if (step === 2) return !!answers.self_proficiency;
  if (step === 3) return !!answers.envir;
  return false;
}

interface RadioProps {
  name: string;
  value: string;
  label: string;
  current: string | undefined;
  onChange: (v: string) => void;
}

function OnboardingRadio({ name, value, label, current, onChange }: RadioProps) {
  const selected = current === value;
  return (
    <label
      className={`flex cursor-pointer items-start gap-3 rounded-md border p-3 transition ${
        selected ? "border-primary bg-primary/10" : "hover:bg-muted"
      }`}
    >
      <input
        type="radio"
        name={name}
        value={value}
        checked={selected}
        onChange={() => onChange(value)}
        className="mt-1"
        aria-label={label}
      />
      <span>{label}</span>
    </label>
  );
}
