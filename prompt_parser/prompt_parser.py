class PromptParser:
    """A class for parsing prompt text files."""

    def __init__(self):
        """Initialize the PromptParser."""
        self.prompt_text = None

    def parse_prompt(self, file_path: str) -> str:
        """
        Read and parse a prompt from a text file.

        Args:
            file_path (str): Path to the text file containing the prompt

        Returns:
            str: The contents of the prompt file as a string

        Raises:
            FileNotFoundError: If the specified file doesn't exist
            IOError: If there's an error reading the file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.prompt_text = file.read()
            return self.prompt_text
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        except IOError as e:
            raise IOError(f"Error reading prompt file: {str(e)}")
