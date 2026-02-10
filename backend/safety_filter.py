"""
Safety and intent filtering for Lawkhai Aerovision.

This module enforces the core constraints of the project:
- Educational and training use only.
- No step‑by‑step maintenance instructions.
- No real aircraft diagnostics.
- No procedural language (e.g. remove, install, torque, replace).
- Encourage reference to approved manuals and instructors.

The goal is to keep the AI strictly in the role of a
system‑understanding tutor, never an operational maintenance advisor.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

from .config import get_settings
from .compliance_logger import ComplianceLogger


QueryCategory = Literal["conceptual", "procedural", "ambiguous"]


@dataclass
class SafetyDecision:
    """
    Result of applying the safety filter to a user query and model answer.

    - allow: whether the answer may be returned as‑is.
    - category: how we classify the user's intent.
    - safe_answer: the response text after any redaction / reframing
      and with training‑only disclaimers added when appropriate.

    Note: This contains no personal identifiers; logging should also
    avoid user identity to remain privacy‑respectful.
    """

    allow: bool
    category: QueryCategory
    safe_answer: str


class SafetyFilter:
    """
    Simple, extensible safety filter for aviation training use.

    This implementation is intentionally conservative:
    if there is doubt about whether a question is procedural,
    it is treated as such and redirected toward conceptual learning
    and reference to official documentation.
    """

    def __init__(self, logger: ComplianceLogger | None = None) -> None:
        app_settings = get_settings()
        self.settings = app_settings.safety
        self._compliance = logger or ComplianceLogger()

    # ---------- Public API ----------

    def classify_query(self, query: str) -> QueryCategory:
        """
        Classify the learner's query as conceptual, procedural, or ambiguous.

        Heuristics:
        - If the query contains common task verbs (remove, install, torque, etc.),
          we classify it as 'procedural'.
        - If the query clearly asks for explanations of 'how the system works',
          effects of failures, or conceptual flow, we classify it as 'conceptual'.
        - Otherwise, we mark it 'ambiguous' and treat it cautiously.
        """

        text = query.lower()

        # Strong procedural intent patterns (task-based phrasing)
        procedural_patterns = (
            r"\bhow\s+to\b",
            r"\bhow\s+do\s+i\b",
            r"\bwalk\s+me\s+through\b",
            r"\bsteps?\b",
            r"\bprocedure\b",
            r"\bchecklist\b",
            r"\bwhat\s+should\s+i\s+do\b",
            r"\btroubleshoot(ing)?\b",
            r"\bdiagnos(e|is|tic|tics)\b",
            r"\brepair\b",
            r"\bfix\b",
        )
        if any(re.search(p, text) for p in procedural_patterns):
            return "procedural"

        # Blocked verbs are treated as procedural even if phrased as a question.
        if any(verb in text for verb in self.settings.blocked_verbs):
            return "procedural"

        # Conceptual cues (system-understanding language)
        conceptual_cues = (
            "how does",
            "explain",
            "overview",
            "conceptual",
            "why does",
            "what happens when",
            "what happens if",
            "cause effect",
            "fault logic",
            "system architecture",
            "flow of",
            "role of",
        )
        if any(cue in text for cue in conceptual_cues):
            return "conceptual"

        return "ambiguous"

    def apply(
        self,
        query: str,
        raw_answer: str,
        *,
        system_focus: str | None = None,
    ) -> SafetyDecision:
        """
        Apply safety rules to a proposed answer.

        This function does NOT generate content itself; it assumes that
        another module (e.g. the RAG engine) produced `raw_answer`.
        Its job is to:
        - Block or reframe responses that drift into procedural territory.
        - Insert safety disclaimers.
        - Maintain the framing as a learning assistant, not a maintenance tool.
        """

        category = self.classify_query(query)

        if category in ("procedural", "ambiguous"):
            # Fully override model output and redirect to conceptual framing.
            safe_text = self._build_procedural_block_message(query, category)
            self._log_blocked(query=query, category=category, system_focus=system_focus)
            return SafetyDecision(
                allow=False,
                category=category,
                safe_answer=safe_text,
            )

        # For conceptual queries, still attach a safety reminder.
        safe_text = self._wrap_with_disclaimer(raw_answer)
        return SafetyDecision(
            allow=True,
            category=category,
            safe_answer=safe_text,
        )

    # ---------- Internal helpers ----------

    def _log_blocked(self, query: str, category: QueryCategory, system_focus: str | None) -> None:
        """
        Log blocked/redirected queries for safety review without storing
        personal data or operational details.
        """

        reasons = self._derive_block_reasons(query)
        try:
            self._compliance.log_blocked_query(
                query=query,
                category=category,
                reasons=reasons,
                system_focus=system_focus,
            )
        except Exception:
            # Safety enforcement must not depend on the logger.
            return

    def _derive_block_reasons(self, query: str) -> list[str]:
        """
        Produce simple reason codes for why a query was blocked.
        """

        text = query.lower()
        reasons: list[str] = []

        matched_verbs = [v for v in self.settings.blocked_verbs if v in text]
        if matched_verbs:
            reasons.append("blocked_verbs:" + ",".join(sorted(set(matched_verbs))))

        if re.search(r"\bhow\s+to\b", text) or re.search(r"\bhow\s+do\s+i\b", text):
            reasons.append("task_how_to_language")
        if re.search(r"\bsteps?\b|\bprocedure\b|\bchecklist\b", text):
            reasons.append("stepwise_language")
        if re.search(r"\btroubleshoot(ing)?\b|\bdiagnos(e|is|tic|tics)\b", text):
            reasons.append("diagnostic_or_troubleshooting_language")

        if not reasons:
            reasons.append("ambiguous_intent")

        return reasons

    def _build_procedural_block_message(
        self,
        query: str,
        category: QueryCategory,
    ) -> str:
        """
        Generate a training‑oriented response when a query appears
        procedural or ambiguous.

        The answer:
        - Avoids any task steps or real diagnostics.
        - Redirects the learner toward conceptual system understanding.
        - Encourages consulting approved manuals and instructors.
        """

        base_notice = (
            "Lawkhai Aerovision is a training‑only learning assistant for "
            "aircraft system understanding. It cannot provide maintenance "
            "procedures, troubleshooting steps, or real‑world diagnostics.\n\n"
        )

        if category == "procedural":
            guidance = (
                "Your question appears to request task‑level or procedural "
                "guidance. For actual maintenance work, always consult the "
                "approved Aircraft Maintenance Manual (AMM), applicable "
                "regulatory documents, and your instructor or supervising "
                "engineer.\n\n"
                "If you would like to continue using this tool, you can "
                "rephrase your question to focus on:\n"
                "- How the system is designed to operate.\n"
                "- How energy or pressure flows through the system.\n"
                "- What indications or protections are provided conceptually.\n"
            )
        else:
            guidance = (
                "This question is somewhat ambiguous from a safety perspective. "
                "To stay within training‑only limits, the system will not "
                "offer task‑level advice.\n\n"
                "You may instead ask about:\n"
                "- System architecture and major components.\n"
                "- High‑level effects of component failures.\n"
                "- The logic behind protections and redundancy.\n"
            )

        reminder = (
            "\nAlways defer to approved maintenance documentation, local "
            "procedures, and regulatory requirements (e.g., Transport Canada "
            "or equivalent) before performing any maintenance activity."
        )

        # We deliberately do not echo the original query verbatim, to avoid
        # capturing personally identifiable or sensitive operational details.
        return base_notice + guidance + reminder

    def _wrap_with_disclaimer(self, answer: str) -> str:
        """
        Attach a concise, aviation‑appropriate disclaimer to otherwise
        acceptable conceptual content.
        """

        disclaimer = (
            "\n\n---\n"
            "This explanation is for educational and training purposes only. "
            "It is not a substitute for the approved Aircraft Maintenance "
            "Manual (AMM), type‑specific training, or regulatory guidance. "
            "Do not use this system to plan or perform real‑world maintenance."
        )

        return answer.strip() + disclaimer


__all__ = ["SafetyFilter", "SafetyDecision", "QueryCategory"]

