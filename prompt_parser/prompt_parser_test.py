import os
import tempfile
import unittest

from prompt_parser.prompt_parser import PromptParser


class TestPromptParser(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parser = PromptParser()
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_parse_valid_prompt(self):
        """Test parsing a valid prompt file."""
        # Create a test prompt file
        test_content = "This is a test prompt\nwith multiple lines."
        test_file = os.path.join(self.temp_dir, "test_prompt.txt")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Parse the prompt
        result = self.parser.parse_prompt(test_file)

        # Assert the result matches the original content
        self.assertEqual(result, test_content)
        self.assertEqual(self.parser.prompt_text, test_content)

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")

        with self.assertRaises(FileNotFoundError):
            self.parser.parse_prompt(nonexistent_file)

    def test_parse_empty_file(self):
        """Test parsing an empty file."""
        empty_file = os.path.join(self.temp_dir, "empty.txt")

        # Create an empty file
        open(empty_file, "w").close()

        # Parse the empty file
        result = self.parser.parse_prompt(empty_file)

        # Assert the result is an empty string
        self.assertEqual(result, "")
        self.assertEqual(self.parser.prompt_text, "")


if __name__ == "__main__":
    unittest.main()
