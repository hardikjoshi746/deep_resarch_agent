# app.py
import os
import gradio as gr
from research_manager import ResearchManager

# Optional banner if the OpenAI key isn't configured in the Space (Settings → Secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BANNER = None if OPENAI_API_KEY else (
    "⚠️ <b>OPENAI_API_KEY</b> is not set. "
    "Add it in <i>Settings → Secrets</i> and restart the Space."
)

def stream(query: str):
    """Wrap the ResearchManager async generator for Gradio streaming."""
    async def agen():
        try:
            async for chunk in ResearchManager().run(query):
                yield chunk
        except Exception as e:
            yield f"**Error:** {e}"
    return agen()

def build_ui():
    with gr.Blocks(title="Agentic Research") as demo:
        gr.Markdown("## Agentic Research (Planner → Search → Writer → Evaluator)")
        if BANNER:
            gr.Markdown(BANNER)

        with gr.Row():
            q = gr.Textbox(
                label="Question",
                placeholder="e.g., What are the commercial applications of agentic AI as of August 2025?",
                lines=3,
                scale=3,
            )
            run = gr.Button("Run", variant="primary", scale=1)

        out = gr.Markdown(label="Research stream")

        run.click(stream, inputs=q, outputs=out, queue=True, show_progress=True)
        q.submit(stream, inputs=q, outputs=out, queue=True, show_progress=True)

        gr.Examples(
            examples=[
                "Exciting commercial applications of agentic AI as of August 2025",
                "Compare Anthropic, OpenAI, and Google’s agentic tooling for enterprises",
                "Summarize the latest research on autonomous multi-agent systems",
            ],
            inputs=q,
            label="Try one",
        )

    return demo

demo = build_ui()
# Small queue so Space stays responsive; adjust if you expect more traffic
demo.queue(concurrency_count=2, max_size=32)

if __name__ == "__main__":
    demo.launch()
