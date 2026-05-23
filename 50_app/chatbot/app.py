"""HF Space entrypoint for the Nisamina chatbot.

Phase-3 interim: Gemma 3 4B-Instruct + system_prompt_v1 + M-P3.E guardrails +
M-P2 MCP grounding. Gradio ChatInterface.

HF Space deploy:
    1. Create a new HF Space (Gradio template; Python 3.11+).
    2. Add HF token if model is gated (Gemma 3 may require accepting license).
    3. Copy this directory's contents to the Space repo root.
    4. Push.
    5. First-boot downloads google/gemma-4-E4B-it (Apache 2.0; not gated).

Engineer-side: this file imports gradio lazily so the orchestrator module
remains test-runnable without gradio installed.
"""

from __future__ import annotations

import os


def _build_gradio_app(orchestrator, ui_state):
    """Lazy-build Gradio ChatInterface. Returns the demo object."""
    import gradio as gr  # noqa: WPS433

    def respond(message: str, history: list[tuple[str, str]]):
        """Returns (text, audio_path_or_None) for ChatInterface + gr.Audio
        side-by-side per F-058-FOLLOWUP punch-list."""
        import tempfile
        resp = orchestrator.orchestrate(message, ui_state["session_state"])
        ui_state["session_state"] = resp.session_state
        text = resp.text
        if resp.citations:
            cites = []
            for rec in resp.citations[:5]:
                hw = rec.get("headword_normalized", "?")
                tier = rec.get("tier", "?")
                cites.append(f"  • {hw} (Tier-{tier})")
            text += "\n\n— Citations —\n" + "\n".join(cites)
        if resp.flagged_garifuna_tokens:
            text += (
                "\n\n— Flagged for elder / Commission review: "
                + ", ".join(resp.flagged_garifuna_tokens[:5])
            )
        if resp.blocked_reason:
            text += f"\n\n(blocked: {resp.blocked_reason})"

        # F-058-FOLLOWUP: render audio if TTS produced output
        audio_path = None
        if resp.has_audio and resp.audio_garifuna_wav:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(resp.audio_garifuna_wav)
            tmp.close()
            audio_path = tmp.name
            if resp.audio_attribution:
                text += f"\n\n— Voice attribution —\n  {resp.audio_attribution}"
        return text, audio_path

    # Blocks layout: chatbot + gr.Audio + attribution chip per F-058-FOLLOWUP.
    with gr.Blocks(
        title="Nisamina · Garifuna Language Assistant",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown(
            "# Nisamina · Garifuna Language Assistant\n\n"
            "Phase-3 interim build. Grounded-only — I cite my foundry sources "
            "and refuse to invent Garifuna. License: **Labayayahoun Ibagari** + "
            "CC-BY-NC-SA 4.0. Apache 2.0 brain (Gemma 3 4B-Instruct). "
            "Voice: facebook/mms-tts-cab (CC-BY-NC 4.0, Pratap et al. 2023)."
        )
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(label="Chat", height=480)
                msg = gr.Textbox(label="Your message",
                                 placeholder="What does abayayahouni mean?")
                with gr.Row():
                    submit_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear")
            with gr.Column(scale=1):
                audio_out = gr.Audio(
                    label="Garifuna pronunciation (mms-tts-cab)",
                    type="filepath",
                    interactive=False,
                )
                gr.Markdown(
                    "**Voice attribution:** facebook/mms-tts-cab — "
                    "Pratap et al. 2023 arXiv 2305.13516 (Meta AI) — "
                    "CC-BY-NC 4.0 — consent_007 + attr_030"
                )
                gr.Examples(
                    examples=[
                        "What does abayayahouni mean?",
                        "How do you say 'my name is' in Garifuna?",
                        "What is walagallo?",
                        "Can you teach me numbers 1 to 5?",
                    ],
                    inputs=msg,
                )

        def submit_and_clear(text: str, chat_history):
            reply_text, audio_path = respond(text, chat_history)
            chat_history = (chat_history or []) + [(text, reply_text)]
            return chat_history, audio_path, ""

        submit_btn.click(submit_and_clear, [msg, chatbot], [chatbot, audio_out, msg])
        msg.submit(submit_and_clear, [msg, chatbot], [chatbot, audio_out, msg])
        clear_btn.click(lambda: ([], None, ""), None, [chatbot, audio_out, msg])

    return demo


def main():
    """HF Space launch entrypoint."""
    # Dual-mode imports: relative when loaded as package (local dev / tests);
    # absolute when run as standalone script (HF Space deploys app.py at repo root).
    try:
        from .orchestrator import Orchestrator, SessionState
        from .brain import load_brain
    except ImportError:
        from orchestrator import Orchestrator, SessionState
        from brain import load_brain

    real_mode = os.getenv("NISAMINA_REAL_BRAIN", "1") == "1"
    brain = load_brain(real_mode=real_mode)
    orchestrator = Orchestrator(brain=brain)
    ui_state = {"session_state": SessionState()}

    demo = _build_gradio_app(orchestrator, ui_state)
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
    )


if __name__ == "__main__":
    main()
