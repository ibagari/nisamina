"""M-P3.LMS.OPEN_BADGES — Open Badges 3.0 JSON-LD emitter.

Per F-059 D-MAX-8 + 1EdTech Open Badges 3.0 specification (2022; W3C VC Data
Model 2.0 aligned). Emits verifiable digital credentials for:
- lesson completion
- mastery milestones (per Bloom 2-sigma criterion)
- cultural-protocol acknowledgment (e.g., learner completed Beluria-respect intro)
- teacher CPD completion (D-MAX-8)

Per F-055 axis #1 sovereign-presentation: badges include cite_sources_payload
linking to source citations + attribution chain. Per F-031 Commission: badges
are co-signed by Commission authority where the credential references cultural-
heritage content; Kaitiakitanga attribution mandatory.

Scaffolded: cryptographic signing (W3C VC Data Integrity Proofs / Ed25519
JCS-2022) is queued multi-session pending PyNaCl integration; this module emits
unsigned JSON-LD assertions that production signs at issuance time.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import json
import uuid


# Per 1EdTech Open Badges 3.0 spec — required @context URLs
OPEN_BADGES_3_CONTEXT: list[str] = [
    "https://www.w3.org/ns/credentials/v2",
    "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json",
]


class AchievementKind(str, Enum):
    LESSON_COMPLETION = "lesson_completion"
    MASTERY_MILESTONE = "mastery_milestone"
    CULTURAL_PROTOCOL_ACK = "cultural_protocol_acknowledgment"
    TEACHER_CPD = "teacher_cpd_completion"
    COHORT_GRADUATION = "cohort_graduation"


@dataclass(frozen=True)
class CriteriaSpec:
    """Open Badges 3.0 Criteria element."""
    narrative: str                              # human-readable description
    id: Optional[str] = None                    # IRI to criteria definition


@dataclass(frozen=True)
class BadgeClass:
    """Open Badges 3.0 Achievement / BadgeClass definition (not instance)."""
    badge_id: str                               # globally unique IRI fragment
    name: str
    description: str
    achievement_kind: AchievementKind
    criteria: CriteriaSpec
    image: Optional[str] = None                 # IRI to badge image
    tags: tuple[str, ...] = ()
    # Per F-055 axis #1 — every badge has attribution chain
    attribution_refs: tuple[str, ...] = ()
    consent_ref: Optional[str] = None
    cultural_protocol_authority: Optional[str] = None  # e.g., "Commission elder panel"


@dataclass(frozen=True)
class IssuerProfile:
    """Per OB 3.0 — issuer identity."""
    issuer_id: str                              # IRI; e.g., https://nisamina.ibagari.foundation
    name: str
    url: str
    email: Optional[str] = None


@dataclass(frozen=True)
class RecipientIdentifier:
    """Per OB 3.0 — opaque identifier (per privacy_policy.md no-PII rule)."""
    identifier: str                             # hashed actor_id or DID
    identifier_type: str = "didDocument"        # "didDocument" | "email-hash" | "platform-id"


@dataclass(frozen=True)
class AssertionCredential:
    """The actual badge instance issued to a learner."""
    assertion_id: str                           # globally unique
    badge_class: BadgeClass
    issuer: IssuerProfile
    recipient: RecipientIdentifier
    issued_on: str                              # ISO 8601 UTC
    envir: str                                  # which envir issued (per F-055 axis #6)
    evidence_narrative: str = ""                # what the learner did to earn it
    cite_sources_payload: dict = field(default_factory=dict)
    expires_on: Optional[str] = None
    revoked: bool = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# === D-070: PyNaCl Ed25519 signer (W3C VC Data Integrity Proofs) ============


import base64  # noqa: E402


class Ed25519Signer:
    """Ed25519 signer for Open Badges 3.0 VC Data Integrity Proofs.

    Lazy-imports PyNaCl on first use; install with: pip install pynacl.
    Per-issuer keypair; production generates offline + stores private key
    encrypted at rest (file + gpg per F-046).
    """

    def __init__(self, signing_key_bytes: bytes, verification_method_iri: str):
        self._signing_key_bytes = signing_key_bytes
        self.verification_method_iri = verification_method_iri
        self._signing_key = None

    def _ensure_signing_key(self):
        if self._signing_key is not None:
            return
        try:
            from nacl.signing import SigningKey  # type: ignore
        except ImportError as e:
            raise ImportError(
                "PyNaCl required for Ed25519 signing. Install with: pip install pynacl"
            ) from e
        self._signing_key = SigningKey(self._signing_key_bytes)

    def sign_b64(self, message: bytes) -> str:
        """Sign bytes; return base64url-encoded signature."""
        self._ensure_signing_key()
        signed = self._signing_key.sign(message)
        return base64.urlsafe_b64encode(signed.signature).rstrip(b"=").decode("ascii")

    def public_key_b64(self) -> str:
        self._ensure_signing_key()
        return base64.urlsafe_b64encode(bytes(self._signing_key.verify_key)).rstrip(b"=").decode("ascii")

    @classmethod
    def generate(cls, verification_method_iri: str) -> "Ed25519Signer":
        """Generate a fresh Ed25519 keypair. Store the returned signer's
        `_signing_key_bytes` securely (file + gpg encryption per F-046)."""
        try:
            from nacl.signing import SigningKey  # type: ignore
        except ImportError as e:
            raise ImportError(
                "PyNaCl required. Install with: pip install pynacl"
            ) from e
        sk = SigningKey.generate()
        return cls(bytes(sk), verification_method_iri=verification_method_iri)

    @classmethod
    def from_file(cls, path: str, verification_method_iri: str) -> "Ed25519Signer":
        """Load a signing key from a binary file (32 raw bytes)."""
        from pathlib import Path
        with open(Path(path), "rb") as f:
            data = f.read()
        if len(data) != 32:
            raise ValueError(f"Ed25519 signing key must be 32 bytes; got {len(data)}")
        return cls(data, verification_method_iri=verification_method_iri)


def verify_assertion(jsonld_with_proof: dict, public_key_b64: str) -> bool:
    """Verify a signed Open Badges 3.0 JSON-LD assertion. Returns True iff valid."""
    if "proof" not in jsonld_with_proof:
        return False
    proof = jsonld_with_proof["proof"]
    signature_b64 = proof.get("proofValue", "")
    payload = {k: v for k, v in jsonld_with_proof.items() if k != "proof"}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    try:
        from nacl.signing import VerifyKey  # type: ignore
    except ImportError as e:
        raise ImportError(
            "PyNaCl required for Ed25519 verification. Install with: pip install pynacl"
        ) from e
    pad = "=" * (-len(public_key_b64) % 4)
    vk_bytes = base64.urlsafe_b64decode(public_key_b64 + pad)
    sig_pad = "=" * (-len(signature_b64) % 4)
    sig_bytes = base64.urlsafe_b64decode(signature_b64 + sig_pad)
    try:
        VerifyKey(vk_bytes).verify(canonical.encode("utf-8"), sig_bytes)
        return True
    except Exception:  # noqa: BLE001
        return False


def assertion_to_jsonld(assertion: AssertionCredential) -> dict:
    """Convert an AssertionCredential to Open Badges 3.0 JSON-LD form.

    Spec: https://www.imsglobal.org/spec/ob/v3p0/
    """
    return {
        "@context": OPEN_BADGES_3_CONTEXT,
        "type": ["VerifiableCredential", "OpenBadgeCredential"],
        "id": assertion.assertion_id,
        "issuer": {
            "type": ["Profile"],
            "id": assertion.issuer.issuer_id,
            "name": assertion.issuer.name,
            "url": assertion.issuer.url,
            **({"email": assertion.issuer.email} if assertion.issuer.email else {}),
        },
        "validFrom": assertion.issued_on,
        **({"validUntil": assertion.expires_on} if assertion.expires_on else {}),
        "credentialSubject": {
            "type": ["AchievementSubject"],
            "id": assertion.recipient.identifier,
            "identifier": [{
                "type": ["IdentityObject"],
                "identityType": assertion.recipient.identifier_type,
                "identityHash": assertion.recipient.identifier,
            }],
            "achievement": {
                "type": ["Achievement"],
                "id": assertion.badge_class.badge_id,
                "name": assertion.badge_class.name,
                "description": assertion.badge_class.description,
                "achievementType": assertion.badge_class.achievement_kind.value,
                "criteria": {
                    "narrative": assertion.badge_class.criteria.narrative,
                    **({"id": assertion.badge_class.criteria.id}
                       if assertion.badge_class.criteria.id else {}),
                },
                **({"image": assertion.badge_class.image} if assertion.badge_class.image else {}),
                **({"tag": list(assertion.badge_class.tags)}
                   if assertion.badge_class.tags else {}),
            },
        },
        # Extensions per F-055 axis #1 + F-031 Commission attribution
        "nisamina:envir": assertion.envir,
        "nisamina:attributionRefs": list(assertion.badge_class.attribution_refs),
        "nisamina:consentRef": assertion.badge_class.consent_ref,
        "nisamina:culturalProtocolAuthority": assertion.badge_class.cultural_protocol_authority,
        "nisamina:evidenceNarrative": assertion.evidence_narrative,
        "nisamina:citeSourcesPayload": assertion.cite_sources_payload,
        "nisamina:revoked": assertion.revoked,
    }


class BadgeIssuer:
    """Issues Open Badges 3.0 assertions on behalf of a Foundation/Commission.

    Production wires this to:
    - Persistent ledger of issued credentials (append-only per F-046)
    - Cryptographic signing via Ed25519 (W3C VC Data Integrity Proofs;
      eddsa-2022 cryptosuite; per D-070 director approval)
    - Moodle LTI 1.3 + per-MOE LRS for distribution

    Ed25519 signing is OPTIONAL via the `signer` constructor argument; if
    not supplied, assertions are unsigned (suitable for dev/test). Production
    issuers MUST pass a signer for verifiable credentials.
    """

    def __init__(self, issuer: IssuerProfile, signer: Optional["Ed25519Signer"] = None):
        self.issuer = issuer
        self.signer = signer
        self._issued: list[AssertionCredential] = []

    def sign(self, assertion: AssertionCredential) -> dict:
        """Sign a credential per W3C VC Data Integrity Proofs (Ed25519 + eddsa-2022).

        Returns JSON-LD with `proof` block. Requires self.signer; raises
        RuntimeError if no signer configured.
        """
        if self.signer is None:
            raise RuntimeError(
                "BadgeIssuer has no signer; cannot produce verifiable credential. "
                "Construct with `BadgeIssuer(issuer, signer=Ed25519Signer.from_file(...))`."
            )
        jsonld = assertion_to_jsonld(assertion)
        canonical = json.dumps(jsonld, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        signature_b64 = self.signer.sign_b64(canonical.encode("utf-8"))
        jsonld["proof"] = {
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-2022",
            "created": _now_iso(),
            "verificationMethod": self.signer.verification_method_iri,
            "proofPurpose": "assertionMethod",
            "proofValue": signature_b64,
        }
        return jsonld

    def issue(
        self,
        badge_class: BadgeClass,
        recipient: RecipientIdentifier,
        envir: str,
        evidence_narrative: str = "",
        cite_sources_payload: Optional[dict] = None,
        expires_on: Optional[str] = None,
    ) -> AssertionCredential:
        """Issue a new credential. Cultural-heritage badges require elder authority."""
        # Enforce cultural-protocol authority for sacred / cultural-heritage badges
        if badge_class.achievement_kind == AchievementKind.CULTURAL_PROTOCOL_ACK:
            if not badge_class.cultural_protocol_authority:
                raise ValueError(
                    "CULTURAL_PROTOCOL_ACK badge requires cultural_protocol_authority "
                    "(Commission elder panel or named authority) per F-031 + Labayayahoun Ibagari"
                )
        assertion = AssertionCredential(
            assertion_id=f"urn:uuid:{uuid.uuid4()}",
            badge_class=badge_class,
            issuer=self.issuer,
            recipient=recipient,
            issued_on=_now_iso(),
            envir=envir,
            evidence_narrative=evidence_narrative,
            cite_sources_payload=cite_sources_payload or {},
            expires_on=expires_on,
        )
        self._issued.append(assertion)
        return assertion

    def issued(self) -> list[AssertionCredential]:
        return list(self._issued)

    def revoke(self, assertion_id: str) -> bool:
        """Per OB 3.0 + W3C VC revocation; returns True if revoked."""
        for i, a in enumerate(self._issued):
            if a.assertion_id == assertion_id:
                # Frozen dataclass → re-create with revoked=True; append-only
                # log the revocation; original stays as historical record per
                # [[feedback-no-hindsight-whitewashing]]
                revoked_copy = AssertionCredential(
                    assertion_id=a.assertion_id,
                    badge_class=a.badge_class,
                    issuer=a.issuer,
                    recipient=a.recipient,
                    issued_on=a.issued_on,
                    envir=a.envir,
                    evidence_narrative=a.evidence_narrative,
                    cite_sources_payload=a.cite_sources_payload,
                    expires_on=a.expires_on,
                    revoked=True,
                )
                self._issued.append(revoked_copy)
                return True
        return False
