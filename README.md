# Deep Research Agent

## Overview

This high-signal agentic research app plans web searches, aggregates findings, writes a source-grounded report, **evaluates** the result with a strict rubric, and (if needed) performs a **single-pass revision**.

Built with **Python**, **Gradio**, and **OpenAI**, the app streams progress live and enforces citation hygiene using a numbered source list.

---

## Features

- **Planner → Search → Writer → Evaluator → (Revise once)**
  - Planner creates targeted search tasks.
  - Searches run concurrently for speed.
  - Writer produces a Markdown report with inline `[n]` citations.
  - Evaluator scores **Faithfulness, Relevance & Completeness, Structure & Citations** (weighted 0.5/0.3/0.2) + actionable fixes.
  - If quality or coverage is low, Writer revises once from evaluator feedback.

- **Streaming UI**
  - Live status lines (planning, searching, writing, evaluating) + final Markdown output.

- **Source-grounded**
  - Writer and Evaluator are given a numbered list of allowed sources to enforce correct `[n]` citations.

- **Safe defaults for Spaces**
  - Tracing is disabled by default to avoid event-loop context issues.
  - Email sending is removed (keeps requirements minimal and deployment simple).

---

## “Schema” (Evaluator & Report)

### `EvaluationReport`  
Returned by the Evaluator agent.

| Field            | Type   | Notes                                                                 |
|------------------|--------|-----------------------------------------------------------------------|
| criteria         | array  | EXACTLY 3 items with `{name, score (1–5), justification}`             |
| overall          | number | `0.5*Faithfulness + 0.3*Relevance + 0.2*Structure` (1 decimal place)  |
| recommendations  | array  | 2–5 short, actionable fixes (e.g., “Add [2] for JPM claim”)          |

### `ReportData`  
Returned by the Writer agent.

| Field             | Type   | Notes                              |
|-------------------|--------|------------------------------------|
| markdown_report   | string | Final Markdown report              |
| short_summary     | string | (Optional) one-liner + metrics     |

---

## Business Logic

- **Citation coverage**: fraction of sentences with `[n]` references.  
- **Source diversity**: Herfindahl-based score over domain names.  
- **Recency**: median source age in days.

A **single revision** is triggered if any threshold fails:
- `overall < 4.0`
- `coverage < 0.60`
- `diversity < 0.50`
- `median_age > 180 days` (if dates exist)

---

## Tech Stack

- **Python (3.10)** — Compatible with Hugging Face Gradio Spaces
- **Gradio** — UI and streaming
- **OpenAI** — Agents and LLMs
- **Pydantic v2** — Strict output schemas

---

## Folder Structure

```bash

├── app.py # Gradio entrypoint (used by Spaces)
├── research_manager.py # Orchestrates planner/search/writer/evaluator
├── planner_agent.py # PlannerAgent schemas & config
├── search_agent.py # SearchAgent (replace shim with real search)
├── writer_agent.py # WriterAgent -> ReportData
├── evaluator_agent.py # EvaluatorAgent -> EvaluationReport
├── eval_schema.py # Pydantic models for evaluator output
├── build_eval_prompt.py # Helper to assemble evaluator input
├── requirements.txt
└── README.md
```


---

## Running the App (Locally & Spaces)

```bash
uv sync
export OPENAI_API_KEY=sk-...
export DISABLE_TRACE=0     # optional: enable tracing locally
uv run app.py

```


---

## Running the App (Locally & Spaces)

### 1) Local (uv)

```bash
uv sync
export OPENAI_API_KEY=sk-...
export DISABLE_TRACE=0     # optional: enable tracing locally
uv run app.py
```
---

Author
Hardik Joshi

