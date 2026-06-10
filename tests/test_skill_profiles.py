import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "generate-technical-spec-pdf",
    "generate-project-report-pdf",
    "generate-incident-report-pdf",
    "generate-meeting-notes-pdf",
)


class SkillProfilesTest(unittest.TestCase):

    def test_specialized_skills_delegate_to_shared_engine(self):
        for skill_name in SKILLS:
            skill_text = (
                ROOT / "skills" / skill_name / "SKILL.md"
            ).read_text(encoding="utf-8")

            with self.subTest(skill=skill_name):
                self.assertIn("generate-professional-pdf", skill_text)
                self.assertIn("build_document_pdf.py", skill_text)
                self.assertNotIn("TODO", skill_text)
                self.assertNotIn("TBD", skill_text)

    def test_profile_examples_are_valid_and_complete(self):
        for skill_name in SKILLS:
            references = ROOT / "skills" / skill_name / "references"
            metadata = json.loads(
                (references / "metadata.example.json").read_text(
                    encoding="utf-8"
                )
            )
            profile = json.loads(
                (references / "validation-profile.example.json").read_text(
                    encoding="utf-8"
                )
            )

            with self.subTest(skill=skill_name):
                self.assertIn(
                    metadata["table_page_break"],
                    {"avoid", "auto"},
                )
                self.assertIn(
                    metadata["cover_page_break"],
                    {"always", "auto"},
                )
                self.assertTrue(profile["required_text"])
                self.assertTrue(profile["review_terms"])
                self.assertTrue(
                    (references / "outline.md").read_text(encoding="utf-8")
                )

    def test_technical_spec_routes_endpoint_contracts(self):
        skill_text = (
            ROOT
            / "skills"
            / "generate-technical-spec-pdf"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("generate-api-spec-pdf", skill_text)
        self.assertIn("endpoint", skill_text)


if __name__ == "__main__":
    unittest.main()
