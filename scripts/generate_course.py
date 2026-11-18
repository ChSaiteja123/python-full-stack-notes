from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "curriculum" / "course_catalog.json"
DEFAULT_SOURCE = ROOT.parent.parent / "ai" / "ai-devops" / "visual-learning" / "python-full-stack-with-ai.txt"

MONTHS = (
    {
        "slug": "month-01-python-fundamentals",
        "name": "Python Programming Fundamentals",
        "focus": "Python syntax, data, control flow, functions, files, and a first command-line application.",
        "project": "Student Management System",
        "ai_bridge": "Use an AI assistant as a tutor, not as an authority: ask for an explanation or test idea, then verify every claim with a tiny Python experiment and official documentation. Use fictional code only; never paste credentials or private data.",
        "docs": [
            ("Python tutorial", "https://docs.python.org/3/tutorial/"),
            ("Built-in functions", "https://docs.python.org/3/library/functions.html"),
        ],
    },
    {
        "slug": "month-02-professional-python-and-apis",
        "name": "Professional Python and APIs",
        "focus": "Object-oriented design, Python protocols, testing, type hints, HTTP clients, and asynchronous work.",
        "project": "Python REST API Client",
        "ai_bridge": "Build a provider-neutral interface and use a deterministic fake response first. Validate structured data with explicit types, mock network calls in tests, and configure any real provider key only in a local environment after reviewing cost and privacy.",
        "docs": [
            ("Python standard library", "https://docs.python.org/3/library/"),
            ("pytest documentation", "https://docs.pytest.org/en/stable/"),
            ("Python typing", "https://docs.python.org/3/library/typing.html"),
        ],
    },
    {
        "slug": "month-03-web-and-database-development",
        "name": "Web and Database Development",
        "focus": "Browser fundamentals, HTML, CSS, JavaScript, Git, HTTP, databases, and client-side interfaces.",
        "project": "Responsive Frontend and Mock AI Chat",
        "ai_bridge": "Keep the browser UI separate from provider credentials. Use a mocked chat endpoint to build loading, empty, error, retry, and cancellation states before connecting any backend.",
        "docs": [
            ("MDN Web Docs", "https://developer.mozilla.org/en-US/docs/Learn"),
            ("React Learn", "https://react.dev/learn"),
            ("PostgreSQL documentation", "https://www.postgresql.org/docs/current/"),
        ],
    },
    {
        "slug": "month-04-django-full-stack",
        "name": "Django Full Stack",
        "focus": "Django MVT, URLs, views, templates, models, ORM, forms, authentication, and a complete web application.",
        "project": "Django Blog Management System",
        "ai_bridge": "Keep provider calls in a tested service module, not a view. For document features, begin with synthetic files, enforce user permissions before retrieval, and return source references with any generated draft.",
        "docs": [
            ("Django documentation", "https://docs.djangoproject.com/en/stable/"),
            ("Django security", "https://docs.djangoproject.com/en/stable/topics/security/"),
        ],
    },
    {
        "slug": "month-05-drf-full-stack-and-ai",
        "name": "Django REST Framework, React, and AI Workflows",
        "focus": "REST APIs, DRF, authentication, PostgreSQL, React, document retrieval, and bounded tool-calling.",
        "project": "Full-Stack Document Assistant",
        "ai_bridge": "Use the same full-stack contract for AI: authenticate the user, check document scope, retrieve approved evidence, call a provider adapter or deterministic mock, validate the result, and return citations. Agent tools remain allowlisted and read-only unless a human approves an action.",
        "docs": [
            ("Django REST Framework", "https://www.django-rest-framework.org/"),
            ("React Learn", "https://react.dev/learn"),
            ("OWASP API Security", "https://owasp.org/www-project-api-security/"),
        ],
    },
    {
        "slug": "month-06-production-deployment-and-job-readiness",
        "name": "Production, Deployment, and Job Readiness",
        "focus": "Security, performance, tests, containers, CI/CD, deployment, observability, AI evaluation, and portfolio readiness.",
        "project": "AI Learning and Developer Assistant Capstone",
        "ai_bridge": "Evaluate security, privacy, quality, latency, and cost independently. Use mock providers in automated tests, apply per-user authorization in server code, and require explicit human approval for external or irreversible side effects.",
        "docs": [
            ("Django deployment checklist", "https://docs.djangoproject.com/en/stable/howto/deployment/checklist/"),
            ("Docker documentation", "https://docs.docker.com/"),
            ("GitHub Actions", "https://docs.github.com/en/actions"),
            ("OWASP Top 10", "https://owasp.org/www-project-top-ten/"),
        ],
    },
)

