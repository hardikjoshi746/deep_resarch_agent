import os
import asyncio
import gradio as gr
from research_manager import ResearchManager

# Optional banner if key is missing
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BANNER = None if OPENAI_API_KEY else (
    "⚠️ <b>OPENAI_API_KEY</b> is not set. "
    "Add it in <i>Settings → Secrets</i> and restart the Space."
)

def stream(query: str):
    """
    Synchronous generator wrapper around the async ResearchManager.
    Gradio streams each yielded chunk to the Markdown output.
    """
    async def agen():
        rm = ResearchManager()
        async for chunk in rm.run(query):
            yield chunk

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        aiter = agen()
        while True:
            try:
                chunk = loop.run_until_complete(aiter.__anext__())
            except StopAsyncIteration:
                break
            except Exception as e:
                yield f"**Error:** {e}"
                break
            else:
                yield chunk
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()

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

        run.click(stream, inputs=q, outputs=out)
        q.submit(stream, inputs=q, outputs=out)

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
demo.queue()

if __name__ == "__main__":
    demo.launch()
