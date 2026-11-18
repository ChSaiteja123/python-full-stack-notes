import contextlib
import io
import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
PROJECTS = ROOT / "projects" / "learning-ladder"


class LearningLadderTests(unittest.TestCase):
    def test_examples_and_projects_cover_five_levels(self):
        levels = ("zero", "beginner", "intermediate", "advanced", "capstone")
        for level in levels:
            with self.subTest(level=level):
                self.assertTrue((EXAMPLES / level / "README.md").is_file())
                expected_examples = 2 if level == "capstone" else 1
                self.assertEqual(len(list((EXAMPLES / level).glob("*.py"))), expected_examples)
                project_files = list((PROJECTS / level).glob("*/app.py"))
                self.assertEqual(len(project_files), 1)
        self.assertTrue((EXAMPLES / "README.md").is_file())
        self.assertTrue((PROJECTS / "README.md").is_file())
        self.assertTrue((EXAMPLES / "index.html").is_file())
        self.assertTrue((PROJECTS / "index.html").is_file())
        self.assertIn('href="../examples/"', (ROOT / "frontend" / "index.html").read_text(encoding="utf-8"))
        self.assertIn(
            'href="../projects/learning-ladder/"',
            (ROOT / "frontend" / "index.html").read_text(encoding="utf-8"),
        )

    def test_vibe_coding_example_requires_human_review_gates(self):
        path = EXAMPLES / "capstone" / "vibe_coding_workflow.py"
        workflow = runpy.run_path(str(path))
        review_change = workflow["review_change"]
        accepted, missing = review_change({"acceptance_criteria", "tests"})
        self.assertFalse(accepted)
        self.assertEqual(missing, ["diff_review", "security_review"])
        accepted, missing = review_change(workflow["REQUIRED_CHECKS"].copy())
        self.assertTrue(accepted)
        self.assertEqual(missing, [])

    def test_all_ladder_scripts_compile_and_run(self):
        scripts = sorted(EXAMPLES.glob("*/*.py")) + sorted(PROJECTS.glob("*/*/app.py"))
        self.assertEqual(len(scripts), 11)
        for path in scripts:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
            with self.subTest(script=path.relative_to(ROOT)):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    runpy.run_path(str(path), run_name="__main__")

    def test_project_boundaries_and_normal_paths(self):
        registry_path = PROJECTS / "intermediate" / "student-registry" / "app.py"
        registry_module = runpy.run_path(str(registry_path))
        registry_type = registry_module["StudentRegistry"]
        registry = registry_type()
        registry.add(1, " Mina ", 90)
        restored = registry_type.from_json(registry.to_json())
        self.assertEqual(restored.average_score(), 90)
        with self.assertRaises(ValueError):
            restored.add(1, "Duplicate", 80)

        task_path = PROJECTS / "advanced" / "task-manager" / "app.py"
        task_module = runpy.run_path(str(task_path))
        manager = task_module["TaskManager"]()
        manager.add("Plan's review")
        self.assertEqual(manager.list_open(), [(1, "Plan's review")])
        manager.close()

        assistant_path = PROJECTS / "capstone" / "local-study-assistant" / "app.py"
        assistant_module = runpy.run_path(str(assistant_path))
        self.assertIn("web/http", assistant_module["answer"]("HTTP request method", "search_notes"))
        self.assertIn("refused", assistant_module["answer"]("anything", "run_shell").lower())


if __name__ == "__main__":
    unittest.main()
