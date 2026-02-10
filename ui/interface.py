"""
Gradio UI for Lawkhai Aerovision – Phase 1 (AI Tutor Core).

This interface is intentionally simple and conservative:
- Text-based Q&A only.
- Dropdown to select the system focus (Electrical / Hydraulic).
- Safety notice that is always visible, emphasising:
  * Training and educational use only.
  * No maintenance procedures or diagnostics.
  * The need to consult approved documentation and instructors.

The UI calls into backend.ai_tutor.AiTutor, which already enforces
additional safety and compliance rules.
"""

from __future__ import annotations

import gradio as gr

from backend.ai_tutor import AiTutor, SystemChoice, TutorResponse


SAFETY_BANNER = (
    "⚠️ **Training-only system** – Lawkhai Aerovision is designed to support "
    "aircraft maintenance *education* by explaining system behaviour, "
    "architecture, and fault logic.\n\n"
    "- It does **not** provide maintenance procedures, troubleshooting steps, "
    "or real-world diagnostics.\n"
    "- Always consult the approved Aircraft Maintenance Manual (AMM), "
    "type-specific documentation, and your instructor or supervising "
    "engineer before any maintenance activity."
)


_SYSTEM_LABEL_TO_KEY: dict[str, SystemChoice] = {
    "Electrical power generation & distribution": "electrical",
    "Hydraulic system conceptual flow": "hydraulic",
}


class TutorUI:
    """
    Thin wrapper that wires the AiTutor backend into a Gradio interface.
    """

    def __init__(self) -> None:
        self._tutor = AiTutor()

    def _answer(
        self,
        question: str,
        system_label: str,
    ) -> tuple[str, str]:
        """
        Callback used by Gradio when the learner submits a question.

        Returns
        -------
        answer_markdown:
            The main explanation for the learner, already safety-filtered.
        meta_markdown:
            A small metadata panel describing how the system handled the query.
        """

        system_key: SystemChoice = _SYSTEM_LABEL_TO_KEY.get(
            system_label, "electrical"
        )

        if not question.strip():
            return (
                "Please enter a question about how the selected system behaves, "
                "such as **'What happens if one generator fails?'**",
                "",
            )

        response: TutorResponse = self._tutor.answer_conceptual_question(
            question=question,
            system_focus=system_key,
        )

        meta_lines = [
            f"**System focus:** {response.system_focus.capitalize()}",
            f"**Safety category:** {response.category}",
        ]
        if response.blocked:
            meta_lines.append(
                "**Note:** The original request was considered procedural or "
                "ambiguous and has been redirected to a safer, conceptual "
                "explanation."
            )

        return response.answer, "\n\n".join(meta_lines)

    def build(self) -> gr.Blocks:
        """
        Build the Gradio Blocks layout for the Phase 1 tutor.
        """

        with gr.Blocks(title="Lawkhai Aerovision – Conceptual Tutor") as demo:
            gr.Markdown(SAFETY_BANNER)

            with gr.Row():
                system_dropdown = gr.Dropdown(
                    label="System focus",
                    choices=list(_SYSTEM_LABEL_TO_KEY.keys()),
                    value="Electrical power generation & distribution",
                    interactive=True,
                    info="Select the system you want to study conceptually.",
                )

            question_box = gr.Textbox(
                label="Ask a conceptual question",
                placeholder=(
                    "Example: How does the main AC bus stay powered if one generator fails?"
                ),
                lines=3,
            )

            ask_button = gr.Button("Ask the tutor")

            answer_output = gr.Markdown(label="Tutor explanation")
            meta_output = gr.Markdown(label="Safety & system context")

            ask_button.click(
                fn=self._answer,
                inputs=[question_box, system_dropdown],
                outputs=[answer_output, meta_output],
            )

        return demo


def launch() -> None:
    """
    Launch the Gradio app.

    This helper keeps the UI bootstrap in one place so that:
    - It is easy to start during development.
    - Future integrations (e.g. running behind a different web server)
      can still reuse the same `TutorUI.build()` method.
    """

    ui = TutorUI()
    demo = ui.build()
    demo.launch()


if __name__ == "__main__":
    launch()

