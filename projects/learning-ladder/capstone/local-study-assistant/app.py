NOTES = (
    {
        "source": "python/functions",
        "text": "Functions package reusable behavior and make inputs and outputs explicit.",
    },
    {
        "source": "web/http",
        "text": "HTTP requests include a method and path; responses include a status.",
    },
    {
        "source": "security/authorization",
        "text": "Authorization checks whether a user may access a particular resource.",
    },
)
ALLOWED_TOOLS = {"search_notes"}


def retrieve(query: str, limit: int = 2) -> list[dict[str, str]]:
    terms = set(query.lower().split())
    if not terms:
        return []
    ranked = []
    for note in NOTES:
        words = set(note["text"].lower().replace(".", "").replace(";", "").split())
        overlap = len(terms & words)
        if overlap:
            ranked.append((overlap, note))
    ranked.sort(key=lambda item: (-item[0], item[1]["source"]))
    return [note for _, note in ranked[:limit]]


def answer(query: str, requested_tool: str) -> str:
    if requested_tool not in ALLOWED_TOOLS:
        return "Request refused: tool is not allowlisted."
    evidence = retrieve(query)
    if not evidence:
        return "No matching evidence found in the local notes."
    citations = ", ".join(item["source"] for item in evidence)
    return f"Relevant local notes were found. Verify the answer against: {citations}"


if __name__ == "__main__":
    print(answer("HTTP request method", "search_notes"))
    print(answer("run arbitrary shell", "run_shell"))