TOPIC_GUIDES = (
    (("variable", "naming"), "A variable name refers to an object; assignment binds a name rather than creating a labeled box that permanently owns a value.", "Use names that communicate meaning, then inspect the value and type where a bug occurs.", "Reassignment, misspelling, and mutable aliases are useful edge cases to test."),
    (("data type", "type conversion"), "A type defines the operations and representation supported by a value. Conversion is a deliberate transformation and may reject or lose information.", "Check the source format before converting, and validate the resulting value against the domain.", "Test empty strings, out-of-range numbers, and invalid formats rather than assuming input is clean."),
    (("operator",), "Operators combine values or test relationships. Precedence and operand types determine the result, so complex expressions should be grouped and named.", "Evaluate one operation at a time and use parentheses when intent might be ambiguous.", "Test zero, negative values, equality boundaries, and incompatible types."),
    (("input and output",), "Input arrives as text or another external representation; output communicates a result. Validate and normalize input before using it in application logic.", "Separate reading, validation, computation, and display so each part can be tested independently.", "An empty or malformed input should produce a useful error, not an unexplained crash."),
    (("string", "regular expression"), "Text is an immutable sequence of characters. String operations create new values; patterns such as regular expressions should be narrowly scoped and tested on both matches and non-matches.", "Normalize only what the task requires, preserve original data when useful, and avoid using regex for nested structured formats.", "Whitespace, Unicode, escaping, and unexpected delimiters are common boundary cases."),
    (("condition", "polymorphism"), "A branch or polymorphic call chooses behavior from a condition or object contract. Make the decision rules explicit and cover both sides of each branch.", "Prefer simple, readable conditions and test exact boundary values.", "Overlapping conditions and an unhandled final case can produce surprising behavior."),
    (("loop", "iteration", "iterable"), "Iteration repeatedly obtains values from an iterable. The loop's state, stopping rule, and update determine whether it progresses and what it visits.", "Trace one iteration at a time; state what changes and why the loop terminates.", "An unchanged condition, off-by-one range, or mutation during iteration can cause incorrect results."),
    (("list", "tuple", "set", "dictionary", "stack", "queue"), "Collections encode different guarantees: sequence order, immutability, uniqueness, key lookup, or a particular access discipline.", "Choose a structure from the operations and invariants the feature needs, then check those invariants after updates.", "Missing keys, duplicate values, ordering assumptions, and shared mutable references deserve tests."),
    (("function", "lambda", "decorator"), "A function packages behavior behind inputs and an output; decorators wrap call behavior. Small functions with explicit contracts are easier to test and reuse.", "Name parameters, document side effects, and test return values and exceptions.", "Hidden state, mutable defaults, and wrappers that lose metadata can make behavior hard to reason about."),
    (("scope", "parameter", "argument", "return"), "Names resolve within scopes, arguments supply call-time values, and return values make results explicit to callers.", "Trace where a name is defined and where a value crosses a function boundary.", "Shadowed names, missing returns, and accidental mutation can look like data loss."),
    (("module", "package", "import"), "Modules group related names; packages provide an importable structure. Imports should be explicit and avoid executing unexpected work at import time.", "Keep reusable logic separate from command-line entry points and use a virtual environment for dependencies.", "Circular imports and module-name collisions can break imports even when files exist."),
    (("exception", "error handling"), "Exceptions represent failures that should be handled at a boundary where the program can recover or explain the problem.", "Catch specific exceptions, preserve context, and avoid turning failure into a success-looking default.", "Broad catches can hide defects; test both expected invalid input and unexpected failures."),
    (("file handling", "json", "csv"), "File processing crosses a trust and encoding boundary. Use context managers, explicit encodings, schema validation, and safe paths.", "Parse, validate, transform, and write separately; preserve originals and handle missing or malformed data visibly.", "Partial writes, encoding differences, malformed records, and oversized input are important cases."),
    (("class", "object", "inheritance", "encapsulation", "abstraction", "magic method", "dataclass"), "A class defines behavior and state for instances. Inheritance is only one reuse mechanism; composition and small protocols can be simpler.", "Give each class a clear invariant and keep side effects at explicit boundaries.", "Shared mutable class state and deep inheritance make behavior harder to predict."),
    (("generator", "iterator"), "An iterator yields values on demand; a generator can provide a concise lazy iterator. Lazy evaluation reduces eager memory use but errors may occur during iteration.", "Consume values deliberately, understand exhaustion, and close resources that are tied to iteration.", "A generator is usually single-pass; retaining all results still uses memory."),
    (("context manager",), "A context manager brackets resource use so cleanup runs on normal exit and exceptions.", "Use `with` for files and locks, and put acquisition and release behavior in one abstraction.", "Manual cleanup can be skipped on an exception or an early return."),
    (("comprehension",), "A comprehension constructs a collection from an iterable and optional condition. It is clearest when the transformation is short and local.", "Use a named loop for complex branching or side effects.", "Nested comprehensions can obscure order and make debugging difficult."),
    (("date", "time"), "Date and time values need explicit time zones and formats. A timestamp is not automatically local time or a calendar date.", "Store unambiguous instants and convert for display at the boundary.", "Naive datetimes, daylight-saving changes, and locale assumptions cause subtle defects."),
    (("logging",), "Logs record structured events that help diagnose behavior; they are not a place to copy secrets or entire private payloads.", "Choose levels, include safe correlation context, and avoid logging credentials or personal data.", "Duplicate handlers and overly verbose logs can leak data or overwhelm operators."),
    (("debugging",), "Debugging is a loop: reproduce, observe, form a testable hypothesis, change one cause, and verify the outcome.", "Reduce the failing case and inspect state at the boundary where it becomes incorrect.", "Changing several things at once obscures which change fixed or caused the behavior."),
    (("test", "assessment"), "Tests encode an expected contract. A useful test checks observable behavior and includes normal, boundary, and failure cases.", "Keep tests deterministic, isolate external systems, and make failures explain the violated expectation.", "Tests that repeat implementation details can pass while user behavior is broken."),
    (("type hint",), "Type hints communicate expected values to readers and tools; they do not validate untrusted runtime input by themselves.", "Use precise types at internal boundaries and runtime validation at external boundaries.", "A `str` annotation cannot prove that a string is a valid email, identifier, or permission."),
    (("virtual environment", "dependency"), "A virtual environment isolates project packages; a dependency file records what must be installed to reproduce the project.", "Create the environment per project, pin compatible versions for applications, and review updates deliberately.", "Installing globally or mixing projects can produce environment-dependent behavior."),
    (("http", "rest api", "requests library", "fetch api", "client-server", "dns", "internet"), "A network request crosses a boundary: method, destination, headers, body, status, and timeout all matter. A response can fail or be partial.", "Use timeouts, validate status and payload shape, and keep credentials out of URLs and logs.", "DNS failure, TLS problems, rate limits, and non-JSON responses need distinct handling."),
    (("async", "thread", "multiprocessing", "websocket", "channels"), "Concurrency lets work make progress without a simple one-task-at-a-time flow. Async I/O helps while waiting; CPU-heavy work may need a process or queue.", "Choose a model from the workload, keep shared state controlled, and bound concurrency.", "Cancellation, race conditions, blocking calls, and unbounded tasks can harm responsiveness."),
    (("html", "semantic", "form"), "HTML describes document structure and meaning. Semantic elements and labels improve keyboard use, assistive technology support, and browser behavior.", "Use native controls and associate each form field with a visible label and useful validation message.", "Placeholder text is not a label, and client-side validation is not a server-side security control."),
    (("css", "flexbox", "grid", "responsive", "animation", "transition"), "CSS separates presentation from document meaning. Layout, sizing, contrast, and motion should adapt to content and viewport.", "Start with a content-first layout and test narrow, wide, keyboard, and reduced-motion cases.", "Fixed widths, low contrast, and motion without a reduced-motion alternative can block users."),
    (("javascript", "dom", "event", "promise", "react", "hooks", "props", "state"), "Browser JavaScript responds to events and updates a rendered interface. State should have a clear owner, and asynchronous work needs loading and error states.", "Keep data flow predictable and render user-provided text as text rather than executable markup.", "Stale state, missing cleanup, double submission, and unhandled promise rejection are common failures."),
    (("django", "url", "view", "template", "middleware", "admin", "model", "queryset", "migration", "form", "session", "cookie", "pagination", "upload"), "Django routes a request through URL configuration and middleware to a view, which coordinates domain logic and a response. ORM, templates, forms, and auth each have separate responsibilities.", "Keep views thin, validate input, enforce authorization server-side, and use migrations to evolve the schema.", "Unescaped output, missing permission checks, N+1 queries, and untrusted uploads can create correctness or security problems."),
    (("serializer", "viewset", "router", "jwt", "cors", "api documentation", "postman", "api"), "An API contract defines request shape, validation, authorization, status codes, and response shape. A serializer validates representation; it does not grant permission.", "Test the API as an authenticated caller and include invalid, unauthorized, and boundary requests.", "Never trust client-supplied ownership fields or expose tokens in logs and URLs."),
    (("sql", "database", "postgresql", "relationship", "index", "transaction", "orm"), "A relational database stores related records under constraints. Query shape, indexes, transactions, and isolation affect correctness and performance.", "Use parameterized queries or ORM expressions, enforce constraints in the database, and inspect query counts.", "Missing indexes, N+1 queries, race conditions, and unsafe string interpolation are common hazards."),
    (("docker", "compose", "container"), "A container packages a process with its runtime dependencies; it is not a virtual machine or a security boundary by itself.", "Build reproducible images, run as a non-root user, limit secrets, and define health checks.", "Mutable tags, oversized images, and exposed ports can undermine repeatability and security."),
    (("security", "injection", "xss", "csrf", "authentication", "authorization", "permission", "secret", "prompt injection", "agent"), "Security decisions must be enforced by trusted server-side code. Untrusted text, model output, and uploaded files never become authority just because they look valid.", "Apply least privilege, validate at boundaries, use safe APIs, and require explicit approval for external side effects.", "Test malicious, malformed, unauthorized, and oversized inputs without using live credentials or systems."),
    (("cache", "redis", "celery", "background task", "email"), "Caching and background work change consistency and failure behavior. A queued task can be retried, delayed, duplicated, or permanently fail.", "Use explicit task state, idempotency, bounded retries, and clear cache invalidation rules.", "Do not assume exactly-once execution or store user-private results in a shared cache."),
    (("cloud", "aws", "deployment", "nginx", "gunicorn", "production", "github actions", "ci/cd", "monitoring", "logging"), "Production delivery needs reproducible builds, protected configuration, health signals, rollback, and an owner for incidents.", "Keep development and production settings separate, validate deployment configuration, and observe errors without exposing sensitive data.", "A successful build does not prove a safe rollout; monitor user outcomes after promotion."),
)

MONTH_COMMON_MISTAKES = {
    1: "Copying code without tracing values, using unclear names, and testing only one happy-path input.",
    2: "Adding abstraction before a clear requirement, ignoring exceptions, and leaving network-dependent tests nondeterministic.",
    3: "Mixing content, style, and behavior; ignoring keyboard/accessibility; and trusting browser validation as security.",
    4: "Putting business logic in templates or views, skipping migrations, and checking authentication without checking object ownership.",
    5: "Treating valid JSON as valid business data, confusing CORS with authorization, and trusting model/tool output.",
    6: "Committing secrets, deploying without rollback, relying on a single aggregate quality metric, and hiding operational failures.",
}

MONTH_TROUBLESHOOTING = {
    1: "Read the full traceback, reduce the input to the smallest failing case, inspect types and values, then add a test for the boundary.",
    2: "Reproduce with a deterministic test, isolate I/O behind a mock, inspect exceptions and logs, and verify that cleanup and cancellation work.",
    3: "Use browser developer tools to inspect the DOM, computed styles, console, network status, and accessibility behavior; then test a narrow viewport.",
    4: "Check URL resolution, middleware order, view response, form errors, migration state, SQL query count, and current user's permissions.",
    5: "Inspect request/response schema, serializer errors, authenticated identity, permission decision, database query, and provider/mock boundary separately.",
    6: "Check build artifact, environment configuration, health checks, logs/metrics, recent version changes, and the documented rollback or disable path.",
}

MONTH_COMMON_ERRORS = {
    1: "SyntaxError, NameError, TypeError, wrong indentation, accidental string/number mixing, and off-by-one loops.",
    2: "Import mismatch, swallowed exceptions, exhausted iterators, missing type validation, flaky tests, and unbounded concurrency.",
    3: "Invalid HTML nesting, CSS specificity surprises, stale DOM references, unhandled promises, and requests blocked by server policy.",
    4: "NoReverseMatch, template lookup failures, missing migrations, invalid form state, permission leaks, and inefficient QuerySets.",
    5: "Serializer mismatch, 401/403 confusion, CORS misconfiguration, invalid pagination, schema drift, and unverified AI output.",
    6: "Missing environment variables, container permission issues, failed health checks, unsafe defaults, noisy alerts, and untested rollback.",
}

MONTH_GUIDES = {
    1: ("Values and control flow", "Python evaluates expressions into values, binds names, and follows explicit branch or loop rules.", "Run a tiny example, inspect the value and type, and change one input to test the boundary."),
    2: ("Contracts and composition", "Professional Python becomes easier to extend when functions and objects expose small, testable contracts.", "Keep side effects at explicit boundaries and test reusable logic without live network services."),
    3: ("Browser and HTTP boundaries", "A web page combines semantic documents, styles, browser events, and network exchanges.", "Inspect the actual request and rendered DOM rather than assuming the browser did what the source intended."),
    4: ("Django request and data lifecycle", "Django maps a request through routing and middleware to a view, then coordinates models, forms, templates, and a response.", "Follow one request end-to-end and enforce authorization before reading or changing user-owned data."),
    5: ("API contracts and full-stack integration", "A full-stack feature crosses browser, API, validation, authorization, database, and service boundaries.", "Test each contract independently and make AI provider outputs untrusted data that must be validated."),
    6: ("Production lifecycle and agent safety", "A production feature includes build, release, observability, incident response, and retirement—not just application code.", "Use least privilege, explicit limits, evaluated changes, safe fallbacks, and tested rollback."),
}

MONTH_AI_BRIDGES = {
    1: "Ask an AI coding assistant to explain one concept or propose an edge-case test. Verify it by running a small local example and checking the official Python documentation. Never paste secrets or private data.",
    2: "Use a deterministic fake provider response while practicing APIs, typing, validation, async work, or tests. Keep provider code behind an interface; no live API key or paid call is needed.",
    3: "Build chat and streaming interface states against a local mock endpoint. Store no provider credential in browser code and test loading, error, retry, and cancellation states.",
    4: "Keep AI integration behind a Django service module. Enforce authenticated ownership before reading a document and return only validated, source-linked drafts.",
    5: "Design each RAG or agent step with source permissions, schema validation, a tool allowlist, a maximum-step budget, and an explicit abstain or human-approval path.",
    6: "Use mocked providers in tests, track version and cost metadata, test prompt injection and unsafe outputs, and require human approval before external side effects.",
}

