NOTES = (
    {"source": "python-guide#functions", "text": "Functions name reusable behavior and define inputs and outputs."},
    {"source": "web-guide#http", "text": "HTTP requests carry a method, path, headers, and optional body."},
    {"source": "security-guide#permissions", "text": "Authorization checks whether this user may access this resource."},
)
ALLOWED_TOOLS = {"search_notes"}


def retrieve(query: str) -> list[dict[str, str]]:
    terms = set(query.lower().split())
    matches = [
        note for note in NOTES
        if terms.intersection(note["text"].lower().replace(".", "").split())
    ]
    return matches


if __name__ == "__main__":
    requested_tool = "search_notes"
    evidence = retrieve("HTTP method path")
    print("Tool allowed:", requested_tool in ALLOWED_TOOLS)
    print("Evidence:", [(item["source"], item["text"]) for item in evidence])
