"""
Minimal RAG engine abstraction for Lawkhai Aerovision Phase 1.

This module is deliberately lightweight and framework‑agnostic. It defines
an interface that can later be backed by a more sophisticated library
such as LlamaIndex or LangChain, or by a custom in‑house implementation.

Responsibilities (Phase 1 scope):
- Load and index training‑oriented documents from /data.
- Retrieve conceptually relevant chunks for a learner's question.
- Call an LLM to synthesize a high‑level, system‑understanding answer.

Constraints:
- No procedural maintenance content.
- No real aircraft diagnostics.
- Use only training / system‑description materials as sources.

The detailed safety filtering is handled by backend.safety_filter;
this module focuses on retrieval and answer synthesis.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import get_settings


@dataclass
class RetrievedChunk:
    """
    Small unit of retrieved context from the training corpus.

    For transparency, we keep track of:
    - source: file name or logical source id
    - content: the text snippet shown to the language model
    """

    source: str
    content: str


class RagEngine:
    """
    Simple in‑process RAG engine.

    This implementation is intentionally minimal: it demonstrates how
    the AI tutor calls into a retrieval layer without prescribing
    a specific underlying library. You can later replace the internal
    logic with a forked LlamaIndex / LangChain integration while keeping
    the public API the same.
    """

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        settings = get_settings().rag
        self.data_dir: Path = data_dir or settings.data_dir
        self._index_built: bool = False
        self._documents: list[RetrievedChunk] = []

    # ---------- Public API ----------

    def build_index(self) -> None:
        """
        Build a very simple in‑memory "index" over the /data directory.

        Phase 1 goal:
        - Support PDFs, images (stubbed as descriptions), and markdown files.
        - Keep implementation straightforward and inspectable for professors.

        In a production‑quality system, this would:
        - Use a dedicated vector store.
        - Track embeddings and metadata.
        - Support incremental updates.
        """

        self._documents.clear()

        if not self.data_dir.exists():
            # No training corpus yet; that's fine for early prototyping.
            self._index_built = True
            return

        for path in self.data_dir.rglob("*"):
            if not path.is_file():
                continue

            suffix = path.suffix.lower()
            if suffix in {".md", ".txt"}:
                content = path.read_text(encoding="utf-8", errors="ignore")
                self._documents.append(RetrievedChunk(source=str(path.name), content=content))
            elif suffix in {".pdf", ".png", ".jpg", ".jpeg"}:
                # Placeholder: in a later phase, PDFs/images can be passed through
                # OCR or converted to text before indexing.
                pseudo_summary = (
                    f"{path.name}: training material (PDF/image). "
                    "Refer to this resource for diagrams or figures related "
                    "to the queried system."
                )
                self._documents.append(RetrievedChunk(source=str(path.name), content=pseudo_summary))

        self._index_built = True

    def answer_question(self, question: str, system_focus: str) -> str:
        """
        Retrieve relevant training content and draft a high‑level answer.

        Parameters
        ----------
        question:
            Learner's question in natural language.
        system_focus:
            High‑level system selection, e.g. 'electrical' or 'hydraulic'.
            This is used only as a routing / hint, not as a type‑specific
            maintenance reference.

        Returns
        -------
        str
            A concept‑level explanation built from retrieved content.

        Note
        ----
        This function does not perform safety filtering; callers should
        pass the result through SafetyFilter before presenting it to users.
        """

        if not self._index_built:
            self.build_index()

        context_snippets = self._simple_keyword_retrieval(question, system_focus)
        return self._synthesize_explanation(question, system_focus, context_snippets)

    # ---------- Internal helpers ----------

    def _simple_keyword_retrieval(
        self,
        question: str,
        system_focus: str,
        max_chunks: int = 3,
    ) -> List[RetrievedChunk]:
        """
        Very basic keyword‑based retrieval as a stand‑in for a vector index.

        This is intentionally simple so that the retrieval logic remains
        transparent for review. It can be replaced by an embedding‑based
        engine later without changing the external API.
        """

        text = question.lower()
        system_text = system_focus.lower()

        scored: list[tuple[int, RetrievedChunk]] = []
        for chunk in self._documents:
            content_lower = chunk.content.lower()
            score = 0
            if system_text and system_text in content_lower:
                score += 2
            # Reward shared words between query and content
            for token in text.split():
                if token and token in content_lower:
                    score += 1
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:max_chunks]]

    def _synthesize_explanation(
        self,
        question: str,
        system_focus: str,
        context_snippets: List[RetrievedChunk],
    ) -> str:
        """
        Draft a concept‑level explanation using retrieved snippets.

        For Phase 1, this uses concise templated text rather than
        calling an external LLM. This keeps the codebase lightweight
        and reviewable. An LLM call can be slotted in later, using
        the same function signature.
        """

        system_label = system_focus.capitalize() if system_focus else "The system"

        intro = (
            f"{system_label} can be understood as a set of major components and "
            "paths that transfer energy or pressure between them. "
            "The description below is conceptual and intended for training only.\n\n"
        )

        if not context_snippets:
            body = (
                "No detailed training documents are currently indexed for this topic. "
                "However, you can still think about the system in terms of:\n"
                "- Primary sources of power or pressure.\n"
                "- Distribution paths and protection or regulation points.\n"
                "- Typical loads or actuators that depend on the system.\n"
            )
        else:
            body_lines = ["Relevant training resources include:\n"]
            for chunk in context_snippets:
                body_lines.append(f"- {chunk.source}: {self._summarize_chunk(chunk.content)}\n")
            body = "".join(body_lines)

        prompt_reflection = (
            "\nWhen reviewing your question, focus on how the system is "
            "designed to behave (normal operation, failure modes, and "
            "protections), rather than on specific maintenance tasks."
        )

        return intro + body + prompt_reflection

    @staticmethod
    def _summarize_chunk(content: str, max_len: int = 200) -> str:
        """
        Produce a short, human‑readable summary stub for a retrieved chunk.

        This does not attempt full automatic summarisation; it simply
        truncates with ellipsis to keep the tutor output compact.
        """

        text = " ".join(content.strip().split())
        if len(text) <= max_len:
            return text
        return text[: max_len - 3] + "..."


__all__ = ["RagEngine", "RetrievedChunk"]

