from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool, ToolContext
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
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
    version = await tool_context.save_artifact(filename=filename,
                                               artifact=artifact)
    return {"status": "saved", "filename": filename, "version": version}








# Create a simple Agent that uses the tool
agent = LlmAgent(
    name="artifact_agent",
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    instruction="Use the save_text_artifact tool to store data.",
    tools=[FunctionTool(save_text_artifact)]
)

# runner = Runner(
#    agent=agent,
#    app_name="artifact_app",
#    session_service=InMemorySessionService(),
#    artifact_service=InMemoryArtifactService()
# )

# Run the agent with input that triggers artifact saving...
# Process the returned events and check event.actions.artifact_delta
