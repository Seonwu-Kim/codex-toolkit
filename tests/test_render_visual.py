import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "skills"
    / "generate-professional-pdf"
    / "scripts"
    / "render_visual.py"
)


class RenderVisualTest(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.log_path = self.root / "calls.jsonl"

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_renderer(self, visual_type, executable, output_svg=True):
        self.make_fake_executable(executable, output_svg)
        source = self.root / {
            "mermaid": "diagram.mmd",
            "graphviz": "diagram.dot",
            "vega-lite": "chart.json",
        }[visual_type]
        source.write_text("source", encoding="utf-8")
        output = self.root / "result.svg"
        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}{os.pathsep}{env.get('PATH', '')}"
        env["VISUAL_TEST_LOG"] = str(self.log_path)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--type",
                visual_type,
                "--input",
                str(source),
                "--output",
                str(output),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        calls = []
        if self.log_path.exists():
            calls = [
                json.loads(line)
                for line in self.log_path.read_text(encoding="utf-8").splitlines()
            ]
        return result, output, calls

    def make_fake_executable(self, name, output_svg):
        executable = self.bin_dir / name
        payload = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 100 50"><text x="5" y="20">ok</text></svg>'
            if output_svg
            else "not svg"
        )
        executable.write_text(
            f"""#!{sys.executable}
import json
import os
from pathlib import Path
import sys

Path(os.environ["VISUAL_TEST_LOG"]).open("a", encoding="utf-8").write(
    json.dumps(sys.argv) + "\\n"
)
args = sys.argv[1:]
if Path(sys.argv[0]).name in {{"mmdc", "dot"}}:
    output = Path(args[args.index("-o") + 1])
else:
    output = Path(args[1])
output.write_text({payload!r}, encoding="utf-8")
""",
            encoding="utf-8",
        )
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)

    def test_mermaid_uses_pdf_compatible_config(self):
        result, output, calls = self.run_renderer("mermaid", "mmdc")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(output.exists())
        self.assertEqual("mmdc", Path(calls[0][0]).name)
        self.assertIn("-i", calls[0])
        self.assertIn("-o", calls[0])
        background_index = calls[0].index("-b")
        self.assertEqual("white", calls[0][background_index + 1])
        config_index = calls[0].index("-c")
        config = Path(calls[0][config_index + 1])
        self.assertTrue(config.is_file())
        config_json = json.loads(config.read_text(encoding="utf-8"))
        self.assertFalse(config_json["htmlLabels"])

    def test_graphviz_uses_dot_and_creates_valid_svg(self):
        result, output, calls = self.run_renderer("graphviz", "dot")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(output.exists())
        self.assertEqual("dot", Path(calls[0][0]).name)
        self.assertIn("-Tsvg", calls[0])

    def test_vega_lite_uses_vl2svg_and_scale(self):
        result, output, calls = self.run_renderer("vega-lite", "vl2svg")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(output.exists())
        self.assertEqual("vl2svg", Path(calls[0][0]).name)
        self.assertIn("-s", calls[0])

    def test_missing_renderer_reports_installation_hint(self):
        source = self.root / "diagram.mmd"
        source.write_text("flowchart LR", encoding="utf-8")
        env = os.environ.copy()
        env["PATH"] = str(self.root / "empty")

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--type",
                "mermaid",
                "--input",
                str(source),
                "--output",
                str(self.root / "result.svg"),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("@mermaid-js/mermaid-cli", result.stderr)

    def test_invalid_svg_output_is_rejected(self):
        result, output, _ = self.run_renderer(
            "graphviz",
            "dot",
            output_svg=False,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("valid SVG", result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
