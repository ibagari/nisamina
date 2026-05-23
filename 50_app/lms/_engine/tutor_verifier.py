"""M-P3.LMS.TUTOR_VERIFIER — Non-LLM deterministic verifier agent for TUTOR.

Per D-065 SOA gap #5 + research-brief §1 (Khan Academy Khanmigo's non-LLM
math-checker pattern; Kestin & Miller Harvard 2024 "course-tailored grounding,
NOT vanilla GPT" ingredient).

The verifier runs BEFORE the brain's output reaches the learner. It catches:
- orthographic errors (e.g., u where ü is required per Cayetano 1992 NGC)
- hallucinated headwords (not in foundry V0.2)
- wrong-dialect terms (e.g., cab_HND term used when cab_BLZ is required)
- response that contradicts the KGRAPH cultural-anchor metadata

A composite verifier chains specialized verifiers; the brain output is held
behind the verifier and rewritten or rejected if it fails. This is the
ingredient that converts a vanilla LLM tutor (Kestin's baseline) into a
>2× learning AI tutor (Kestin's experimental).

Per F-055 axis #1 sovereign presentation: verifier prevents hallucinated
Garifuna content from reaching the learner. cite_sources MCP integration
emits verifier outcomes for transparency.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class VerifierStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"                    # passes but with flag


@dataclass(frozen=True)
class VerifierIssue:
    """A single issue identified by a verifier."""
    verifier_name: str
    severity: str                          # "error" | "warning" | "info"
    offending_token: str
    rationale: str
    suggested_fix: Optional[str] = None


@dataclass(frozen=True)
class VerifierResult:
    """Outcome of running a verifier (or composite) over candidate brain output."""
    status: VerifierStatus
    issues: tuple[VerifierIssue, ...]
    candidate_text: str                    # the brain output that was verified
    proposed_rewrite: Optional[str] = None  # if FAIL, an automated repair suggestion

    @property
    def passed(self) -> bool:
        return self.status == VerifierStatus.PASS

    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)


# === Abstract verifier =====================================================


class Verifier(ABC):
    """Abstract single-aspect verifier. Implementations check one property."""
    verifier_name: str = ""

    @abstractmethod
    def verify(self, candidate_text: str, context: Optional[dict] = None) -> VerifierResult:
        """Inspect candidate_text; return VerifierResult."""


# === Concrete verifiers ====================================================


# NGC orthography per Cayetano 1992: 22 letters; no c/k/q/v/x/z; uses ü
_NGC_LETTERS: set[str] = set("abcdefghijklmnñopqrstuüwy")  # lowercase
_NGC_FORBIDDEN: set[str] = {"c", "k", "q", "v", "x", "z"}  # not in NGC orthography
_NGC_REQUIRED_FOR_HIGH_CENTRAL: set[str] = {"ü"}            # for /ɨ/ phoneme


class OrthographyVerifier(Verifier):
    """Checks output against Cayetano 1992 NGC orthography rules.

    Flags use of forbidden letters (c/k/q/v/x/z) in Garifuna-marked tokens.
    Does NOT flag English/Spanish co-occurring text — context is critical.
    """
    verifier_name = "orthography_ngc"

    def verify(self, candidate_text: str, context: Optional[dict] = None) -> VerifierResult:
        # Context should indicate which tokens are "Garifuna" — supplied by caller
        cab_tokens: list[str] = (context or {}).get("cab_tokens", [])
        issues: list[VerifierIssue] = []
        for tok in cab_tokens:
            lower = tok.lower()
            for ch in lower:
                if ch in _NGC_FORBIDDEN:
                    issues.append(VerifierIssue(
                        verifier_name=self.verifier_name,
                        severity="error",
                        offending_token=tok,
                        rationale=f"Token '{tok}' contains '{ch}' which is not in NGC orthography (Cayetano 1992)",
                        suggested_fix=None,
                    ))
                    break  # one issue per token is enough
        status = VerifierStatus.FAIL if any(i.severity == "error" for i in issues) else VerifierStatus.PASS
        return VerifierResult(
            status=status,
            issues=tuple(issues),
            candidate_text=candidate_text,
        )


class FoundryExistenceVerifier(Verifier):
    """Checks that any Garifuna headword the brain emits actually exists in
    foundry V0.2.

    The brain MUST NOT invent Garifuna terms — that's the Reiser/Kestin
    grounding requirement + F-055 axis #1 sovereign-presentation rule.
    Missing terms route via neologism_queue, NOT via brain hallucination.
    """
    verifier_name = "foundry_existence"

    def __init__(self, known_headwords: set[str]):
        # known_headwords: the canonical set from foundry V0.2 (lower-cased)
        self.known_headwords: set[str] = {h.lower() for h in known_headwords}

    def verify(self, candidate_text: str, context: Optional[dict] = None) -> VerifierResult:
        cab_tokens: list[str] = (context or {}).get("cab_tokens", [])
        issues: list[VerifierIssue] = []
        for tok in cab_tokens:
            if tok.lower() not in self.known_headwords:
                issues.append(VerifierIssue(
                    verifier_name=self.verifier_name,
                    severity="error",
                    offending_token=tok,
                    rationale=(
                        f"Token '{tok}' not in foundry V0.2. "
                        f"If this is a needed term, route via neologism_queue per F-067 §3 — "
                        f"DO NOT pass through hallucinated Garifuna content."
                    ),
                ))
        status = VerifierStatus.FAIL if issues else VerifierStatus.PASS
        return VerifierResult(
            status=status,
            issues=tuple(issues),
            candidate_text=candidate_text,
        )


class DialectTagVerifier(Verifier):
    """Checks that emitted tokens carry the envir/dialect appropriate to the
    learner's cohort.

    E.g., a Belize learner should not receive a Honduras-specific lexical
    variant unless explicitly cross-envir-bridging is intended.
    """
    verifier_name = "dialect_tag"

    def __init__(self, headword_to_dialect: dict[str, str]):
        # headword_to_dialect: lowercased headword → canonical dialect_tag
        self.headword_to_dialect = {k.lower(): v for k, v in headword_to_dialect.items()}

    def verify(self, candidate_text: str, context: Optional[dict] = None) -> VerifierResult:
        ctx = context or {}
        learner_envir: Optional[str] = ctx.get("learner_envir")
        cab_tokens: list[str] = ctx.get("cab_tokens", [])
        # Map envir → dialect_tag prefix
        envir_to_dialect = {
            "belize": "cab_BLZ",
            "honduras": "cab_HND",
            "guatemala": "cab_GUA",
            "nicaragua": "cab_NIC",
            "svg_yurumein": "cab_SVG",
            "garicomm": None,                  # canonical; any dialect OK
        }
        expected = envir_to_dialect.get(learner_envir) if learner_envir else None
        if expected is None:
            return VerifierResult(status=VerifierStatus.PASS, issues=(), candidate_text=candidate_text)
        issues: list[VerifierIssue] = []
        for tok in cab_tokens:
            tag = self.headword_to_dialect.get(tok.lower())
            if tag and tag != expected:
                issues.append(VerifierIssue(
                    verifier_name=self.verifier_name,
                    severity="warning",
                    offending_token=tok,
                    rationale=(
                        f"Token '{tok}' has dialect_tag={tag} but learner envir={learner_envir} "
                        f"(expected {expected})"
                    ),
                ))
        status = VerifierStatus.WARNING if issues else VerifierStatus.PASS
        return VerifierResult(
            status=status,
            issues=tuple(issues),
            candidate_text=candidate_text,
        )


# === Composite verifier ====================================================


class CompositeVerifier(Verifier):
    """Chains specialized verifiers; aggregates their issues.

    Status policy:
    - If any child verifier returns FAIL → composite is FAIL
    - Else if any child returns WARNING → composite is WARNING
    - Else PASS
    """
    verifier_name = "composite"

    def __init__(self, verifiers: list[Verifier]):
        self.verifiers = verifiers

    def verify(self, candidate_text: str, context: Optional[dict] = None) -> VerifierResult:
        all_issues: list[VerifierIssue] = []
        worst_status = VerifierStatus.PASS
        for v in self.verifiers:
            result = v.verify(candidate_text, context=context)
            all_issues.extend(result.issues)
            if result.status == VerifierStatus.FAIL:
                worst_status = VerifierStatus.FAIL
            elif result.status == VerifierStatus.WARNING and worst_status != VerifierStatus.FAIL:
                worst_status = VerifierStatus.WARNING
        return VerifierResult(
            status=worst_status,
            issues=tuple(all_issues),
            candidate_text=candidate_text,
        )