DOC_LINKS = {
    "python": ("Python Tutorial", "https://docs.python.org/3/tutorial/"),
    "web": ("MDN Learn Web Development", "https://developer.mozilla.org/en-US/docs/Learn"),
    "django": ("Django Documentation", "https://docs.djangoproject.com/en/stable/"),
    "api": ("Django REST Framework", "https://www.django-rest-framework.org/"),
    "react": ("React Learn", "https://react.dev/learn"),
    "security": ("OWASP Top 10", "https://owasp.org/www-project-top-ten/"),
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError(f"Cannot create a folder name from {value!r}")
    return slug


def extract_section_titles(source: Path, start_marker: str, end_marker: str) -> list[str]:
    text = source.read_text(encoding="utf-8")
    try:
        section = text.split(start_marker, 1)[1].split(end_marker, 1)[0]
    except IndexError as error:
        raise ValueError(f"Could not find syllabus section {start_marker!r} in {source}") from error
    titles: list[str] = []
    expected = 1
    for line in section.splitlines():
        match = re.match(r"^\s*(\d{1,3})\.\s+(.+?)\s*$", line)
        if not match:
            continue
        number = int(match.group(1))
        if number != expected:
            continue
        titles.append(match.group(2).rstrip("."))
        expected += 1
        if expected == 181:
            break
    if len(titles) != 180:
        raise ValueError(f"Expected 180 ordered lesson titles in {source}, found {len(titles)}")
    return titles


def make_catalog(titles: list[str]) -> dict:
    lessons = []
    for day_number, title in enumerate(titles, start=1):
        month_number = (day_number - 1) // 30 + 1
        month = MONTHS[month_number - 1]
        lessons.append(
            {
                "day": day_number,
                "month": month_number,
                "month_slug": month["slug"],
                "month_name": month["name"],
                "title": title,
                "slug": slugify(title),
            }
        )
    return {"course": "Python Full Stack + AI Application + AI Agent Development", "days": lessons}


def get_topic_guide(title: str, month_number: int) -> tuple[str, str, str]:
    lowered = title.lower()
    for keywords, concept, method, boundary in TOPIC_GUIDES:
        if any(keyword in lowered for keyword in keywords):
            return concept, method, boundary
    core, method, boundary = MONTH_GUIDES[month_number]
    return f"{core}: {title} is the specific skill to practice today.", method, boundary


def python_example(code: str, expected: str, second: str | None = None, second_expected: str | None = None) -> list[dict]:
    examples = [{"language": "python", "code": code, "expected": expected}]
    if second:
        examples.append({"language": "python", "code": second, "expected": second_expected or "Inspect the printed value and explain the difference."})
    return examples


def examples_for(day_number: int, title: str, month_number: int) -> list[dict]:
    lowered = title.lower()
    if "introduction to programming" in lowered:
        return python_example(
            "task = 'calculate a study score'\ncompleted = 3\ntotal = 4\nprint(task, completed / total)",
            "calculate a study score 0.75",
            "input_value = 8\nresult = input_value * 2\nprint(result)",
            "16",
        )
    if "installing python" in lowered:
        return [
            {"language": "powershell", "code": "py -3 --version\npy -3 -m venv .venv\n.\\.venv\\Scripts\\python.exe -m pip --version", "expected": "The commands report the installed interpreter and the virtual environment's pip version. Exact version numbers depend on the machine."},
            {"language": "bash", "code": "python3 --version\npython3 -m venv .venv\n. .venv/bin/activate", "expected": "The commands report Python and create/activate an isolated environment on Linux or macOS."},
        ]
    if "interpreter and execution" in lowered:
        return [
            {"language": "python", "code": "print('source code is evaluated by the interpreter')", "expected": "source code is evaluated by the interpreter"},
            {"language": "powershell", "code": "python .\\hello.py\npython -c \"print(2 + 3)\"", "expected": "The first command runs a script; the second prints 5. The selected Python launcher may differ by installation."},
        ]
    if "variable" in lowered or "naming convention" in lowered:
        return python_example(
            "student_name = 'Ari'\nstudent_name = 'Mina'\nprint(student_name)",
            "Mina",
            "attempts = 0\nattempts += 1\nprint(attempts)",
            "1",
        )
    if "data type" in lowered:
        return python_example(
            "name = 'Ari'\nscore = 91\nis_ready = True\nprint(type(name).__name__, type(score).__name__, type(is_ready).__name__)",
            "str int bool",
            "values = [1, 2]\nprint(type(values).__name__, isinstance(values, list))",
            "list True",
        )
    if "nested condition" in lowered:
        return python_example(
            "score = 82\nsubmitted = True\nif submitted:\n    if score >= 70:\n        result = 'pass'\n    else:\n        result = 'retry'\nelse:\n    result = 'missing'\nprint(result)",
            "pass",
        )
    if "break, continue" in lowered:
        return python_example(
            "for number in range(1, 6):\n    if number == 2:\n        continue\n    if number == 5:\n        break\n    print(number)",
            "1\\n3\\n4",
            "for number in range(3):\n    pass\nprint('loop completed')",
            "loop completed",
        )
    if "list and dictionary methods" in lowered:
        return python_example(
            "scores = [70, 85]\nscores.append(92)\nprofile = {'name': 'Ari'}\nprofile.update({'active': True})\nprint(max(scores), profile['active'])",
            "92 True",
        )
    if "for loop" in lowered:
        return python_example(
            "scores = [72, 88, 91]\ntotal = 0\nfor score in scores:\n    total += score\nprint(total)",
            "251",
            "scores = []\nfor score in scores:\n    print(score)\nprint('count:', len(scores))",
            "count: 0",
        )
    if "while loop" in lowered:
        return python_example(
            "remaining = 3\nwhile remaining > 0:\n    print(remaining)\n    remaining -= 1",
            "3\\n2\\n1",
            "remaining = 0\nwhile remaining > 0:\n    remaining -= 1\nprint('stopped:', remaining)",
            "stopped: 0",
        )
    if "conditional" in lowered or "conditions" in lowered:
        return python_example(
            "score = 84\nif score >= 90:\n    grade = 'A'\nelif score >= 70:\n    grade = 'B'\nelse:\n    grade = 'C'\nprint(grade)",
            "B",
            "score = 69\nprint('pass' if score >= 70 else 'review')",
            "review",
        )
    if "list" in lowered:
        return python_example(
            "tasks = ['read', 'practice']\ntasks.append('review')\nprint(tasks[0], len(tasks))",
            "read 3",
            "tasks.remove('practice')\nprint(tasks)",
            "['read', 'review']",
        )
    if "tuple" in lowered:
        return python_example("point = (4, 7)\nx, y = point\nprint(x + y)", "11")
    if "set" in lowered:
        return python_example("tags = {'python', 'web', 'python'}\nprint(len(tags), 'web' in tags)", "2 True")
    if "dictionary" in lowered or "dictionaries" in lowered or "dict" in lowered:
        return python_example(
            "student = {'name': 'Ari', 'score': 86}\nstudent['score'] += 4\nprint(student['name'], student['score'])",
            "Ari 90",
        )
    if "string" in lowered:
        return python_example(
            "name = '  Ada Lovelace  '\nclean_name = name.strip()\nprint(clean_name.upper())",
            "ADA LOVELACE",
            "message = 'Python, Django'\nprint(message.split(', '))",
            "['Python', 'Django']",
        )
    if "type conversion" in lowered:
        return python_example("raw_count = '12'\ncount = int(raw_count)\nprint(count + 3)", "15")
    if "operator" in lowered:
        return python_example("price = 8\nquantity = 3\nsubtotal = price * quantity\nprint(subtotal >= 20)", "True")
    if "input and output" in lowered:
        return python_example("name = 'Sam'\nprint(f'Welcome, {name}!')", "Welcome, Sam!")
    if "parameters and arguments" in lowered:
        return python_example(
            "def make_label(name: str, prefix: str = 'Student') -> str:\n    return f'{prefix}: {name}'\n\nprint(make_label('Ari'))",
            "Student: Ari",
            "print(make_label('Mina', prefix='Learner'))",
            "Learner: Mina",
        )
    if "function" in lowered or "return statement" in lowered:
        return python_example("def add_tax(price: float, rate: float = 0.1) -> float:\n    return price * (1 + rate)\n\nprint(round(add_tax(20), 2))", "22.0")
    if "lambda" in lowered:
        return python_example("items = ['pear', 'fig', 'apple']\nprint(sorted(items, key=lambda item: len(item)))", "['fig', 'pear', 'apple']")
    if "exception" in lowered or "error handling" in lowered:
        return python_example("raw_value = '42'\ntry:\n    value = int(raw_value)\nexcept ValueError:\n    print('enter a whole number')\nelse:\n    print(value + 1)", "43")
    if "file handling" in lowered:
        return python_example("from io import StringIO\n\nwith StringIO('first line') as source:\n    print(source.read())", "first line")
    if "modules and packages" in lowered:
        return python_example("import math\n\nradius = 2\nprint(round(math.pi * radius ** 2, 2))", "12.57")
    if "json" in lowered or "csv" in lowered:
        return python_example("import json\n\nrecord = {'name': 'Mina', 'active': True}\nencoded = json.dumps(record)\nprint(json.loads(encoded)['active'])", "True")
    if "student management system" in lowered:
        return python_example(
            "students = [{'name': 'Ari', 'score': 82}, {'name': 'Mina', 'score': 94}]\nfor student in students:\n    print(student['name'], student['score'])",
            "Ari 82\\nMina 94",
            "passed = [student['name'] for student in students if student['score'] >= 90]\nprint(passed)",
            "['Mina']",
        )
    if "revision and assessment" in lowered:
        return python_example(
            "def average(values: list[float]) -> float:\n    if not values:\n        raise ValueError('values cannot be empty')\n    return sum(values) / len(values)\n\nassert average([2, 4]) == 3",
            "The assertion passes; an empty input raises ValueError.",
        )
    if "context manager" in lowered:
        return python_example("from contextlib import nullcontext\n\nwith nullcontext('ready') as value:\n    print(value)", "ready")
    if "class" in lowered or "object-oriented" in lowered or "dataclass" in lowered:
        return python_example("class Counter:\n    def __init__(self) -> None:\n        self.value = 0\n\n    def increment(self) -> int:\n        self.value += 1\n        return self.value\n\nprint(Counter().increment())", "1")
    if "generator" in lowered:
        return python_example("def squares(limit: int):\n    for value in range(limit):\n        yield value * value\n\nprint(list(squares(4)))", "[0, 1, 4, 9]")
    if "decorator" in lowered:
        return python_example("def announce(func):\n    def wrapper():\n        return f'result: {func()}'\n    return wrapper\n\n@announce\ndef answer():\n    return 42\n\nprint(answer())", "result: 42")
    if "comprehension" in lowered:
        return python_example("values = [1, 2, 3, 4]\nevens = [value for value in values if value % 2 == 0]\nprint(evens)", "[2, 4]")
    if "regular expression" in lowered:
        return python_example("import re\n\nmatch = re.fullmatch(r'[A-Z]{2}-\\d{3}', 'AB-123')\nprint(bool(match))", "True")
    if "date and time" in lowered:
        return python_example("from datetime import date\n\nrelease = date(2026, 1, 15)\nprint(release.isoformat())", "2026-01-15")
    if "logging" in lowered:
        return python_example("import logging\n\nlogging.basicConfig(level=logging.INFO)\nlogging.info('job finished: %s', 'demo')", "INFO:root:job finished: demo")
    if "unittest" in lowered or "pytest" in lowered or "testing" in lowered:
        return python_example("def total(values: list[int]) -> int:\n    return sum(values)\n\nassert total([2, 3]) == 5\nprint('test passed')", "test passed")
    if "type hint" in lowered or "typing" in lowered:
        return python_example("def greeting(name: str) -> str:\n    return f'Hello, {name}'\n\nprint(greeting('Ari'))", "Hello, Ari")
    if "async" in lowered or "asynchronous" in lowered:
        return python_example("import asyncio\n\nasync def main() -> None:\n    await asyncio.sleep(0)\n    print('done')\n\nasyncio.run(main())", "done")
    if "http" in lowered or "api" in lowered or "request" in lowered:
        return [
            {"language": "python", "code": "from urllib.parse import urlsplit\n\nparts = urlsplit('https://example.test/items?page=2')\nprint(parts.scheme, parts.path)", "expected": "https /items"},
            {"language": "text", "code": "GET /items?page=2 HTTP/1.1\nAccept: application/json", "expected": "A request describes a method, path, and accepted response type; a real server response is not assumed."},
        ]
    if month_number == 3 and any(word in lowered for word in ("css", "flexbox", "grid", "responsive", "animation")):
        return [
            {"language": "css", "code": ".card-list {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));\n  gap: 1rem;\n}", "expected": "Cards flow into columns that fit the available width; verify on narrow and wide viewports."},
            {"language": "css", "code": "@media (prefers-reduced-motion: reduce) {\n  *, *::before, *::after {\n    scroll-behavior: auto;\n    animation-duration: 0.01ms;\n  }\n}", "expected": "The stylesheet reduces non-essential motion when the user requests reduced motion."},
        ]
    if month_number == 3 and any(word in lowered for word in ("javascript", "dom", "event", "fetch", "promise", "array", "object")):
        return [
            {"language": "javascript", "code": "const status = document.querySelector('#status');\nstatus.textContent = 'Ready';", "expected": "The element with id status displays the text Ready, if that element exists."},
            {"language": "javascript", "code": "const items = [2, 4, 6];\nconsole.log(items.filter((item) => item > 3));", "expected": "The console shows [4, 6]."},
        ]
    if month_number == 3:
        return [
            {"language": "html", "code": "<main>\n  <h1>Study planner</h1>\n  <p>Track one small goal at a time.</p>\n</main>", "expected": "The browser renders a main landmark, heading, and paragraph in document order."},
            {"language": "text", "code": "Browser -> DNS -> Server -> HTTP response -> Rendered page", "expected": "A simplified request path; caching, proxies, TLS, and browser internals add further steps."},
        ]
    if month_number == 4:
        if "model" in lowered or "orm" in lowered or "query" in lowered or "database" in lowered:
            return [
                {"language": "python", "code": "class Article(models.Model):\n    title = models.CharField(max_length=120)\n    published = models.BooleanField(default=False)", "expected": "Django defines a model with a bounded title and an explicit publication state; apply migrations before querying it."},
                {"language": "python", "code": "articles = Article.objects.filter(published=True).order_by('title')", "expected": "A lazy QuerySet for published articles ordered by title; evaluate it only when needed."},
            ]
        if "url" in lowered or "routing" in lowered:
            return [{"language": "python", "code": "from django.urls import path\nfrom . import views\n\nurlpatterns = [path('articles/', views.article_list, name='article-list')]", "expected": "Requests matching /articles/ are routed to article_list; route names support reverse URL lookup."}]
        return [{"language": "python", "code": "from django.http import HttpResponse\n\ndef home(request):\n    return HttpResponse('Welcome')", "expected": "A Django view returns an HTTP response containing Welcome; run it inside a configured Django project."}]
    if month_number == 5:
        if "react" in lowered or "props" in lowered or "hooks" in lowered or "state" in lowered:
            return [
                {"language": "javascript", "code": "function Greeting({ name }) {\n  return <h1>Hello, {name}</h1>;\n}", "expected": "React renders a heading from the name prop; component setup is required."},
                {"language": "javascript", "code": "const [count, setCount] = useState(0);\nsetCount((current) => current + 1);", "expected": "React schedules the count state to increase by one."},
            ]
        if "sql" in lowered or "database" in lowered or "postgres" in lowered:
            return [{"language": "sql", "code": "SELECT title\nFROM lessons\nWHERE published = TRUE\nORDER BY title;", "expected": "A result set of published lesson titles ordered alphabetically; actual rows depend on the database."}]
        if "jwt" in lowered or "authentication" in lowered:
            return [{"language": "text", "code": "Request -> authenticate token -> identify user -> authorize object -> return response", "expected": "A conceptual sequence. Token validation and object authorization are distinct checks."}]
        if any(word in lowered for word in ("rag", "retrieval", "embedding", "agent", "tool", "llm", "ai ")):
            return python_example("documents = [{'id': 'guide#2', 'text': 'Rate limits protect shared services.'}]\nquery = 'rate limits'\nhits = [item for item in documents if query in item['text'].lower()]\nprint([item['id'] for item in hits])", "['guide#2']", "allowed_tools = {'search_lessons'}\nrequested_tool = 'search_lessons'\nprint(requested_tool in allowed_tools)", "True")
        return [{"language": "python", "code": "def validate_payload(payload: dict) -> bool:\n    return isinstance(payload.get('title'), str) and bool(payload['title'].strip())", "expected": "The function returns True only when title is a non-empty string."}]
    if month_number == 6:
        if "docker" in lowered or "container" in lowered or "compose" in lowered:
            return [{"language": "dockerfile", "code": "FROM python:3.12-slim\nWORKDIR /app\nCOPY . .\nCMD [\"python\", \"manage.py\", \"runserver\", \"0.0.0.0:8000\"]", "expected": "Illustrative development container only; production requires reviewed settings, a production server, and hardened image configuration."}]
        if "security" in lowered or "injection" in lowered or "csrf" in lowered or "xss" in lowered:
            return python_example("ALLOWED_TOOLS = {'search_lessons'}\nrequested = 'search_lessons'\nif requested not in ALLOWED_TOOLS:\n    raise PermissionError('tool not allowed')\nprint('approved')", "approved", "user_id = 7\nrecord_owner_id = 8\nprint(user_id == record_owner_id)", "False")
        if "sql" in lowered or "index" in lowered or "database" in lowered:
            return [{"language": "sql", "code": "CREATE INDEX lesson_published_created_idx\nON lessons (published, created_at);", "expected": "The database creates a composite index; confirm usefulness with representative query plans and data."}]
        return [{"language": "text", "code": "Build -> test -> approve -> canary -> monitor -> promote or roll back", "expected": "A release sequence with an explicit decision gate; real deployment commands depend on the reviewed target environment."}]
    return python_example("topic = " + repr(title) + "\nchecks = ['normal case', 'boundary case']\nprint(topic, len(checks))", f"{title} 2")


def python_companion_code(lesson: dict) -> str:
    day_number = lesson["day"]
    title = lesson["title"]
    month_number = lesson["month"]
    lowered = title.lower()
    header = (
        f'"""Standalone Python practice for Day {day_number:03}: {title}.\n\n'
        "Uses only Python's standard library and fictional local data. "
        "Framework and infrastructure concepts are simulated; no services are contacted.\n"
        '"""\n\n'
    )

    if day_number == 176:
        body = (
            "REQUIRED_CHECKS = {'acceptance_criteria', 'tests', 'diff_review', 'security_review'}\n\n"
            "def review_change(completed_checks: set[str]) -> tuple[bool, list[str]]:\n"
            "    missing = sorted(REQUIRED_CHECKS - completed_checks)\n"
            "    return not missing, missing\n\n"
            "draft_checks = {'acceptance_criteria', 'tests'}\n"
            "accepted, missing = review_change(draft_checks)\n"
            "print('Decision:', 'ACCEPT' if accepted else 'HOLD')\n"
            "print('Still required:', ', '.join(missing) or 'nothing')\n"
        )
        return header + body

    if month_number <= 2:
        if "installing python" in lowered:
            body = (
                "import sys\n\n"
                "print('Executable:', sys.executable)\n"
                "print('Version:', sys.version.split()[0])\n"
            )
        else:
            example = next(
                (item for item in examples_for(day_number, title, month_number) if item["language"] == "python"),
                None,
            )
            if example:
                body = example["code"].rstrip() + "\n"
            else:
                body = f"topic = {title!r}\nprint('Practice concept:', topic)\n"
        return header + body

    if month_number == 3:
        if any(word in lowered for word in ("css", "flexbox", "grid", "responsive", "animation", "transition")):
            body = (
                "def columns_for(viewport_width: int, card_width: int, gap: int) -> int:\n"
                "    if min(viewport_width, card_width) <= 0 or gap < 0:\n"
                "        raise ValueError('widths must be positive and gap cannot be negative')\n"
                "    return max(1, (viewport_width + gap) // (card_width + gap))\n\n"
                "print('columns:', columns_for(820, 260, 16))\n"
            )
        elif any(word in lowered for word in ("html", "semantic", "form", "validation")):
            body = (
                "from html import escape\n\n"
                "def render_labelled_input(label: str, value: str) -> str:\n"
                "    safe_label = escape(label)\n"
                "    safe_value = escape(value, quote=True)\n"
                "    return f'<label>{safe_label}<input value=\"{safe_value}\"></label>'\n\n"
                "print(render_labelled_input('Study goal', 'Python & web'))\n"
            )
        elif any(word in lowered for word in ("git", "github", "collaboration")):
            body = (
                "history = ['a1: create lesson outline']\n"
                "feature_branch = history + ['b2: add examples']\n"
                "main_branch = history + ['c3: review outline']\n"
                "print('shared base:', history[0])\n"
                "print('feature tip:', feature_branch[-1])\n"
                "print('main tip:', main_branch[-1])\n"
            )
        elif any(word in lowered for word in ("http", "dns", "client-server", "internet", "fetch")):
            body = (
                "from urllib.parse import urlsplit\n\n"
                "request_url = 'https://academy.example/lessons?page=2'\n"
                "parts = urlsplit(request_url)\n"
                "print('scheme:', parts.scheme)\n"
                "print('path:', parts.path)\n"
                "print('query:', parts.query)\n"
                "print('No network request was made.')\n"
            )
        else:
            body = (
                "def reduce_event(state: dict[str, int], event: str) -> dict[str, int]:\n"
                "    if event == 'increment':\n"
                "        return {**state, 'count': state.get('count', 0) + 1}\n"
                "    return state\n\n"
                "current = {'count': 0}\n"
                "print(reduce_event(current, 'increment'))\n"
            )
    elif month_number == 4:
        if any(word in lowered for word in ("model", "orm", "query", "database")):
            body = (
                "articles = [\n"
                "    {'title': 'Draft', 'published': False},\n"
                "    {'title': 'Guide', 'published': True},\n"
                "]\n"
                "visible = sorted(\n"
                "    (item for item in articles if item['published']),\n"
                "    key=lambda item: item['title'],\n"
                ")\n"
                "print([item['title'] for item in visible])\n"
            )
        elif any(word in lowered for word in ("form", "validation", "upload")):
            body = (
                "def validate_form(data: dict[str, str]) -> list[str]:\n"
                "    errors = []\n"
                "    if not data.get('title', '').strip():\n"
                "        errors.append('title is required')\n"
                "    return errors\n\n"
                "print(validate_form({'title': 'A lesson'}))\n"
                "print(validate_form({'title': '   '}))\n"
            )
        elif any(word in lowered for word in ("auth", "permission", "session", "login")):
            body = (
                "def can_view(user_id: int | None, owner_id: int) -> bool:\n"
                "    return user_id is not None and user_id == owner_id\n\n"
                "print('owner:', can_view(7, 7))\n"
                "print('other user:', can_view(8, 7))\n"
            )
        else:
            body = (
                "ROUTES = {'/': 'home', '/lessons': 'lesson_list'}\n\n"
                "def dispatch(path: str) -> tuple[int, str]:\n"
                "    view_name = ROUTES.get(path)\n"
                "    return (200, view_name) if view_name else (404, 'not_found')\n\n"
                "print(dispatch('/lessons'))\n"
                "print(dispatch('/missing'))\n"
            )
    elif month_number == 5:
        if any(word in lowered for word in ("rag", "retrieval", "embedding", "agent", "tool", "llm", "ai ")):
            body = (
                "documents = [\n"
                "    {'id': 'guide-1', 'text': 'Rate limits protect shared services.'},\n"
                "    {'id': 'guide-2', 'text': 'Tests check expected behavior.'},\n"
                "]\n"
                "query = 'rate limits'\n"
                "hits = [item['id'] for item in documents if query in item['text'].lower()]\n"
                "allowed_tools = {'search_lessons'}\n"
                "requested_tool = 'search_lessons'\n"
                "print('evidence:', hits)\n"
                "print('tool allowed:', requested_tool in allowed_tools)\n"
            )
        elif any(word in lowered for word in ("react", "props", "hooks", "state")):
            body = (
                "def reducer(state: dict[str, int], action: str) -> dict[str, int]:\n"
                "    if action == 'increment':\n"
                "        return {**state, 'count': state['count'] + 1}\n"
                "    return state\n\n"
                "state = {'count': 0}\n"
                "print(reducer(state, 'increment'))\n"
            )
        elif any(word in lowered for word in ("sql", "database", "postgres")):
            body = (
                "rows = [\n"
                "    {'title': 'Intro', 'published': True},\n"
                "    {'title': 'Draft', 'published': False},\n"
                "]\n"
                "print([row['title'] for row in rows if row['published']])\n"
            )
        elif any(word in lowered for word in ("auth", "permission", "cors", "jwt")):
            body = (
                "def may_read(user_id: int | None, owner_id: int) -> bool:\n"
                "    return user_id is not None and user_id == owner_id\n\n"
                "print(may_read(7, 7))\n"
                "print(may_read(8, 7))\n"
            )
        else:
            body = (
                "def validate_payload(payload: dict[str, object]) -> list[str]:\n"
                "    title = payload.get('title')\n"
                "    return [] if isinstance(title, str) and title.strip() else ['title is required']\n\n"
                "print(validate_payload({'title': 'A lesson'}))\n"
                "print(validate_payload({'title': ' '}))\n"
            )
    else:
        if any(word in lowered for word in ("security", "injection", "csrf", "xss", "authentication", "authorization")):
            body = (
                "ALLOWED_ACTIONS = {'read_status', 'view_logs'}\n"
                "for action in ('read_status', 'delete_everything'):\n"
                "    print(action, 'allowed' if action in ALLOWED_ACTIONS else 'blocked')\n"
            )
        elif any(word in lowered for word in ("docker", "container", "compose")):
            body = (
                "stages = ['choose base image', 'install dependencies', 'copy app', 'run health check']\n"
                "for number, stage in enumerate(stages, start=1):\n"
                "    print(f'{number}. {stage} (simulation)')\n"
                "print('No container was built or started.')\n"
            )
        elif any(word in lowered for word in ("database", "sql", "index")):
            body = (
                "records = [{'id': 1, 'published': True}, {'id': 2, 'published': False}]\n"
                "published_ids = [record['id'] for record in records if record['published']]\n"
                "print('matching ids:', published_ids)\n"
                "print('An index can speed repeated lookups; inspect real query plans before adding one.')\n"
            )
        elif any(word in lowered for word in ("cache", "redis", "celery", "background")):
            body = (
                "cache: dict[str, str] = {}\n\n"
                "def get_or_create(key: str, value: str) -> str:\n"
                "    return cache.setdefault(key, value)\n\n"
                "print(get_or_create('lesson:1', 'cached result'))\n"
                "print(get_or_create('lesson:1', 'new result'))\n"
            )
        elif any(word in lowered for word in ("monitor", "logging", "performance", "observability")):
            body = (
                "samples = [120, 150, 90]\n"
                "average_ms = sum(samples) / len(samples)\n"
                "print(f'average response: {average_ms:.1f} ms (synthetic)')\n"
            )
        else:
            body = (
                "stages = ['build', 'test', 'review', 'deploy to sample', 'check health']\n"
                "for stage in stages:\n"
                "    print(f'{stage}: ready (simulation)')\n"
                "print('No deployment or external service call was made.')\n"
            )
    return header + body


def explain_code(code: str, language: str) -> list[str]:
    explanations = []
    for number, line in enumerate(code.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            note = "comment documenting intent; it is not executed."
        elif stripped.startswith(("def ", "async def ")):
            note = "declares a callable and its input/output contract."
        elif stripped.startswith("class "):
            note = "declares a type or reusable structure."
        elif stripped.startswith(("if ", "elif ", "else:", "for ", "while ")):
            note = "selects or repeats a path based on a condition or iterable."
        elif stripped.startswith("return "):
            note = "returns a value to the caller."
        elif stripped.startswith(("import ", "from ")):
            note = "imports a standard-library or framework name used by the example."
        elif "=" in stripped and not stripped.startswith(("==", ">=", "<=")):
            note = "binds a name to a value or expression."
        elif stripped.startswith(("print(", "console.log(")):
            note = "displays a value for inspection."
        elif language in {"html", "css", "javascript", "sql", "dockerfile", "text"}:
            note = "contributes one part of the demonstrated document, style, request, query, or workflow."
        else:
            note = "applies the operation shown by the example."
        explanations.append(f"{number}. `{stripped}` — {note}")
    return explanations


def visualization_steps(day_number: int, title: str, month_number: int) -> list[str]:
    lowered = title.lower()
    if "loop" in lowered or "iteration" in lowered:
        return ["Initialize the input and state", "Check the stopping condition", "Process one item and update state", "Stop and inspect the result"]
    if month_number == 4:
        return ["Browser sends request", "URL and middleware select a view", "View validates data and calls model", "Django returns a response"]
    if month_number == 5:
        return ["Authenticate user and scope", "Validate API or tool request", "Run approved service work", "Return validated result and evidence"]
    if month_number == 6:
        return ["Version the change", "Run tests and security checks", "Approve and stage release", "Monitor, recover, or roll back"]
    if month_number == 3:
        return ["User action in the browser", "HTML and JavaScript handle state", "HTTP request crosses the network", "Render result or show error"]
    if day_number in (29, 59, 88, 119, 149, 176, 177, 180):
        return ["Define the requirement", "Build the smallest working slice", "Test normal and failure paths", "Review and explain the result"]
    return [f"Start with {title}", "Apply one explicit rule", "Inspect the output", "Try a boundary case"]


def lesson_diagrams(title: str, steps: list[str]) -> str:
    escaped_title = html.escape(title)
    flow_steps = "".join(
        f'<li class="flowchart-step"><span>{html.escape(step)}</span></li>'
        for step in steps
    )
    return f"""<section class="lesson-diagrams" aria-label="Visual diagrams for {html.escape(title, quote=True)}">
      <figure class="lesson-diagram">
        <figcaption>Concept flowchart: {escaped_title}</figcaption>
        <ol class="lesson-flowchart" data-concept-flowchart>
          {flow_steps}
          <li class="flowchart-decision">
            <span class="flowchart-diamond">Expected behavior?</span>
            <ul class="flowchart-branches">
              <li class="flowchart-success"><strong>Yes</strong><span>Record the result and explain why it matches.</span></li>
              <li class="flowchart-retry"><strong>Not yet</strong><span>Inspect the state and boundary case, then retry.</span></li>
            </ul>
          </li>
        </ol>
        <p class="diagram-caption">Follow the lesson stages, then use evidence to decide whether to finish or investigate.</p>
      </figure>
      <figure class="lesson-diagram">
        <figcaption>Concept map: {escaped_title}</figcaption>
        <ol class="concept-map" data-concept-map aria-label="Input, concept, and observable result">
          <li><span>INPUT</span><strong>Value, request, or state</strong></li>
          <li><span>CONCEPT</span><strong>{escaped_title}</strong></li>
          <li><span>RESULT</span><strong>Output or state change</strong></li>
        </ol>
        <p class="diagram-caption">Trace what enters the concept, what rule is applied, and what you can observe afterward.</p>
      </figure>
    </section>"""


def lesson_sections(lesson: dict, previous: dict | None) -> list[tuple[str, str]]:
    day_number = lesson["day"]
    month_number = lesson["month"]
    title = lesson["title"]
    month = MONTHS[month_number - 1]
    concept, method, boundary = get_topic_guide(title, month_number)
    examples = examples_for(day_number, title, month_number)
    steps = visualization_steps(day_number, title, month_number)
    prerequisites = (
        f"Day {previous['day']:03} — {previous['title']}; basic computer and file-system use."
        if previous
        else "No coding prerequisite. A text editor and a willingness to test small examples."
    )
    objectives = [
        f"Explain the central idea in {title} using your own words.",
        f"Trace how {title} changes an input, state, or user-facing result.",
        "Test one ordinary case and one boundary or failure case, then record what the evidence shows.",
    ]
    intro = (
        f"This session focuses on **{title}**. The goal is to understand the behavior well enough to build, test, and explain a small feature—not to memorize a definition. "
        f"It belongs to Month {month_number}: {month['name']}, where the course emphasis is {month['focus'].lower()}"
    )
    detailed = (
        f"### Core model\n{concept}\n\n"
        f"### A practical way to learn it\n{method} Start with the smallest example, name the inputs and expected result, then change one condition at a time. "
        f"Keep the code readable enough that another learner can predict what happens before running it.\n\n"
        f"### Boundaries and failure cases\n{boundary} Record the observed failure and the rule that prevents it; do not hide an error behind a plausible default.\n\n"
        f"### Connection to the application\nIn a full-stack system, this concept eventually crosses other boundaries: user input, validation, persistence, HTTP, or deployment. "
        f"Keep those responsibilities separate as the course grows."
    )
    syntax = (
        f"The exact syntax depends on the technology shown in today's examples. Read the example as a contract: identify inputs, transformation, output, and any side effect. "
        f"Use the official reference linked below before relying on a version-specific API."
    )
    code = []
    for index, example in enumerate(examples, start=1):
        code.append(f"### Example {index} ({example['language']})\n```{example['language']}\n{example['code']}\n```")
        code.append(f"Expected result: {example['expected']}")
    code_examples = "\n\n".join(code)
    line_by_line = "\n".join(
        explain_code(example["code"], example["language"])[i]
        for example in examples[:1]
        for i in range(len(explain_code(example["code"], example["language"])))
    ) or "Trace each statement from input to output and note any side effect."
    output = "\n\n".join(
        f"- Example {index}: {example['expected']}"
        for index, example in enumerate(examples, start=1)
    )
    applications = (
        f"Use {title.lower()} when a feature needs the behavior covered in this lesson. In a real application, place it at the layer that owns the rule, "
        "validate external data at the boundary, and add tests for the expected contract."
    )
    visualization = (
        "The lesson HTML includes an interactive stepper, a flowchart with success and retry branches, and a concept map from input to result. "
        "Use the diagrams to predict the behavior, inspect evidence, and reset before testing a different case. "
        "The visualizer does not execute arbitrary lesson code."
    )
    vibe_coding = (
        "Vibe coding is an AI-assisted way to explore and draft software through natural-language requests and short iterations. "
        "The developer remains accountable for requirements, architecture, privacy, security, and accepting the final change.\n\n"
        "1. Write acceptance criteria and name files or behaviors that must remain unchanged.\n"
        "2. Ask for one small, bounded change; inspect the proposed diff before running it.\n"
        "3. Run focused tests, then review edge cases, security, privacy, and dependency changes.\n"
        "4. Accept only when the evidence matches the criteria; otherwise revise or reject the draft.\n\n"
        "[Run the human-review checklist example](../../../examples/capstone/vibe_coding_workflow.py). "
        "It is deterministic and does not call an AI service."
    )
    common_errors = f"Typical Month {month_number} mistakes include {MONTH_COMMON_MISTAKES[month_number]} For this topic, also check whether the input shape and boundary conditions match the assumption in the example."
    troubleshooting = (
        f"1. Reproduce the issue with the smallest input.\n"
        f"2. Inspect the input type/value and the state immediately before the failing step.\n"
        f"3. Compare actual behavior with the contract for {title.lower()}.\n"
        f"4. Add a test for the failing boundary, apply one fix, and rerun it.\n"
        f"5. If the behavior depends on a framework or service, inspect its version and official documentation."
    )
    exercises = (
        f"1. Annotate the first example: identify its input, rule, and output for {title.lower()}.\n"
        f"2. Change one value or condition and predict the result before checking it.\n"
        f"3. Add a boundary case that could violate an assumption; write the expected behavior before implementing it."
    )
    assignment = (
        f"Create a small, isolated demonstration of **{title}**. Include a normal case, a boundary case, a short explanation of the result, and one test or manual verification step. "
        "Use synthetic data and keep unrelated framework or AI features out of the exercise."
    )
    quiz = (
        f"1. What is the core purpose of {title.lower()} in this example?\n"
        "2. Which boundary case would you test before using this behavior in an application?"
    )
    answers = (
        f"1. It applies the specific rule described in the core model above to produce or validate a result; the learner should be able to point to the exact input and operation.\n"
        f"2. A strong answer identifies an empty, malformed, unauthorized, duplicated, or boundary-value input appropriate to {title.lower()}, and states the expected safe behavior."
    )
    interview = (
        f"1. Explain {title.lower()} to a teammate and compare it with a simpler alternative.\n"
        "2. Describe a failure case, how you would reproduce it, and which test would prevent a regression."
    )
    revision = (
        f"- Core concept: {title}.\n"
        f"- Method: {method}\n"
        f"- Boundary: {boundary}"
    )
    further = "\n".join(
        f"- [{label}]({url})"
        for label, url in MONTHS[month_number - 1]["docs"]
    )
    ai_bridge = (
        f"{MONTH_AI_BRIDGES[month_number]} For today's topic, ask for a test idea about **{title.lower()}**, inspect the proposed test, then implement or revise it yourself. "
        "No live LLM call is required; a deterministic mock is sufficient."
    )
    security = (
        "Treat AI output, browser input, uploaded files, and external responses as untrusted. Keep secrets out of prompts and logs. "
        "Enforce identity, authorization, limits, and side-effect approval in ordinary server-side code."
        if month_number >= 2
        else "Use only toy input. Do not include passwords, API keys, personal data, or private repository code in an AI assistant prompt."
    )
    commit = f"Suggested commit: `learn: practice {lesson['slug']}`"
    checklist = "- [ ] I can explain the concept without notes.\n- [ ] I tried a normal and boundary case.\n- [ ] I can explain the example and its limitations."
    sections = [
        ("Learning Objectives", "\n".join(f"- {item}" for item in objectives)),
        ("Prerequisites", prerequisites),
        ("Introduction", intro),
        ("Detailed Explanation", detailed),
        ("Syntax", syntax),
        ("Code Examples", code_examples),
        ("Line-by-Line Explanation", line_by_line),
        ("Expected Output", output),
        ("Real-World Applications", applications),
        ("Interactive Visualization", visualization + "\n\nVisualization stages:\n" + "\n".join(f"- {step}" for step in steps)),
        ("Common Errors", common_errors),
        ("Troubleshooting", troubleshooting),
        ("Hands-on Exercises", exercises),
        ("Assignment", assignment),
        ("Quiz", quiz),
        ("Answers and Explanations", answers),
        ("Interview Questions", interview),
        ("Revision Summary", revision),
        ("Further Learning", further),
        ("AI and Security Connection", f"**AI bridge:** {ai_bridge}\n\n**Security note:** {security}\n\n{commit}"),
        ("Progress Checklist", checklist),
    ]
    if day_number == 176:
        insert_at = next(index for index, (heading, _) in enumerate(sections) if heading == "Hands-on Exercises")
        sections.insert(insert_at, ("Vibe Coding Workflow", vibe_coding))
    return sections


def markdown_for_lesson(lesson: dict, previous: dict | None) -> str:
    sections = lesson_sections(lesson, previous)
    month = MONTHS[lesson["month"] - 1]
    header = (
        f"# Day {lesson['day']:03} — {lesson['title']}\n\n"
        f"> Month {lesson['month']}: {month['name']} · Level: "
        f"{'Beginner' if lesson['month'] == 1 else 'Intermediate' if lesson['month'] < 5 else 'Advanced / job-ready'}\n\n"
        f"[Course dashboard](../../../frontend/index.html) · "
        f"[Month roadmap](../README.md) · "
        f"[Architecture and setup](../../../docs/architecture/overview.md) · "
        f"[Python companion](./{lesson['slug']}.py)\n"
    )
    body = "\n".join(f"\n## {heading}\n\n{content}\n" for heading, content in sections)
    return header + body


def inline_markdown(value: str) -> str:
    escaped = html.escape(value, quote=True)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)

    def render_link(match: re.Match[str]) -> str:
        label, target = match.groups()
        decoded_target = html.unescape(target)
        scheme = re.match(r"^([a-zA-Z][a-zA-Z0-9+.-]*):", decoded_target)
        if scheme and scheme.group(1).lower() not in {"http", "https"}:
            return label
        external = decoded_target.startswith(("http://", "https://"))
        security_attributes = ' rel="noopener noreferrer"' if external else ""
        return f'<a href="{target}"{security_attributes}>{label}</a>'

    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", render_link, escaped)
    return escaped


def markdown_fragment(markdown: str) -> str:
    output: list[str] = []
    in_code = False
    code_language = ""
    code_lines: list[str] = []
    in_list = False
    reveal = False
    paragraph: list[str] = []

    def close_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    for line in markdown.splitlines():
        if line.startswith("```"):
            close_paragraph()
            close_list()
            if in_code:
                output.append(f'<pre><code class="language-{html.escape(code_language, quote=True)}">{html.escape(chr(10).join(code_lines))}</code></pre>')
                code_lines.clear()
                in_code = False
            else:
                code_language = line[3:].strip()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if line.startswith("# "):
            close_paragraph()
            close_list()
            output.append(f"<h2>{inline_markdown(line[2:])}</h2>")
        elif line.startswith("## "):
            close_paragraph()
            close_list()
            if reveal:
                output.append("</div></details>")
                reveal = False
            heading = line[3:]
            if heading == "Answers and Explanations":
                output.append(f"<h2>{inline_markdown(heading)}</h2><details><summary>Reveal answer and explanation</summary><div>")
                reveal = True
            else:
                output.append(f"<h2>{inline_markdown(heading)}</h2>")
        elif line.startswith("### "):
            close_paragraph()
            close_list()
            output.append(f"<h3>{inline_markdown(line[4:])}</h3>")
        elif line.startswith("- "):
            close_paragraph()
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{inline_markdown(line[2:])}</li>")
        elif re.match(r"^\d+\.\s", line):
            close_paragraph()
            close_list()
            output.append(f"<p>{inline_markdown(line)}</p>")
        elif line.startswith("> "):
            close_paragraph()
            close_list()
            output.append(f"<blockquote>{inline_markdown(line[2:])}</blockquote>")
        elif not line.strip():
            close_paragraph()
            close_list()
        else:
            close_list()
            paragraph.append(line.strip())
    close_paragraph()
    close_list()
    if in_code:
        raise ValueError("Unclosed code fence in generated lesson.")
    if reveal:
        output.append("</div></details>")
    return "\n".join(output)


def html_for_lesson(lesson: dict, markdown: str, previous: dict | None, following: dict | None) -> str:
    month = MONTHS[lesson["month"] - 1]
    steps = visualization_steps(lesson["day"], lesson["title"], lesson["month"])
    step_items = "".join(f'<li data-step>{html.escape(step)}</li>' for step in steps)
    diagrams = lesson_diagrams(lesson["title"], steps)
    lab_by_month = {1: "python", 2: "python", 3: "web", 4: "web", 5: "ai", 6: "delivery"}
    lowered_title = lesson["title"].lower()
    topic_lab = next(
        (topic for keyword, topic in (
            ("docker", "docker"),
            ("aws", "aws"),
            ("github actions", "delivery"),
            ("github", "git"),
        ) if keyword in lowered_title),
        None,
    )
    if topic_lab is None and re.search(r"\bgit\b", lowered_title):
        topic_lab = "git"
    visualization_lab = topic_lab or lab_by_month[lesson["month"]]
    previous_link = (
        f'<a href="../{previous["slug"]}/lesson.html">Previous: Day {previous["day"]:03}</a>'
        if previous and previous["month"] == lesson["month"]
        else (
            f'<a href="../../{previous["month_slug"]}/{previous["slug"]}/lesson.html">Previous: Day {previous["day"]:03}</a>'
            if previous
            else ""
        )
    )
    next_link = (
        f'<a href="../{following["slug"]}/lesson.html">Next: Day {following["day"]:03}</a>'
        if following and following["month"] == lesson["month"]
        else (
            f'<a href="../../{following["month_slug"]}/{following["slug"]}/lesson.html">Next: Day {following["day"]:03}</a>'
            if following
            else ""
        )
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Day {lesson["day"]:03}: {html.escape(lesson["title"], quote=True)}">
  <title>Day {lesson["day"]:03}: {html.escape(lesson["title"])} | Python Full Stack Academy</title>
  <link rel="stylesheet" href="../../../frontend/css/style.css">
</head>
<body>
  <main class="lesson-page">
    <nav class="breadcrumbs"><a href="../../../frontend/index.html">Dashboard</a> / <a href="../index.html">{html.escape(month["name"])}</a></nav>
    <header class="lesson-hero"><p>DAY {lesson["day"]:03} OF 180 · MONTH {lesson["month"]}</p><h1>{html.escape(lesson["title"])}</h1><p>{html.escape(month["focus"])}</p></header>
    <section class="lesson-visual" data-stepper>
      <h2>Interactive concept flow</h2>
      <ol class="visual-steps">{step_items}</ol>
      <p class="step-status" aria-live="polite"></p>
      <div class="controls"><button type="button" data-action="previous">Previous</button><button type="button" data-action="next">Next</button><button type="button" data-action="play">Play</button><button type="button" data-action="reset">Reset</button></div>
      <p>This stepper explains the lesson flow; it does not execute arbitrary code.</p>
      <p><a href="{lesson["slug"]}.py" download>Download the {html.escape(lesson["title"])} Python companion</a></p>
      <p><a href="../../../visualizations/index.html?lab={visualization_lab}#deep-dive-labs">Open a {html.escape({"python": "Python", "web": "Web and Django", "ai": "AI systems", "delivery": "delivery", "docker": "Docker", "aws": "AWS", "git": "Git"}[visualization_lab])} deep-dive simulation</a></p>
    </section>
    {diagrams}
    <article class="lesson-content">{markdown_fragment(markdown)}</article>
    <nav class="lesson-navigation">{previous_link}{next_link}</nav>
  </main>
  <script src="../../../frontend/js/visualizer.js" defer></script>
</body>
</html>
"""


def write_month_pages(catalog: dict) -> None:
    for month_number, month in enumerate(MONTHS, start=1):
        month_root = ROOT / "curriculum" / month["slug"]
        month_root.mkdir(parents=True, exist_ok=True)
        lessons = [item for item in catalog["days"] if item["month"] == month_number]
        cards = []
        markdown_links = [
            f"- [Day {item['day']:03}: {item['title']}]({item['slug']}/README.md)"
            for item in lessons
        ]
        for item in lessons:
            cards.append(
                f'<li><span>Day {item["day"]:03}</span> <a href="{item["slug"]}/lesson.html">{html.escape(item["title"])}</a></li>'
            )
        readme = (
            f"# Month {month_number}: {month['name']}\n\n"
            f"{month['focus']}\n\n"
            f"Month project: **{month['project']}**.\n\n"
            "## Lessons\n\n" + "\n".join(markdown_links) + "\n"
        )
        (month_root / "README.md").write_text(readme, encoding="utf-8")
        month_html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Month {month_number}: {html.escape(month['name'])}</title><link rel="stylesheet" href="../../frontend/css/style.css"></head>
<body><main class="dashboard"><p><a href="../../frontend/index.html">Dashboard</a></p><header class="lesson-hero"><p>MONTH {month_number} · DAYS {(month_number - 1) * 30 + 1:03}-{month_number * 30:03}</p><h1>{html.escape(month['name'])}</h1><p>{html.escape(month['focus'])}</p></header><section class="panel"><h2>Month project: {html.escape(month['project'])}</h2><ol class="lesson-list">{''.join(cards)}</ol></section></main></body></html>"""
        (month_root / "index.html").write_text(month_html, encoding="utf-8")


def write_roadmap(catalog: dict) -> None:
    lines = [
        "# Course Roadmap",
        "",
        "Six months, 180 sequential lessons. The daily topics follow the supplied syllabus; AI practice is added as an extension without removing the original full-stack topics.",
        "",
    ]
    for month_number, month in enumerate(MONTHS, start=1):
        lines.extend(
            [
                f"## Month {month_number}: {month['name']}",
                "",
                f"**Focus:** {month['focus']}",
                "",
                f"**Monthly project:** {month['project']}",
                "",
            ]
        )
        for item in catalog["days"]:
            if item["month"] == month_number:
                href = f"curriculum/{item['month_slug']}/{item['slug']}/README.md"
                lines.append(f"- Day {item['day']:03}: [{item['title']}]({href})")
        lines.append("")
    (ROOT / "COURSE_ROADMAP.md").write_text("\n".join(lines), encoding="utf-8")


def write_dashboard_index(catalog: dict) -> None:
    payload = {"course": catalog["course"], "months": []}
    for month_number, month in enumerate(MONTHS, start=1):
        payload["months"].append(
            {
                "number": month_number,
                "slug": month["slug"],
                "name": month["name"],
                "focus": month["focus"],
                "lessons": [
                    {
                        "day": item["day"],
                        "title": item["title"],
                        "slug": item["slug"],
                        "markdown": f"../curriculum/{item['month_slug']}/{item['slug']}/README.md",
                        "html": f"../curriculum/{item['month_slug']}/{item['slug']}/lesson.html",
                    }
                    for item in catalog["days"]
                    if item["month"] == month_number
                ],
            }
        )
    (ROOT / "frontend" / "course-index.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_weekly_challenges(catalog: dict) -> None:
    directory = ROOT / "exercises" / "weekly"
    directory.mkdir(parents=True, exist_ok=True)
    for start in range(1, 181, 7):
        end = min(start + 6, 180)
        topics = [item["title"] for item in catalog["days"] if start <= item["day"] <= end]
        slug = f"week-{(start - 1) // 7 + 1:02}"
        text = (
            f"# {slug.title()} Challenge: Days {start:03}-{end:03}\n\n"
            f"## Concepts to integrate\n\n" + "\n".join(f"- {topic}" for topic in topics) + "\n\n"
            "## Challenge\n\n"
            "Build a small, testable slice that uses at least two concepts from this week. Keep input validation, error behavior, and the expected result explicit. "
            "For AI-related work, use a deterministic mock and preserve authorization and human-review boundaries.\n\n"
            "## Acceptance checklist\n\n"
            "- [ ] State the problem and constraints.\n- [ ] Demonstrate the normal path.\n- [ ] Test an edge or failure path.\n"
            "- [ ] Explain one design trade-off.\n- [ ] Record what was actually tested and what remains unverified.\n"
        )
        (directory / f"{slug}.md").write_text(text, encoding="utf-8")


def write_monthly_assessments(catalog: dict) -> None:
    directory = ROOT / "quizzes" / "monthly"
    directory.mkdir(parents=True, exist_ok=True)
    for month_number, month in enumerate(MONTHS, start=1):
        topics = [item["title"] for item in catalog["days"] if item["month"] == month_number]
        sample = [topics[index] for index in (2, 8, 15, 22, 28)]
        questions = "\n".join(
            f"{index}. Explain **{topic}** and name one test or failure case."
            for index, topic in enumerate(sample, start=1)
        )
        answers = "\n".join(
            f"{index}. A strong response explains the concept's input, rule, and result, then chooses a relevant boundary case and states expected behavior."
            for index in range(1, 6)
        )
        text = (
            f"# Month {month_number} Assessment: {month['name']}\n\n"
            f"Review Days {(month_number - 1) * 30 + 1:03}-{month_number * 30:03}. Attempt the questions before opening the answer key.\n\n"
            f"## Questions\n\n{questions}\n\n"
            f"## Answer key\n\n{answers}\n\n"
            f"## Practical checkpoint\n\nComplete the month project, {month['project']}, with a README, a normal-path demo, and at least one test or explicit manual verification. "
            "Do not claim coverage you did not run.\n"
        )
        (directory / f"month-{month_number:02}-assessment.md").write_text(text, encoding="utf-8")


def write_project_catalog(source: Path) -> None:
    text = source.read_text(encoding="utf-8")
    try:
        section = text.split("4. PROJECT-BASED LEARNING", 1)[1].split("5. INTERACTIVE VISUALIZATION SYSTEM", 1)[0]
    except IndexError:
        section = ""
    projects = []
    for line in section.splitlines():
        match = re.match(r"^\s*(\d{1,2})\.\s+(.+?)\s*$", line)
        if match and len(projects) < 20:
            projects.append(match.group(2).rstrip("."))
    if len(projects) != 20:
        projects = [
            "Calculator application", "Number guessing game", "Student management system", "Expense tracker",
            "File organizer automation", "Weather API application", "Personal portfolio website",
            "Responsive blog website", "Django blog application", "Student registration portal",
            "Employee management system", "Authentication and role management system", "REST API application",
            "E-commerce application", "Online learning management system", "Real-time chat application",
            "Task management application", "Full Stack Job Portal", "Inventory management system",
            "Production-ready Django + React capstone project",
        ]
    project_root = ROOT / "projects" / "briefs"
    for index, title in enumerate(projects, start=1):
        slug = slugify(title)
        folder = project_root / slug
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "README.md").write_text(
            f"""# Project {index:02}: {title}

**Status:** Project brief generated from the course syllabus. Source code is not included in this course-content generation stage.

## Problem and learner outcome

Build a small application that demonstrates **{title.lower()}**. Define a target user, the minimum useful workflow, and what the application intentionally does not do.

## Requirements

- Write acceptance criteria before implementation.
- Separate interface, validation, domain logic, and persistence where appropriate.
- Use synthetic sample data and documented local setup.
- Include normal, invalid-input, and failure-path tests.
- Add an architecture sketch and explain the most important design trade-off.

## AI extension

Use a deterministic mock first. If an AI feature is appropriate, keep provider calls behind a service boundary, validate output, enforce user permissions in server code, and require human review for external side effects. A project does not need an AI feature merely because the course includes AI.

## Security and verification

Do not commit credentials. Validate external input, protect user-owned data, and document dependencies. Report only tests actually run; deployment and production readiness require separate review.
""",
            encoding="utf-8",
        )
    catalog_md = ["# Project Brief Catalog", "", "These are scoped project briefs, not claims that the projects have been implemented.", ""]
    for index, title in enumerate(projects, start=1):
        catalog_md.append(f"{index}. [{title}](briefs/{slugify(title)}/README.md)")
    (ROOT / "projects" / "PROJECT_CATALOG.md").write_text("\n".join(catalog_md) + "\n", encoding="utf-8")


def build_lesson_files(catalog: dict) -> None:
    lessons = catalog["days"]
    for index, lesson in enumerate(lessons):
        previous = lessons[index - 1] if index else None
        following = lessons[index + 1] if index + 1 < len(lessons) else None
        folder = ROOT / "curriculum" / lesson["month_slug"] / lesson["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        markdown = markdown_for_lesson(lesson, previous)
        (folder / "README.md").write_text(markdown, encoding="utf-8")
        (folder / f"{lesson['slug']}.py").write_text(
            python_companion_code(lesson),
            encoding="utf-8",
        )
        (folder / "lesson.html").write_text(
            html_for_lesson(lesson, markdown, previous, following),
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the 180-day Python Full Stack + AI course.")
    parser.add_argument(
        "--source",
        type=Path,
        help="Path to python-full-stack-with-ai.txt; defaults to a copy in this workspace on first generation.",
    )
    args = parser.parse_args()
    if args.source:
        source = args.source.resolve()
        titles = extract_section_titles(source, "3. COMPLETE 180-DAY LEARNING ROADMAP", "4. PROJECT-BASED LEARNING")
        catalog = make_catalog(titles)
        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_project_catalog(source)
    elif CATALOG_PATH.is_file():
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    elif DEFAULT_SOURCE.is_file():
        titles = extract_section_titles(DEFAULT_SOURCE, "3. COMPLETE 180-DAY LEARNING ROADMAP", "4. PROJECT-BASED LEARNING")
        catalog = make_catalog(titles)
        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_project_catalog(DEFAULT_SOURCE)
    else:
        raise FileNotFoundError(
            f"Course catalog and source syllabus were not found. Run again with --source <path-to-python-full-stack-with-ai.txt>."
        )

    if len(catalog.get("days", [])) != 180:
        raise ValueError("The course catalog must contain exactly 180 lessons.")
    build_lesson_files(catalog)
    write_month_pages(catalog)
    write_roadmap(catalog)
    write_dashboard_index(catalog)
    write_weekly_challenges(catalog)
    write_monthly_assessments(catalog)
    print(f"Generated exactly {len(catalog['days'])} daily lessons across {len(MONTHS)} months.")


if __name__ == "__main__":
    main()
