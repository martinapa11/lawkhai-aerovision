"""
High‑level AI tutor orchestration for Lawkhai Aerovision (Phase 1).

This module connects:
- The RAG engine (retrieval over training materials).
- The safety filter (enforcing training‑only, non‑procedural use).

It exposes a simple, backend‑friendly API that the UI or HTTP layer
can call to obtain aviation‑safe, concept‑oriented explanations for
electrical power and hydraulic systems.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .rag_engine import RagEngine
from .safety_filter import SafetyFilter, SafetyDecision


SystemChoice = Literal["electrical", "hydraulic"]


@dataclass
class TutorResponse:
    """
    Structured response from the AI tutor.

    Fields are kept explicit so that calling layers (e.g. Gradio UI)
    can show additional context, such as whether a query was blocked
    for safety reasons.
    """

    answer: str
    system_focus: SystemChoice
    category: str  # from SafetyDecision.category
    blocked: bool  # True if the original answer was overridden


class AiTutor:
    """
    Orchestrates conceptual Q&A for aircraft systems.

    Design principles:
    - The tutor never returns detailed maintenance steps.
    - Answers emphasise system architecture, flows, and fault logic.
    - All outputs are passed through the safety filter.
    - The interface is intentionally simple for Phase 1 and can later
      be extended with richer metadata (citations, diagrams, etc.).
    """

    def __init__(self) -> None:
        self._rag = RagEngine()
        self._safety = SafetyFilter()

    def answer_conceptual_question(
        self,
        question: str,
        system_focus: SystemChoice,
    ) -> TutorResponse:
        """
        Answer a learner's conceptual system question in a safety‑aware way.

        Parameters
        ----------
        question:
            Free‑text question from the learner.
        system_focus:
            'electrical' or 'hydraulic'. Used to guide retrieval and
            encourage thinking in terms of system behaviour.
        """

        # 1. Obtain a concept‑level draft answer from the RAG engine.
        rag_answer = self._rag.answer_question(question=question, system_focus=system_focus)

        # 2. Apply the safety filter to enforce training‑only constraints.
        decision: SafetyDecision = self._safety.apply(
            query=question,
            raw_answer=rag_answer,
            system_focus=system_focus,
        )

        return TutorResponse(
            answer=decision.safe_answer,
            system_focus=system_focus,
            category=decision.category,
            blocked=not decision.allow,
        )


__all__ = ["AiTutor", "TutorResponse", "SystemChoice"]

