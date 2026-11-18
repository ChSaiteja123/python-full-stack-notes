# Setup and Usage

## Requirements

- Python 3 for course generation and the local static server.
- A modern browser.
- No package installation is required for the generator, dashboard, tests, or visualizations.

The lesson sequence teaches additional tools such as Django, a database, and JavaScript frameworks. Those dependencies are not needed to browse or regenerate the course; follow the relevant lesson before installing them.

## Windows PowerShell

From the `python-full-stack-academy` directory:

```powershell
python scripts\generate_course.py
python -m http.server 8000
```

Open `http://localhost:8000/frontend/`. Keep the server running while using the dashboard and lesson pages. Stop it with `Ctrl+C`.

The DevOps Console Studio is at `http://localhost:8000/consoles/`. It is a local simulation: it never invokes a shell, contacts vendor APIs, or changes real resources.

To re-read the syllabus:

```powershell
python scripts\generate_course.py --source ..\..\ai\ai-devops\visual-learning\python-full-stack-with-ai.txt
```

## Linux and macOS

From the `python-full-stack-academy` directory:

```bash
python3 scripts/generate_course.py
python3 -m http.server 8000
```

Open `http://localhost:8000/frontend/`. The matching syllabus path, if needed, is `../../ai/ai-devops/visual-learning/python-full-stack-with-ai.txt`.

Open `http://localhost:8000/consoles/` for the local-only DevOps console simulations.

## Run the checks

```powershell
python -m unittest discover -s tests -v
```

The checks cover the exact lesson count, required section structure, concept-named paths, local lesson links, and Python snippet syntax. They do not execute Django, browser, SQL, deployment, or provider examples.

## Privacy and secrets

The static dashboard stores progress, bookmarks, and notes only in the current browser's local storage. Do not put passwords, API keys, or sensitive personal information in those notes. No API key is needed for this course.
