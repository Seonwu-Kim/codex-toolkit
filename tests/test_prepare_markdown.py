import sys
import unittest
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "generate-api-spec-pdf"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

from prepare_markdown import prettify_json


class PrettifyJsonTest(unittest.TestCase):

    def test_formats_nested_json_with_prettier_style_brackets(self):
        source = (
            '{"data":[{"id":"1","items":[{"name":"A"},{"name":"B"}]}],'
            '"page":{"size":20,"number":0}}'
        )

        formatted = prettify_json(source)

        self.assertEqual(
            """{
  "data": [
    {
      "id": "1",
      "items": [
        {
          "name": "A"
        },
        {
          "name": "B"
        }
      ]
    }
  ],
  "page": {
    "size": 20,
    "number": 0
  }
}""",
            formatted,
        )

    def test_rejects_trailing_comma_with_location(self):
        with self.assertRaisesRegex(
            ValueError,
            r"Invalid JSON example at line 1, column 19:",
        ):
            prettify_json('{"data": [{"id": 1,}],}')

    def test_rejects_non_standard_constants(self):
        with self.assertRaisesRegex(
            ValueError,
            r"Invalid JSON example: unsupported constant NaN",
        ):
            prettify_json('{"score": NaN}')

    def test_rejects_duplicate_keys(self):
        with self.assertRaisesRegex(
            ValueError,
            r"Invalid JSON example: duplicate key 'id'",
        ):
            prettify_json('{"id": "1", "id": "2"}')

    def test_preserves_ascii_delimiters_and_escaped_quotes(self):
        formatted = prettify_json(
            '{"message":"그는 \\"확인 완료\\"라고 답했습니다.",'
            '"quote":"“스마트 따옴표”"}'
        )

        self.assertIn(
            '"message": "그는 \\"확인 완료\\"라고 답했습니다."',
            formatted,
        )
        self.assertIn('"quote": "“스마트 따옴표”"', formatted)

    def test_rejects_smart_quotes_used_as_json_delimiters(self):
        with self.assertRaisesRegex(
            ValueError,
            r"Invalid JSON example at line 1, column 2:",
        ):
            prettify_json('{“id”: “1”}')


if __name__ == "__main__":
    unittest.main()
