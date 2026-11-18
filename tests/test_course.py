import json
import re
import unittest
import contextlib
import io
import runpy
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum"
REQUIRED_SECTIONS = (
    "Learning Objectives",
    "Prerequisites",
    "Introduction",
    "Detailed Explanation",
    "Syntax",
    "Code Examples",
    "Line-by-Line Explanation",
    "Expected Output",
    "Real-World Applications",
    "Interactive Visualization",
    "Common Errors",
    "Troubleshooting",
    "Hands-on Exercises",
    "Assignment",
    "Quiz",
    "Answers and Explanations",
    "Interview Questions",
    "Revision Summary",
    "Further Learning",
    "AI and Security Connection",
    "Progress Checklist",
)


def load_course_index():
    return json.loads((ROOT / "frontend" / "course-index.json").read_text(encoding="utf-8"))


def lesson_markdown_files():
    return sorted(
        path for path in CURRICULUM.glob("month-*/**/README.md")
        if path.parent.parent != CURRICULUM
    )


def lesson_python_files():
    return sorted(CURRICULUM.glob("month-*/**/*.py"))


class LocalReferenceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


class CourseGenerationTests(unittest.TestCase):
    def test_exactly_180_nonempty_markdown_and_html_lessons(self):
        lesson_markdown = lesson_markdown_files()
        lesson_html = sorted(CURRICULUM.glob("month-*/**/lesson.html"))
        lesson_python = lesson_python_files()
        self.assertEqual(len(lesson_markdown), 180)
        self.assertEqual(len(lesson_html), 180)
        self.assertEqual(len(lesson_python), 180)
        self.assertTrue(all(path.stat().st_size > 800 for path in lesson_markdown))
        self.assertTrue(all(path.stat().st_size > 800 for path in lesson_html))
        self.assertTrue(all(path.stat().st_size > 100 for path in lesson_python))

    def test_catalog_has_all_sequential_days_and_concept_folders(self):
        catalog = json.loads((CURRICULUM / "course_catalog.json").read_text(encoding="utf-8"))
        self.assertEqual([lesson["day"] for lesson in catalog["days"]], list(range(1, 181)))
        for lesson in catalog["days"]:
            self.assertNotRegex(lesson["slug"], r"^day-\d+")
            folder = CURRICULUM / lesson["month_slug"] / lesson["slug"]
            self.assertTrue((folder / "README.md").is_file())
            self.assertTrue((folder / f"{lesson['slug']}.py").is_file())

    def test_each_lesson_has_requested_sections_and_a_visual_stepper(self):
        for path in lesson_markdown_files():
            markdown = path.read_text(encoding="utf-8")
            for heading in REQUIRED_SECTIONS:
                self.assertIn(f"## {heading}", markdown, f"{heading} missing from {path}")
            self.assertIn("```", markdown, f"No code example in {path}")
            lesson_html = path.with_name("lesson.html").read_text(encoding="utf-8")
            self.assertIn('data-stepper', lesson_html)
            self.assertIn("data-concept-flowchart", lesson_html)
            self.assertIn("data-concept-map", lesson_html)
            self.assertIn("flowchart-success", lesson_html)
            self.assertIn("flowchart-retry", lesson_html)

    def test_generated_markdown_links_resolve(self):
        markdown_files = [ROOT / "COURSE_ROADMAP.md"]
        markdown_files.extend(CURRICULUM.glob("month-*/README.md"))
        markdown_files.extend(lesson_markdown_files())
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for path in markdown_files:
            for target in link_pattern.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("https://", "http://", "#")):
                    continue
                local_target = target.split("#", 1)[0]
                self.assertTrue((path.parent / local_target).is_file(), f"Broken link {target} in {path}")

    def test_lesson_html_references_resolve(self):
        for path in CURRICULUM.glob("month-*/**/lesson.html"):
            parser = LocalReferenceParser()
            parser.feed(path.read_text(encoding="utf-8"))
            for reference in parser.references:
                if reference.startswith(("https://", "http://", "#")):
                    continue
                local_target = urlsplit(reference).path
                if local_target:
                    self.assertTrue((path.parent / local_target).is_file(), f"Broken HTML reference {reference} in {path}")

    def test_interactive_labs_cover_core_pathways_and_have_controls(self):
        page = (ROOT / "visualizations" / "index.html").read_text(encoding="utf-8")
        for lab_id in ("python", "web", "ai", "delivery", "devops"):
            self.assertIn(f'data-lab="{lab_id}"', page)
        for simulator in (
            'id="python-state-lab"',
            'id="request-pipeline-lab"',
            'id="rag-retrieval-lab"',
            'id="agent-policy-lab"',
            'id="delivery-lab"',
            'id="docker-lab"',
            'id="aws-lab"',
            'id="terraform-lab"',
            'id="ansible-lab"',
            'id="git-lab"',
            'id="kubernetes-lab"',
        ):
            self.assertIn(simulator, page)
        for script_name, controls in (
            ("visualizer.js", ("data-loop-action", "data-request-action", "data-rag-action", "data-agent-action", "data-release-action")),
            ("infrastructure-labs.js", ("data-docker-action", "data-aws-action", "data-terraform-action", "data-ansible-action", "data-git-action", "data-k8s-action")),
        ):
            script = (ROOT / "frontend" / "js" / script_name).read_text(encoding="utf-8")
            for control in controls:
                self.assertIn(control, page)
                self.assertIn(control, script)

    def test_service_console_is_local_allowlisted_and_has_all_requested_tools(self):
        console_path = ROOT / "consoles" / "index.html"
        page = console_path.read_text(encoding="utf-8")
        for service in ("docker", "aws", "grafana", "prometheus", "kubernetes", "terraform", "ansible", "git", "jenkins", "actions"):
            self.assertIn(f'data-service="{service}"', page)
        self.assertIn("SIMULATION ONLY", page)
        script = (ROOT / "frontend" / "js" / "console-studio.js").read_text(encoding="utf-8")
        for command in ("docker ps", "aws sts get-caller-identity", "terraform plan", "ansible-playbook site.yml --check", "git status --short", "kubectl get pods", "rate(http_requests_total[5m])"):
            self.assertIn(command, script)
        self.assertNotRegex(script, r"\beval\s*\(")
        self.assertNotIn("fetch(", script)
        self.assertIn("needsConfirmation", script)
        parser = LocalReferenceParser()
        parser.feed(page)
        for reference in parser.references:
            local_path = urlsplit(reference).path
            if local_path and not reference.startswith(("https://", "http://")):
                self.assertTrue((console_path.parent / local_path).is_file(), f"Broken console asset {reference}")

    def test_daily_lessons_link_to_a_matching_deep_dive(self):
        for path in lesson_markdown_files():
            lesson_html = path.with_name("lesson.html").read_text(encoding="utf-8")
            self.assertRegex(
                lesson_html,
                r'href="\.\./\.\./\.\./visualizations/index\.html\?lab=(python|web|ai|delivery|docker|aws|git)#deep-dive-labs"',
                f"Missing visualization lab link in {path}",
            )

    def test_dashboard_links_resolve_to_lesson_pages(self):
        index = load_course_index()
        lessons = [lesson for month in index["months"] for lesson in month["lessons"]]
        self.assertEqual(len(index["months"]), 6)
        self.assertEqual(len(lessons), 180)
        for lesson in lessons:
            target = (ROOT / "frontend" / lesson["html"]).resolve()
            self.assertTrue(target.is_file(), f"Broken dashboard link for day {lesson['day']}")

    def test_python_code_blocks_are_syntactically_valid(self):
        code_block = re.compile(r"```python\s*\n(.*?)\n```", re.DOTALL)
        checked = 0
        for path in lesson_markdown_files():
            text = path.read_text(encoding="utf-8")
            for index, match in enumerate(code_block.finditer(text), start=1):
                compile(match.group(1), f"{path}:python-example-{index}", "exec")
                checked += 1
        self.assertGreaterEqual(checked, 120)

    def test_python_companion_scripts_compile_and_run(self):
        for path in lesson_python_files():
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                runpy.run_path(str(path), run_name="__main__")

    def test_capstone_lesson_teaches_vibe_coding_review(self):
        lesson = CURRICULUM / "month-06-production-deployment-and-job-readiness" / "capstone-project-development" / "README.md"
        content = lesson.read_text(encoding="utf-8")
        self.assertIn("## Vibe Coding Workflow", content)
        self.assertIn("vibe_coding_workflow.py", content)

    def test_project_briefs_are_explicitly_scoped_as_briefs(self):
        catalog = ROOT / "projects" / "PROJECT_CATALOG.md"
        self.assertTrue(catalog.is_file())
        briefs = list((ROOT / "projects" / "briefs").glob("*/README.md"))
        self.assertEqual(len(briefs), 20)
        self.assertTrue(all("Project brief" in path.read_text(encoding="utf-8") for path in briefs))


if __name__ == "__main__":
    unittest.main()
