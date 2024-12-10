from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os

class FileToolInput(BaseModel):
    """Input schema for FileTool."""
    content: str = Field(..., description="Content to write to the file")
    filename: str = Field(..., description="Name of the file to create")

class FileTool(BaseTool):
    name: str = "File Creator"
    description: str = "Creates a file with the provided content"
    args_schema: Type[BaseModel] = FileToolInput

    def _run(self, content: str, filename: str) -> str:
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return f"File created at {filename}"
        except Exception as e:
            return f"Error creating file: {str(e)}"
