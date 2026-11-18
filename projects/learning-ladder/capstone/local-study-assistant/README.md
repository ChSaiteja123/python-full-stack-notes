# Capstone Project: Local Study Assistant

Search a small, approved set of study notes, return matching source references, and refuse unapproved tool names. The project also practices **vibe coding**: use an AI assistant to draft one small change at a time, while the learner owns requirements, review, tests, and the final decision.

Run `python app.py`. The application is deterministic and offline: it does not call an LLM, execute shell commands, or connect to a provider.

Concepts: retrieval, evidence-backed answers, input normalization, tool allowlists, and human-supervised AI-assisted development.

## Vibe-coding workflow

1. Write acceptance criteria and identify files that should not change.
2. Ask for one small, bounded draft and inspect the proposed diff.
3. Run the tests and review security, privacy, and dependency changes.
4. Accept only if the evidence supports the criteria; otherwise revise or reject the draft.

The app remains deterministic and offline; this workflow does not imply a live AI integration.
