import gradio as gr
import asyncio
from research_manager import ResearchManager

def _stream(query: str):
    async def agen():
        async for chunk in ResearchManager().run(query):
            yield chunk
    return agen()

def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## Agentic Research (OpenAI-powered)")
        inp = gr.Textbox(label="Question", lines=3, placeholder="Ask about a topic…")
        out = gr.Markdown(label="Research stream")
        btn = gr.Button("Run")
        btn.click(_stream, inputs=inp, outputs=out, queue=True, show_progress=True)
    return demo

if __name__ == "__main__":
    ui = build_ui()
    ui.queue(concurrency_count=2, max_size=16)
    ui.launch()
