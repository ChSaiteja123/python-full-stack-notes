# Python Full Stack + AI Academy

A 180-day, concept-named learning path generated from the supplied `python-full-stack-with-ai.txt` syllabus. It preserves the original Python, web, Django, and full-stack sequence while adding practical, provider-neutral AI, RAG, agent-safety, testing, and deployment exercises.

## What is included

- 180 daily concept folders, each with a Markdown study note, standalone HTML lesson page containing an interactive stepper, concept flowchart, and input-to-result map, and a runnable Python companion script.
- Six month roadmaps and a searchable progress dashboard.
- Eleven interactive deep-dive labs for Python state tracing, Django request boundaries, retrieval, agent tool policy, CI/CD, Docker, AWS, Terraform, Ansible, Git, and Kubernetes.
- A local DevOps Console Studio for Docker, AWS, Grafana, Prometheus, Kubernetes, Terraform, Ansible, Git, Jenkins, and GitHub Actions. Supported commands operate only on fictional in-browser state.
- Daily lessons link to relevant visualization pathways. Simulations never call providers or mutate real systems.
- 26 weekly integration challenges, six monthly assessments, and 20 scoped project briefs.
- A zero-to-advanced [example ladder](examples/) and five runnable [progressive projects](projects/learning-ladder/), from first Python output through SQLite, deterministic retrieval, and a human-reviewed vibe-coding workflow.
- A standard-library generator and tests for syllabus coverage, lesson structure, local links, and Python example syntax.
- Official documentation links for the technologies used.

The project is a learning-content site, not a deployed Django application. No paid API, provider key, third-party package, or video-rendering service is required. AI examples use local mock data unless a later implementation explicitly adds and reviews a provider integration.

The DevOps Console Studio is intentionally simulated: it does not connect to vendor consoles, execute shell commands, read credentials, or change cloud resources, clusters, repositories, or pipelines.

## Start here

1. Follow [setup instructions](docs/setup/README.md).
2. Open the [course dashboard](frontend/index.html) through the local server.
3. Open the [DevOps Console Studio](consoles/index.html) to practice against local mock state.
4. Start with the [zero-to-advanced examples](examples/) or build the [project ladder](projects/learning-ladder/).
5. Use the [180-day roadmap](COURSE_ROADMAP.md) to browse lessons directly.
6. Read [architecture and implementation status](docs/architecture/overview.md).

## Regenerating lessons

From this directory, run:

```powershell
python scripts\generate_course.py
```

The generator uses the saved `curriculum/course_catalog.json`. To rebuild the catalog from the original syllabus:

```powershell
python scripts\generate_course.py --source ..\..\ai\ai-devops\visual-learning\python-full-stack-with-ai.txt
```

Generated lesson files are overwritten when regenerated; edit the generator or the source syllabus and regenerate rather than hand-editing generated lesson pages.

## Verification

```powershell
python -m unittest discover -s tests -v
```

Python snippets in lessons are syntax-checked by the tests. Framework, browser, shell, SQL, and deployment snippets are instructional examples and are not represented as executed or production-ready.
