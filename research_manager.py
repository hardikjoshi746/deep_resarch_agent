from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from evaluator_agent import evaluator_agent
from eval_schema import EvaluationReport
from build_eval_prompt import build_eval_prompt

import asyncio
import math
import re
from collections import Counter
from datetime import datetime, timezone
from contextlib import nullcontext
import os


class ResearchManager:

    async def run(self, query: str):
        """Run the deep research process, yielding status updates and the final report"""
        trace_id = gen_trace_id()
        # Disable trace by default on Spaces to avoid ContextVar loop issues
        use_trace = os.getenv("DISABLE_TRACE", "1") != "1"
        ctx = trace("Research trace", trace_id=trace_id) if use_trace else nullcontext()

        with ctx:
            if use_trace:
                msg = f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
                print(msg)
                yield msg
            else:
                print("Tracing disabled for this run (set DISABLE_TRACE=0 to enable).")
                yield "Tracing disabled for this run."

            print("Starting research...")

            search_plan = await self.plan_searches(query)
            yield "Searches planned, starting to search..."

            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."

            # Build minimal 'sources' from search results (upgrade when your search tool returns real URLs/meta)
            sources = self._build_sources_from_results(search_plan, search_results)

            report = await self.write_report(query, search_results, sources)
            yield "Report written, evaluating quality..."

            report, eval_report = await self.evaluate_and_maybe_revise(query, report, sources)
            yield f"Evaluation done (overall: {eval_report.overall:.1f}). Research complete."

            yield report.markdown_report

    # ---------- Planning & Search ----------

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """Plan the searches to perform for the query"""
        print("Planning searches...")
        result = await Runner.run(planner_agent, f"Query: {query}")
        plan = result.final_output_as(WebSearchPlan)
        print(f"Will perform {len(plan.searches)} searches")
        return plan

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """Perform the searches for the query"""
        print("Searching...")
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        num_completed = 0
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """Perform a search for a single item"""
        _input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(search_agent, _input)
            return str(result.final_output)
        except Exception:
            return None

    # ---------- Writing ----------

    async def write_report(self, query: str, search_results: list[str], sources: list[dict]) -> ReportData:
        """Write the report for the query"""
        print("Thinking about report...")
        # Provide sources list to encourage citations like [1], [2]
        sources_block = "\n".join(
            f"[{i+1}] {(s.get('title') or s.get('url') or f'Source {i+1}')} — {s.get('url','')}"
            for i, s in enumerate(sources)
        )
        _input = (
            f"Original query: {query}\n"
            f"Summarized search results: {search_results}\n\n"
            f"Sources (for inline [n] citations):\n{sources_block}"
        )
        result = await Runner.run(writer_agent, _input)
        print("Finished writing report")
        return result.final_output_as(ReportData)

    # ---------- Evaluation & Revision ----------

    async def evaluate_and_maybe_revise(self, query: str, report: ReportData, sources: list[dict]) -> tuple[ReportData, EvaluationReport]:
        """
        1) Call EvaluatorAgent using build_eval_prompt
        2) Run minimal deterministic checks
        3) If scores are low, invoke a single revision pass with WriterAgent
        """
        # 1) LLM-as-judge
        eval_input = build_eval_prompt(query, report.markdown_report, sources)
        eval_res = await Runner.run(evaluator_agent, eval_input)
        eval_report: EvaluationReport = eval_res.final_output_as(EvaluationReport)

        # 2) Cheap deterministic checks
        cov = self._citation_coverage(report.markdown_report)
        div = self._source_diversity([s.get("url", "") for s in sources])
        age = self._median_source_age_days([s.get("published_at") for s in sources])

        # Attach brief metrics to a short summary if available
        try:
            report.short_summary += (
                f"\n\n_Eval:_ overall {eval_report.overall:.1f}/5 • "
                f"cov {cov:.2f} • div {div:.2f} • age_med {('∞' if age == math.inf else int(age))}d"
            )
        except Exception:
            pass

        # 3) Decide if a revision is needed
        MIN_OVERALL = 4.0
        MIN_COV = 0.60
        MIN_DIV = 0.50
        MAX_AGE = 180  # days

        needs_revision = (
            eval_report.overall < MIN_OVERALL
            or cov < MIN_COV
            or div < MIN_DIV
            or (age != math.inf and age > MAX_AGE)
        )

        if not needs_revision:
            return report, eval_report

        # Build concise feedback from evaluator recommendations
        feedback_lines = "\n".join(
            f"- {r}" for r in (getattr(eval_report, "recommendations", None) or [])
        ) or "- Tighten unsupported claims and add/repair [n] citations for non-obvious facts."

        revise_prompt = (
            "Revise the draft to address these issues. Keep markdown. "
            "Only keep claims supported by the provided sources. "
            "Attach inline numeric citations like [1], [2] for all non-obvious facts.\n\n"
            f"Issues:\n{feedback_lines}"
        )

        # Re-run writer once with feedback
        sources_block = "\n".join(
            f"[{i+1}] {(s.get('title') or s.get('url') or f'Source {i+1}')} — {s.get('url','')}"
            for i, s in enumerate(sources)
        )
        writer_input = (
            f"Original query: {query}\n\n"
            f"Feedback:\n{revise_prompt}\n\n"
            f"Draft:\n{report.markdown_report}\n\n"
            f"Sources (for inline [n] citations):\n{sources_block}"
        )
        writer_res2 = await Runner.run(writer_agent, writer_input)
        revised = writer_res2.final_output_as(ReportData)

        # (Optional) quick second evaluation
        eval_input2 = build_eval_prompt(query, revised.markdown_report, sources)
        eval_res2 = await Runner.run(evaluator_agent, eval_input2)
        eval_report2: EvaluationReport = eval_res2.final_output_as(EvaluationReport)

        return revised, eval_report2

    # ---------- Helpers ----------

    def _build_sources_from_results(self, search_plan: WebSearchPlan, search_results: list[str]) -> list[dict]:
        """
        Temporary shim: creates 'sources' entries from the summaries produced by SearchAgent.
        Replace this with real metadata (url/title/date/snippet) when your search tool exposes it.
        """
        sources: list[dict] = []
        for i, summary in enumerate(search_results, start=1):
            q = search_plan.searches[i - 1].query if i - 1 < len(search_plan.searches) else f"Search {i}"
            sources.append({
                "url": f"https://example.com/search/{i}",  # TODO: real URL from search results
                "title": f"Notes for: {q}",
                "published_at": None,
                "snippet": summary[:400] if summary else "",
            })
        return sources

    def _citation_coverage(self, markdown: str) -> float:
        sents = re.split(r'(?<=[.!?])\s+', markdown or "")
        sents = [s for s in sents if s.strip()]
        cited = sum(1 for s in sents if re.search(r'\[(\d+)\]', s))
        return 0.0 if not sents else cited / len(sents)

    def _source_diversity(self, urls: list[str]) -> float:
        if not urls:
            return 0.0
        domains = []
        for u in urls:
            try:
                d = u.split("://", 1)[1].split("/", 1)[0].removeprefix("www.").lower()
                domains.append(d)
            except Exception:
                pass
        n = len(domains)
        counts = Counter(domains)
        return 1 - sum((c / n) ** 2 for c in counts.values()) if n else 0.0

    def _median_source_age_days(self, iso_dates: list[str | None]) -> float:
        now = datetime.now(timezone.utc)
        ages = []
        for ts in iso_dates:
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                ages.append((now - dt).days)
            except Exception:
                pass
        if not ages:
            return math.inf
        ages.sort()
        m = len(ages) // 2
        return ages[m] if len(ages) % 2 else (ages[m - 1] + ages[m]) / 2
