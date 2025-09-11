"""
Enhanced Research State Agent - Comprehensive ADK State Management Demo

Demonstrates ALL recommended ADK state management patterns:
1. output_key for automatic state saving
2. State injection in instructions with {key} templating
3. EventActions.state_delta for complex updates
4. Direct state access in tool contexts
5. State scoping with prefixes (user:, app:, temp:)
6. Callback-based state management

Follows all patterns from https://google.github.io/adk-docs/sessions/state/
"""

from google.adk.agents import Agent, LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .prompts import AGENT_INSTRUCTION, STATEFUL_INSTRUCTION
from .tools.research_state_tools import (
    add_research_progress_tool,
    add_research_source_tool,
    get_research_status_tool,
    set_research_deadline_tool,
    set_research_priority_tool,
    set_research_topic_tool,
)
# Enhanced tools removed - they were incorrectly implemented
# See demo_manual_state_updates.py for proper "Standard Way" implementation

# Sub-agent demonstrating output_key - automatically saves response to state
greeting_agent = LlmAgent(
    name="GreetingAgent", 
    model=LiteLlm(model="gemini-2.0-flash-exp"),
    instruction="Generate a friendly, encouraging greeting for a research session. Reference the current topic if available.",
    output_key="last_greeting"  # Response automatically saved to state["last_greeting"]
)

# Sub-agent demonstrating state injection + output_key combination
summary_agent = LlmAgent(
    name="SummaryAgent",
    model=LiteLlm(model="gemini-2.0-flash-exp"),
    instruction=STATEFUL_INSTRUCTION,  # Uses {current_topic}, {priority_level} etc. from state
    output_key="research_summary"  # Summary automatically saved to state["research_summary"]
)

# Sub-agent for research analysis building on previous outputs
analysis_agent = LlmAgent(
    name="AnalysisAgent",
    model=LiteLlm(model="gemini-2.0-flash-exp"),
    instruction="""Analyze the current research status and provide insights.
    
    Topic: {current_topic}
    Last summary: {research_summary}
    Priority: {priority_level}
    
    Provide 3 specific next steps or research questions.""",
    output_key="research_analysis"  # Analysis automatically saved to state["research_analysis"]
)

# Main enhanced agent with comprehensive state management demonstrations
agent = Agent(
    model=LiteLlm(model="gemini-2.0-flash-exp"),
    name="enhanced_research_state_agent",
    instruction=AGENT_INSTRUCTION,
    tools=[
        # Simple state management tools (fixed to use proper patterns)
        get_research_status_tool,
        set_research_topic_tool, 
        add_research_progress_tool,
        set_research_priority_tool,
        set_research_deadline_tool,
        add_research_source_tool,
        # Advanced EventActions.state_delta tools removed - see standalone demo script
    ],
    # Demonstrates sub-agent delegation with output_key pattern
    agents=[greeting_agent, summary_agent, analysis_agent]
)