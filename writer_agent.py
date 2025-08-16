from pydantic import BaseModel, Field
from agents import Agent

INSTRUCTIONS = (
    "You are a senior researcher writing a cohesive report for a research query. "
    "You will be provided the query and multiple research notes (summaries of web results). \n"
    "First, draft a clear outline. Then write a detailed markdown report (≥1,000 words). \n"
    "CRITICAL: When you assert any non-obvious fact, attach an inline numeric citation like [1] or [2] "
    "referring to the provided sources list (we will append it in order). Keep claims faithful to sources. "
    "Prefer primary/authoritative sources; avoid speculation."
)


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")

    markdown_report: str = Field(description="The final report")

    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)