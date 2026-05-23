"""Shared LMS engine — used by all 6 envirs (garicomm + belize + honduras + guatemala + nicaragua + svg_yurumein).

Per F-051 6-envir architecture + F-059 Phase B WAVE-2.A foundations:
- lesson_player (M-P3.LMS.B)        — lesson/unit/step state machine
- spaced_repetition (M-P3.LMS.SR)   — FSRS-v5 review scheduling
- caliper (M-P3.LMS.CALIPER)        — IMS Caliper 1.2 analytics events
- olm (M-P3.LMS.OLM)                — Open Learner Model + mastery beliefs

Each envir layers per-MOE sovereignty (F-055 axis #6) + dialect tagging (D-MAX-9).
"""
from .lesson_player import Lesson, Unit, Step, StepKind, LessonState, LessonPlayer
from .spaced_repetition import Card, ReviewSchedule, FSRSScheduler, Rating
from .caliper import CaliperEvent, Actor, Action, DigitalResource, EventBuffer
from .olm import OpenLearnerModel, MasteryBelief, MASTERY_THRESHOLD
from .pathway import (
    PathwayKind, RegisterTier, LearnerProfile, PathwaySpec,
    HERITAGE_PATHWAY, NOVICE_PATHWAY, L1_MAINTAINER_PATHWAY,
    pathway_for, PathwayResolver, PathwayAdapter,
)
from .neologism_queue import NeologismQueue, NeologismRequest, NeologismApproval, RequestStatus
from .stem_lesson_gen import LessonGenerator, ConceptSpec, SourceRef
from .multimodal import (
    AssetKind, ConsentScope, MultimodalAsset, AssetCatalog, make_asset,
)
from .games import (
    GameKind, GameItem, GameSession, make_session, difficulty_for_pathway,
)
from .a11y import (
    ContrastLevel, BandwidthMode, WorkbookSection,
    contrast_ratio, classify_contrast, validate_touch_target,
    render_workbook_markdown, select_assets_for_mode,
    MIN_TOUCH_TARGET_PX,
)
from .charts import (
    ChartSubject, ChartTier, TrilingualGloss, ChartItem, Chart, ChartCatalog,
)
from .chart_seed import build_seed_catalog
from .kgraph import KnowledgeGraph, Node, Edge, NodeKind, EdgeKind
from .mastery import MasteryGate, MasteryGateResult, threshold_for_pathway
from .micro import (
    MicroUnitKind, MicroUnit, MicroSession, DailyMicroDelivery,
    DEFAULT_MICRO_DURATION_MINUTES, MAX_MICRO_DURATION_MINUTES,
)
from .tutor import (
    ScaffoldLevel, TutorTurn, TutorState, SocraticTutor, SocraticBrainCallable,
    CognitiveLoadSignal,
)
from .blocks import (
    BlockRenderContext, RenderedBlock, Score, ProvenanceRef,
    LessonBlock, BlockRegistry, VocabFlashcardBlock,
)
from .lesson_block_player import (
    BlockPlayerState, BlockReference, BlockPlayerSession, LessonBlockPlayer,
)
from .tutor_verifier import (
    VerifierStatus, VerifierIssue, VerifierResult, Verifier,
    OrthographyVerifier, FoundryExistenceVerifier, DialectTagVerifier, CompositeVerifier,
)
from .review_queue import ReviewQueue, ReviewProposal, ReviewDecision, ReviewStatus
from .xapi import XAPIStatement, XAPIEmitter, caliper_to_xapi
from .affect_gentle import (
    EngagementSignal, NudgeKind, Nudge, AffectState, GentleNudgeGenerator,
    DEFAULT_SOFT_NUDGE_MINUTES, DEFAULT_HARD_STOP_MINUTES,
    DEFAULT_GENTLE_RETURN_DAYS, DEFAULT_FRUSTRATION_WINDOW_INCORRECT,
)
from .elder_loop import ElderReviewItemKind, ElderReviewItem, ElderReviewQueue
from .versioned_kgraph import KGEdit, KGraphProposal, VersionedKnowledgeGraph
from .olm import (
    BeliefRevisionStatus, BeliefRevisionProposal, BeliefRevisionResolution,
    NegotiableOLMExtension,
)

__all__ = [
    "Lesson", "Unit", "Step", "StepKind", "LessonState", "LessonPlayer",
    "Card", "ReviewSchedule", "FSRSScheduler", "Rating",
    "CaliperEvent", "Actor", "Action", "DigitalResource", "EventBuffer",
    "OpenLearnerModel", "MasteryBelief", "MASTERY_THRESHOLD",
    "PathwayKind", "RegisterTier", "LearnerProfile", "PathwaySpec",
    "HERITAGE_PATHWAY", "NOVICE_PATHWAY", "L1_MAINTAINER_PATHWAY",
    "pathway_for", "PathwayResolver", "PathwayAdapter",
    "NeologismQueue", "NeologismRequest", "NeologismApproval", "RequestStatus",
    "LessonGenerator", "ConceptSpec", "SourceRef",
    "AssetKind", "ConsentScope", "MultimodalAsset", "AssetCatalog", "make_asset",
    "GameKind", "GameItem", "GameSession", "make_session", "difficulty_for_pathway",
    "ContrastLevel", "BandwidthMode", "WorkbookSection",
    "contrast_ratio", "classify_contrast", "validate_touch_target",
    "render_workbook_markdown", "select_assets_for_mode",
    "MIN_TOUCH_TARGET_PX",
    "ChartSubject", "ChartTier", "TrilingualGloss", "ChartItem", "Chart", "ChartCatalog",
    "build_seed_catalog",
    "KnowledgeGraph", "Node", "Edge", "NodeKind", "EdgeKind",
    "MasteryGate", "MasteryGateResult", "threshold_for_pathway",
    "MicroUnitKind", "MicroUnit", "MicroSession", "DailyMicroDelivery",
    "DEFAULT_MICRO_DURATION_MINUTES", "MAX_MICRO_DURATION_MINUTES",
    "ScaffoldLevel", "TutorTurn", "TutorState", "SocraticTutor", "SocraticBrainCallable",
    "CognitiveLoadSignal",
    "BlockRenderContext", "RenderedBlock", "Score", "ProvenanceRef",
    "LessonBlock", "BlockRegistry", "VocabFlashcardBlock",
    "BlockPlayerState", "BlockReference", "BlockPlayerSession", "LessonBlockPlayer",
    "VerifierStatus", "VerifierIssue", "VerifierResult", "Verifier",
    "OrthographyVerifier", "FoundryExistenceVerifier", "DialectTagVerifier", "CompositeVerifier",
    "ReviewQueue", "ReviewProposal", "ReviewDecision", "ReviewStatus",
    "XAPIStatement", "XAPIEmitter", "caliper_to_xapi",
    "EngagementSignal", "NudgeKind", "Nudge", "AffectState", "GentleNudgeGenerator",
    "DEFAULT_SOFT_NUDGE_MINUTES", "DEFAULT_HARD_STOP_MINUTES",
    "DEFAULT_GENTLE_RETURN_DAYS", "DEFAULT_FRUSTRATION_WINDOW_INCORRECT",
    "ElderReviewItemKind", "ElderReviewItem", "ElderReviewQueue",
    "KGEdit", "KGraphProposal", "VersionedKnowledgeGraph",
    "BeliefRevisionStatus", "BeliefRevisionProposal", "BeliefRevisionResolution",
    "NegotiableOLMExtension",
]
