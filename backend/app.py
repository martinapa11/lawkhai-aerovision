"""
Entry point for the Lawkhai Aerovision Phase 1 backend.

For now this is a very small HTTP‑less harness that exposes a
callable `run_demo()` function. In later phases, this file can
be extended into a FastAPI / Flask app or wired directly into
the Gradio UI.

The key goal at this stage is clarity:
- Show how a question flows through the AI tutor.
- Demonstrate that safety filtering is always applied.
- Keep everything squarely in the domain of training and
  conceptual understanding, not operational maintenance.
"""

from __future__ import annotations

from .ai_tutor import AiTutor, SystemChoice


def run_demo() -> None:
    """
    Run a simple command‑line demo of the AI tutor.

    This is primarily for local testing and instructor review.
    In production, the Gradio UI should call the same AiTutor
    interface rather than using this helper.
    """

    tutor = AiTutor()
    print("Lawkhai Aerovision – Conceptual Tutor (Phase 1 demo)")
    print("This demo is for educational use only.\n")

    system: SystemChoice = "electrical"
    try:
        question = input("Enter a conceptual question about the electrical system: ")
    except EOFError:
        return

    response = tutor.answer_conceptual_question(question=question, system_focus=system)

    print("\n--- Tutor Response ---")
    print(response.answer)
    print("\n[metadata] category:", response.category, "blocked:", response.blocked)


if __name__ == "__main__":
    # Running this module directly gives a lightweight sanity check.
    run_demo()

