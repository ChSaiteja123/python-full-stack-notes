# Architecture and Implementation Status

## What runs today

```text
Browser
  ├─ /frontend/                 Static learning dashboard
  ├─ /curriculum/month-*/       180 Markdown + HTML lesson pairs
  ├─ /visualizations/           Eleven client-side interactive deep-dive labs
  └─ /consoles/                 Ten service-specific, local-only console simulations

Python standard-library generator
  ├─ reads the supplied syllabus (first generation or --source)
  ├─ writes curriculum/course_catalog.json
  └─ generates lesson pages, roadmap, dashboard catalog, challenges, and assessments
```

The dashboard uses browser `localStorage` for progress, bookmarks, and private study notes. It does not send this information to a server. Visual labs trace local sample data and decision branches; the console studio matches only a small allowlist of commands to fixed handlers. Neither evaluates arbitrary code, calls AI providers, uses real credentials, nor mutates external services.

## Deliberate scope limits

- No Django backend or database is implemented in this content-generation phase.
- No paid LLM API, provider SDK, API key, or external service call is made.
- The project directory contains scoped briefs, not completed applications.
- Code snippets are instructional; only Python syntax is checked automatically. Framework, browser, shell, SQL, and deployment examples need their stated environment and are not claimed to have been executed.
- The six-month curriculum includes AI integration, retrieval, and bounded-agent safety as learning topics; these are not presented as a deployed AI product.

## Content generation

`scripts/generate_course.py` parses the numbered 180-day roadmap from the supplied text file, assigns concept-based folder names, and generates the pages from one catalog. It does not delete files. Re-running it overwrites generated lesson content, so make curriculum edits in the source or generator.

## Next implementation stages

1. Review the generated curriculum and approve a first project brief.
2. Implement that project as a separate, tested application.
3. Only then add an optional Django/API backend if course progress needs to sync between devices.
4. Review privacy, permissions, provider costs, AI evaluation, and deployment before adding any live AI integration.
