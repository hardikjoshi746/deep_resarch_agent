# Deep Research Agent

**A modular, AI-powered research assistant framework** built with Python and powered by [Gradio](https://www.gradio.app/) for the UI.  
The system employs multiple agents — search, planner, writer, and email communicator — to autonomously break down research tasks, gather and analyze information, plan workflows, write drafts, and share results.

---

## 📂 Repository Structure

deep_resarch_agent/
├── deep_research.py # Main entry point for the deep research agent
├── email_agent.py # Sends email summaries or alerts
├── planner_agent.py # Creates structured research plans
├── research_manager.py # Oversees workflows and agent interactions
├── search_agent.py # Retrieves data from the web or custom sources
├── writer_agent.py # Drafts content or research summaries
├── main.py # Combined multimodal orchestration (if applicable)
├── pyproject.toml # Project configuration & dependencies (managed by uv)
├── requirements.txt # Dependencies list (pre-uv migration)
├── uv.lock # Lockfile created by uv
└── .python-version # Python version specification

yaml
Copy
Edit

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (as specified in `.python-version`)
- [`uv`](https://docs.astral.sh/uv) installed for dependency management

### Setup

```bash
# If starting fresh (no pyproject.toml)
uv init

# Install dependencies from requirements.txt
uv add --requirements requirements.txt

# Or sync using existing pyproject.toml
uv sync
Run the Agent
bash
Copy
Edit
uv run deep_research.py
🧩 Modules Overview
deep_research.py – Main orchestrator script

email_agent.py – Sends research summaries or notifications via email

planner_agent.py – Generates step-by-step research plans

research_manager.py – Coordinates agent collaboration

search_agent.py – Handles information retrieval

writer_agent.py – Creates written summaries and reports

main.py – (Optional) Entry point for combined agents or UI launch

⚙️ Configuration & Customization
Update dependencies in pyproject.toml

Modify agent scripts to integrate with your preferred APIs or data sources

To run without affecting your environment:

bash
Copy
Edit
uv run <script>.py
🤝 Contributing
Fork the repo & clone it locally

Install dependencies:

bash
Copy
Edit
uv sync
Add features, improve existing agents, write tests, and update docs

Submit a pull request

```
