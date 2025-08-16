# app.py
import os
import gradio as gr

# Fail fast if no key present (or degrade features gracefully)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Show a banner in the UI instead of crashing
    WARNING = (
        "⚠️ OPENAI_API_KEY is not set. Add it in the Space → **Settings → Secrets**. "
        "The app will not run without it."
    )
else:
    # make sure the OpenAI SDK can see it (your agents probably do os.getenv internally)
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from deep_research import build_ui

demo = build_ui()
demo.queue(concurrency_count=2, max_size=32)  # tune as needed

if __name__ == "__main__":
    demo.launch()
