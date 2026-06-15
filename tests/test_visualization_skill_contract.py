from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "generate-professional-pdf"


class VisualizationSkillContractTest(unittest.TestCase):

    def test_skill_routes_visual_work_to_renderer_and_reference(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("scripts/render_visual.py", skill)
        self.assertIn("references/visualizations.md", skill)

    def test_visualization_reference_covers_tools_and_quality_rules(self):
        reference = (
            SKILL_ROOT / "references" / "visualizations.md"
        ).read_text(encoding="utf-8")

        for term in [
            "Mermaid",
            "Graphviz",
            "Vega-Lite",
            "Gantt",
            "200%",
            "custom SVG",
            "제작 지침",
        ]:
            self.assertIn(term, reference)

    def test_reusable_visual_templates_are_bundled(self):
        templates = SKILL_ROOT / "assets" / "visualization"

        for filename in [
            "architecture.mmd",
            "gantt.mmd",
            "dependency.dot",
            "chart.vl.json",
            "mermaid-config.json",
        ]:
            self.assertTrue((templates / filename).is_file(), filename)


if __name__ == "__main__":
    unittest.main()
