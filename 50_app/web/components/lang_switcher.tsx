"use client";

import { useState, useEffect } from "react";
import {
  LangAxisState,
  InterfaceLang,
  TargetDialect,
  Envir,
  DEFAULT_LANG_AXIS,
  loadLangAxis,
  saveLangAxis,
} from "@/lib/learner_state";

/**
 * Trilingual + envir 3-axis language switcher per D-065 research UX gap #3.
 *
 * Three independent axes:
 * - interface_lang (en/es/kr) — chrome / UI language
 * - target_dialect (cab + per-region variants) — Garifuna-target lexicon
 * - envir (belize/honduras/.../diaspora) — content per-MOE sovereignty filter
 *
 * Switching any axis NEVER resets learner state (per Hillside PLoP 2022 +
 * Smart Interface Design Patterns 2025).
 */

const INTERFACE_LANGS: [InterfaceLang, string][] = [
  ["en", "English"],
  ["es", "Español"],
  ["kr", "Belize Kriol"],
];

const TARGET_DIALECTS: [TargetDialect, string][] = [
  ["cab", "Pan-Garifuna (canonical)"],
  ["cab-bz", "cab-bz (Belize)"],
  ["cab-hn", "cab-hn (Honduras)"],
  ["cab-gt", "cab-gt (Guatemala)"],
  ["cab-ni", "cab-ni (Nicaragua)"],
  ["cab-svg", "cab-svg (SVG / Yurumein)"],
];

const ENVIRS: [Envir, string][] = [
  ["belize", "Belize"],
  ["honduras", "Honduras"],
  ["guatemala", "Guatemala"],
  ["nicaragua", "Nicaragua"],
  ["svg_yurumein", "SVG / Yurumein"],
  ["garicomm", "GariComm canonical"],
  ["diaspora", "Diaspora"],
];

export function LangSwitcher() {
  const [state, setState] = useState<LangAxisState>(DEFAULT_LANG_AXIS);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setState(loadLangAxis());
  }, []);

  const update = (patch: Partial<LangAxisState>) => {
    const next = { ...state, ...patch };
    setState(next);
    saveLangAxis(next);
  };

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setOpen(!open)}
        className="rounded-md border px-3 py-1.5 text-sm hover:bg-muted"
        aria-haspopup="true"
        aria-expanded={open}
      >
        {labelFor(state)}
      </button>

      {open && (
        <div
          className="absolute right-0 mt-2 w-72 rounded-md border bg-card p-4 shadow-lg"
          role="dialog"
          aria-label="Language and dialect selection"
        >
          <div className="space-y-4">
            <div>
              <div className="mb-1 text-xs font-medium uppercase text-muted-foreground">
                Interface language
              </div>
              <select
                value={state.interface_lang}
                onChange={(e) => update({ interface_lang: e.target.value as InterfaceLang })}
                className="w-full rounded border px-2 py-1.5 text-sm"
                aria-label="Interface language"
              >
                {INTERFACE_LANGS.map(([v, label]) => (
                  <option key={v} value={v}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <div className="mb-1 text-xs font-medium uppercase text-muted-foreground">
                Target dialect
              </div>
              <select
                value={state.target_dialect}
                onChange={(e) => update({ target_dialect: e.target.value as TargetDialect })}
                className="w-full rounded border px-2 py-1.5 text-sm"
                aria-label="Target dialect"
              >
                {TARGET_DIALECTS.map(([v, label]) => (
                  <option key={v} value={v}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <div className="mb-1 text-xs font-medium uppercase text-muted-foreground">
                Community (envir)
              </div>
              <select
                value={state.envir}
                onChange={(e) => update({ envir: e.target.value as Envir })}
                className="w-full rounded border px-2 py-1.5 text-sm"
                aria-label="Community envir"
              >
                {ENVIRS.map(([v, label]) => (
                  <option key={v} value={v}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={() => setOpen(false)}
              className="mt-2 w-full rounded-md bg-primary px-3 py-1.5 text-sm text-primary-foreground"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function labelFor(state: LangAxisState): string {
  const lang = INTERFACE_LANGS.find(([v]) => v === state.interface_lang)?.[1] ?? state.interface_lang;
  const dialect = state.target_dialect.toUpperCase();
  return `${lang} · ${dialect}`;
}
