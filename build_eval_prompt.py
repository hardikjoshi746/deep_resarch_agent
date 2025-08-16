def build_eval_prompt(user_query: str, markdown: str, sources: list[dict]) -> str:
    """
    sources: list of dicts with keys:
      - url: str
      - title: str | None
      - published_at: ISO8601 str | None
      - snippet: str | None
    """
    src_lines = []
    for i, s in enumerate(sources, start=1):
        title = s.get("title") or s.get("url") or f"Source {i}"
        line = f"[{i}] {title}"
        if s.get("published_at"):
            line += f" ({s['published_at']})"
        if s.get("snippet"):
            line += f": {s['snippet'][:250]}"
        if s.get("url"):
            line += f" — {s['url']}"
        src_lines.append(line)

    return (
        f"## User Query\n{user_query}\n\n"
        f"## Answer (Markdown)\n{markdown}\n\n"
        f"## Allowed Sources\n" + "\n".join(src_lines)
    )
