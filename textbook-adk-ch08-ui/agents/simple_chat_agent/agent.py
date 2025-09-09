#!/usr/bin/env python3
"""
Simple chat agent for Textual UI integration.

This agent provides basic conversational capabilities using the model specified in .env.
"""

import os

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool, ToolContext
from google.genai.types import Part


async def save_text_artifact(text: str, filename: str, tool_context: ToolContext):
    """
    Save a text string as an artifact.

    Args:
        text (str): The text content to save as a file artifact.
        filename (str): The name of the file to save the artifact under.

    Returns:
        dict: status
    """
    artifact = Part.from_bytes(data=text.encode("utf-8"), mime_type="text/plain")
    version = await tool_context.save_artifact(filename=filename, artifact=artifact)
    return {"status": "saved", "filename": filename, "version": version}


async def retrieve_artifact(filename: str, tool_context: ToolContext):
    """
    Retrieve the content of a saved artifact.

    Args:
        filename (str): The name of the artifact file to retrieve.

    Returns:
        dict: The artifact content and metadata, or error if not found.
    """
    try:
        # Load the artifact from the ADK artifact system using the correct method
        artifact = await tool_context.load_artifact(filename=filename)

        if artifact is None:
            return {
                "status": "error",
                "error": f"Artifact '{filename}' not found",
                "filename": filename,
            }

        # Extract the content using the correct ADK structure
        content = ""
        mime_type = "text/plain"

        if hasattr(artifact, "inline_data") and artifact.inline_data:
            # Access data via the inline_data property
            if hasattr(artifact.inline_data, "data") and artifact.inline_data.data:
                # Convert bytes to string if needed
                if isinstance(artifact.inline_data.data, bytes):
                    content = artifact.inline_data.data.decode("utf-8")
                else:
                    content = str(artifact.inline_data.data)

            # Get MIME type
            if (
                hasattr(artifact.inline_data, "mime_type")
                and artifact.inline_data.mime_type
            ):
                mime_type = artifact.inline_data.mime_type

        return {
            "status": "success",
            "filename": filename,
            "content": content,
            "content_length": len(content),
            "mime_type": mime_type,
        }

    except ValueError as e:
        # ValueError is specifically mentioned in ADK docs for artifact loading errors
        return {
            "status": "error",
            "error": f"Artifact '{filename}' not found: {str(e)}",
            "filename": filename,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to retrieve artifact '{filename}': {str(e)}",
            "filename": filename,
        }


class SimpleChatAgent(Agent):
    """A simple conversational agent for testing Textual UI integration."""

    def __init__(self):
        # Use model from environment with fallback
        model_name = os.getenv("ANTHROPIC_MODEL", "anthropic/claude-3-5-haiku-20241022")

        super().__init__(
            name="simple_chat_agent",
            description="A simple agent for testing Textual chat interfaces.",
            model=LiteLlm(model=model_name),
            instruction="""You are a helpful assistant. You can save text content as artifacts when explicitly requested.

ARTIFACT CREATION GUIDELINES:
- Only create artifacts when the user explicitly asks you to CREATE, SAVE, WRITE, or GENERATE something specific
- Do NOT create artifacts for requests that ask you to SHOW, DISPLAY, TELL, EXPLAIN, DESCRIBE, or TALK ABOUT something
- Do NOT create artifacts for simple questions or conversational responses
- Examples that should create artifacts:
  * "Create a document about..."
  * "Write a script that..."  
  * "Save this information as a file"
  * "Generate a report on..."
  * "Make a list and save it"

- Examples that should NOT create artifacts:
  * "Tell me about..."
  * "What is...?"
  * "Show me information about..."
  * "Explain how..."
  * "Describe the process of..."

When you do create artifacts, use descriptive filenames that reflect the content.

ARTIFACT RETRIEVAL:
- You can retrieve the content of previously saved artifacts using the retrieve_artifact tool
- When asked to "retrieve", "show content of", or "load" an artifact, use the retrieve_artifact tool with the filename
- Example: "Please retrieve the content of artifact: example.txt" should call retrieve_artifact with filename="example.txt" """,
            tools=[FunctionTool(save_text_artifact), FunctionTool(retrieve_artifact)],
        )
