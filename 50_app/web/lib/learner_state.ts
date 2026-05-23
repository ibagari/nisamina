/**
 * Per-D-069: client-side learner state + pathway resolution.
 *
 * Mirrors the Python `PathwayResolver.resolve()` heuristic (50_app/lms/_engine/pathway.py)
 * so onboarding can compute pathway without server round-trip. Server-side
 * `PathwayResolver.resolve()` remains the canonical implementation; this is
 * the UX optimization. State persists to localStorage.
 *
 * Per F-055 axis #6: envir is part of learner state from onboarding; never
 * gets switched away from learner-default without explicit cross-envir consent.
 */

export type Pathway = "heritage" | "novice" | "l1_maintainer";
export type Envir =
  | "belize"
  | "honduras"
  | "guatemala"
  | "nicaragua"
  | "svg_yurumein"
  | "garicomm"
  | "diaspora";
export type InterfaceLang = "en" | "es" | "kr";
export type TargetDialect =
  | "cab"            // canonical / pan-Garifuna
  | "cab-bz"
  | "cab-hn"
  | "cab-gt"
  | "cab-ni"
  | "cab-svg";

export interface OnboardingAnswers {
  family_speaks: "family_fluent" | "family_some" | "community" | "none_yet";
  self_proficiency: "none" | "receptive" | "conversational" | "fluent";
  envir: Envir;
}

export interface LearnerProfile {
  has_heritage_speaker_family: boolean;
  self_reported_proficiency: number; // [0, 1]
  primary_language: InterfaceLang | null;
  envir: Envir;
}

/**
 * Mirror of Python PathwayResolver.resolve() — keep in sync with
 * `50_app/lms/_engine/pathway.py:PathwayResolver.resolve()`.
 */
export function resolvePathway(profile: LearnerProfile): Pathway {
  if (
    profile.self_reported_proficiency >= 0.7 &&
    profile.has_heritage_speaker_family
  ) {
    return "l1_maintainer";
  }
  if (profile.has_heritage_speaker_family && profile.self_reported_proficiency < 0.7) {
    return "heritage";
  }
  return "novice";
}

/** Convert onboarding answers to a LearnerProfile. */
export function answersToProfile(
  answers: OnboardingAnswers,
  interfaceLang: InterfaceLang
): LearnerProfile {
  const has_family =
    answers.family_speaks === "family_fluent" || answers.family_speaks === "family_some";
  const proficiencyMap: Record<OnboardingAnswers["self_proficiency"], number> = {
    none: 0.05,
    receptive: 0.4,
    conversational: 0.6,
    fluent: 0.85,
  };
  return {
    has_heritage_speaker_family: has_family,
    self_reported_proficiency: proficiencyMap[answers.self_proficiency],
    primary_language: interfaceLang,
    envir: answers.envir,
  };
}

// === Persistence (localStorage; private; no PII beyond opaque preferences) ===

const STORAGE_KEY = "nisamina.learner_profile";
const ONBOARDING_KEY = "nisamina.onboarding_answers";
const PATHWAY_KEY = "nisamina.pathway";

export function saveLearnerState(opts: {
  profile: LearnerProfile;
  answers: OnboardingAnswers;
  pathway: Pathway;
}): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(opts.profile));
  window.localStorage.setItem(ONBOARDING_KEY, JSON.stringify(opts.answers));
  window.localStorage.setItem(PATHWAY_KEY, opts.pathway);
}

export function loadLearnerProfile(): LearnerProfile | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as LearnerProfile;
  } catch {
    return null;
  }
}

export function loadPathway(): Pathway | null {
  if (typeof window === "undefined") return null;
  const v = window.localStorage.getItem(PATHWAY_KEY);
  if (v === "heritage" || v === "novice" || v === "l1_maintainer") return v;
  return null;
}

// === A11y preferences (D-069 + a11y.py BandwidthMode + WCAG 2.2 AAA + COGA) ===

export type TextSpacing = "normal" | "loose" | "extra_loose";
export type BandwidthMode = "full" | "audio_only" | "text_only" | "print";

export interface A11yPreferences {
  reduced_motion: boolean;
  text_spacing: TextSpacing;
  dyslexic_font: boolean;
  high_contrast: boolean;
  plain_language: boolean;
  bandwidth_mode: BandwidthMode;
}

const A11Y_KEY = "nisamina.a11y_preferences";

export const DEFAULT_A11Y_PREFERENCES: A11yPreferences = {
  reduced_motion: false,
  text_spacing: "normal",
  dyslexic_font: false,
  high_contrast: false,
  plain_language: false,
  bandwidth_mode: "full",
};

export function saveA11yPreferences(prefs: A11yPreferences): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(A11Y_KEY, JSON.stringify(prefs));
}

export function loadA11yPreferences(): A11yPreferences {
  if (typeof window === "undefined") return DEFAULT_A11Y_PREFERENCES;
  const raw = window.localStorage.getItem(A11Y_KEY);
  if (!raw) return DEFAULT_A11Y_PREFERENCES;
  try {
    return { ...DEFAULT_A11Y_PREFERENCES, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_A11Y_PREFERENCES;
  }
}

// === Lang/dialect/envir 3-axis switcher state ===

export interface LangAxisState {
  interface_lang: InterfaceLang;
  target_dialect: TargetDialect;
  envir: Envir;
}

const LANG_AXIS_KEY = "nisamina.lang_axis";

export const DEFAULT_LANG_AXIS: LangAxisState = {
  interface_lang: "en",
  target_dialect: "cab",
  envir: "garicomm",
};

export function saveLangAxis(state: LangAxisState): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(LANG_AXIS_KEY, JSON.stringify(state));
}

export function loadLangAxis(): LangAxisState {
  if (typeof window === "undefined") return DEFAULT_LANG_AXIS;
  const raw = window.localStorage.getItem(LANG_AXIS_KEY);
  if (!raw) return DEFAULT_LANG_AXIS;
  try {
    return { ...DEFAULT_LANG_AXIS, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_LANG_AXIS;
  }
}
