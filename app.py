# app.py
import os
import gradio as gr
from research_manager import ResearchManager

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BANNER = None if OPENAI_API_KEY else (
    "⚠️ <b>OPENAI_API_KEY</b> is not set. "
    "Add it in <i>Settings → Secrets</i> and restart the Space."
)

# async generator that yields incremental text
async def stream(query: str):
    try:
        rm = ResearchManager()
        async for chunk in rm.run(query):
            yield chunk
    except Exception as e:
        yield f"**Error:** {e}"

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

        # IMPORTANT in Gradio 5: pass stream=True so the async generator is consumed as a stream
        run.click(stream, inputs=q, outputs=out, stream=True)
        q.submit(stream, inputs=q, outputs=out, stream=True)

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
demo.queue()  # defaults are fine for Gradio 5

if __name__ == "__main__":
    demo.launch()
