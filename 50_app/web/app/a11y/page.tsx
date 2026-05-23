"use client";

import { useState, useEffect } from "react";
import {
  A11yPreferences,
  DEFAULT_A11Y_PREFERENCES,
  loadA11yPreferences,
  saveA11yPreferences,
  TextSpacing,
  BandwidthMode,
} from "@/lib/learner_state";

/**
 * COGA + WCAG 2.2 AAA accessibility preferences panel.
 *
 * Per D-065 research UX gap #5 (W3C Making Content Usable for People with
 * Cognitive Disabilities + WCAG 2.2 AAA). Settings persist to localStorage;
 * client-side reading layer applies them globally via document classes.
 *
 * Bandwidth mode connects to a11y.py `BandwidthMode` enum + `select_assets_for_mode`.
 */
export default function A11yPanelPage() {
  const [prefs, setPrefs] = useState<A11yPreferences>(DEFAULT_A11Y_PREFERENCES);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setPrefs(loadA11yPreferences());
  }, []);

  // Apply preferences to <html> classes whenever they change
  useEffect(() => {
    if (typeof document === "undefined") return;
    const html = document.documentElement;
    html.classList.toggle("reduced-motion", prefs.reduced_motion);
    html.classList.toggle("high-contrast", prefs.high_contrast);
    html.classList.toggle("dyslexic-font", prefs.dyslexic_font);
    html.classList.toggle("plain-language", prefs.plain_language);
    html.dataset.textSpacing = prefs.text_spacing;
    html.dataset.bandwidthMode = prefs.bandwidth_mode;
  }, [prefs]);

  const save = () => {
    saveA11yPreferences(prefs);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <main id="main-content" className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">Accessibility preferences</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          These settings save to your device. Per WCAG 2.2 AAA + W3C Making
          Content Usable (COGA).
        </p>
      </header>

      <div className="space-y-6">
        <Toggle
          checked={prefs.reduced_motion}
          onChange={(v) => setPrefs({ ...prefs, reduced_motion: v })}
          label="Reduce motion"
          description="Pauses animations + transitions."
        />
        <Toggle
          checked={prefs.dyslexic_font}
          onChange={(v) => setPrefs({ ...prefs, dyslexic_font: v })}
          label="Dyslexia-friendly font"
          description="Uses OpenDyslexic-flavored serif spacing."
        />
        <Toggle
          checked={prefs.high_contrast}
          onChange={(v) => setPrefs({ ...prefs, high_contrast: v })}
          label="High contrast"
          description="Maximum text-background contrast (≥21:1 where feasible)."
        />
        <Toggle
          checked={prefs.plain_language}
          onChange={(v) => setPrefs({ ...prefs, plain_language: v })}
          label="Plain language summaries"
          description="Adds simpler-language summaries next to every lesson step."
        />

        <fieldset className="space-y-2">
          <legend className="font-medium">Text spacing</legend>
          <div className="flex gap-2">
            {(["normal", "loose", "extra_loose"] as TextSpacing[]).map((v) => (
              <button
                key={v}
                onClick={() => setPrefs({ ...prefs, text_spacing: v })}
                className={`rounded-md border px-3 py-1.5 text-sm ${
                  prefs.text_spacing === v
                    ? "border-primary bg-primary/10"
                    : "hover:bg-muted"
                }`}
              >
                {v === "normal" ? "Normal" : v === "loose" ? "Loose (1.5×)" : "Extra loose (2×)"}
              </button>
            ))}
          </div>
        </fieldset>

        <fieldset className="space-y-2">
          <legend className="font-medium">Connection mode</legend>
          <p className="text-sm text-muted-foreground">
            Choose what kinds of media we should send.
          </p>
          <div className="grid grid-cols-2 gap-2">
            {(
              [
                ["full", "Full (audio + video + images)"],
                ["audio_only", "Audio + text only"],
                ["text_only", "Text only"],
                ["print", "Print workbook mode"],
              ] as [BandwidthMode, string][]
            ).map(([v, label]) => (
              <button
                key={v}
                onClick={() => setPrefs({ ...prefs, bandwidth_mode: v })}
                className={`rounded-md border px-3 py-1.5 text-sm text-left ${
                  prefs.bandwidth_mode === v
                    ? "border-primary bg-primary/10"
                    : "hover:bg-muted"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </fieldset>
      </div>

      <div className="mt-8 flex items-center gap-3">
        <button
          onClick={save}
          className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
        >
          Save preferences
        </button>
        {saved && (
          <span className="text-sm text-green-600" role="status">
            ✓ Saved
          </span>
        )}
      </div>
    </main>
  );
}

interface ToggleProps {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
  description: string;
}

function Toggle({ checked, onChange, label, description }: ToggleProps) {
  return (
    <label className="flex cursor-pointer items-start gap-3 rounded-md border p-4 hover:bg-muted/50">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-1 h-5 w-5"
        aria-label={label}
      />
      <div className="flex-1">
        <div className="font-medium">{label}</div>
        <div className="text-sm text-muted-foreground">{description}</div>
      </div>
    </label>
  );
}
