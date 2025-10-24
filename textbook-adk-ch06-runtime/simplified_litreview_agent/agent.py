"""
Simplified Literature Review Agent - Comprehensive ADK State Management Demo

This agent demonstrates ALL recommended ADK state management patterns through
a realistic academic workflow: managing papers through a literature review pipeline.

State Management Patterns Demonstrated:
1. Direct state access in tools (tool_context.state)
2. output_key for automatic agent response saving  
3. State injection with {key} templating in instructions
4. Manual event creation for complex operations
5. State scoping with user:, app:, temp: prefixes
6. Database persistence across sessions

Based on: https://google.github.io/adk-docs/sessions/state/
"""

from google.adk.agents import Agent, LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .prompts import (
    MAIN_AGENT_INSTRUCTION,
    SUMMARY_AGENT_INSTRUCTION, 
    THEME_AGENT_INSTRUCTION,
    RECOMMENDATION_AGENT_INSTRUCTION,
    STAGE_GUIDANCE_MAP
)
from .tools.paper_tools import (
    add_paper_tool,
    search_papers_tool,
    get_pipeline_status_tool,
    set_research_query_tool
)
from .tools.screening_tools import (
    screen_paper_tool,
    batch_screen_papers_tool,
    update_screening_criteria_tool
)


def _get_stage_guidance(state: dict) -> str:
    """Get stage-specific guidance based on current pipeline stage."""
    stage = state.get("pipeline_stage", "initialization")
    return STAGE_GUIDANCE_MAP.get(stage, "Ready to help with literature review tasks!")


# Sub-agent that demonstrates output_key pattern for paper summaries
summary_agent = LlmAgent(
    name="SummaryAgent",
    model=LiteLlm(model="gemini-2.0-flash-exp"),
    instruction=SUMMARY_AGENT_INSTRUCTION,  # Uses state injection
    output_key="paper_summary"  # Automatically saves response to state["paper_summary"]
)

# Sub-agent that demonstrates theme extraction with output_key
theme_agent = LlmAgent(
    name="ThemeAgent", 
    model=LiteLlm(model="gemini-2.0-flash-exp"),
    instruction=THEME_AGENT_INSTRUCTION,  # Uses state injection
    output_key="extracted_themes"  # Automatically saves to state["extracted_themes"]
)

# Sub-agent for research recommendations with output_key
recommendation_agent = LlmAgent(
    name="RecommendationAgent",
    model=LiteLlm(model="gemini-2.0-flash-exp"), 
    instruction=RECOMMENDATION_AGENT_INSTRUCTION,  # Uses state injection
    output_key="research_recommendations"  # Automatically saves to state["research_recommendations"]
)

# Sub-agent for generating search queries
query_agent = LlmAgent(
    name="QueryAgent",
    model=LiteLlm(model="gemini-2.0-flash-exp"),
    instruction="""
    Generate effective academic search queries based on current research focus.
    
    Current focus: {current_search_query}
    Research interests: {user_research_interests}
    Papers already found: {papers_in_pipeline}
    
    Suggest 3-5 alternative search terms or query refinements that could help
    find additional relevant papers. Consider synonyms, related concepts, and
    different academic terminology.
    """,
    output_key="suggested_queries"  # Saves query suggestions to state
)


def _inject_stage_guidance(instruction: str, state: dict) -> str:
    """
    Inject stage-specific guidance into the main agent instruction.
    
    This demonstrates advanced state injection where we modify instructions
    based on current state values.
    """
    stage_guidance = _get_stage_guidance(state)
    return instruction.format(stage_guidance=stage_guidance, **state)


# Main literature review agent with comprehensive state management
agent = Agent(
    model=LiteLlm(model="gemini-2.0-flash-exp"),
    name="simplified_litreview_agent", 
    instruction=MAIN_AGENT_INSTRUCTION,  # Uses extensive state injection
    tools=[
        # Paper management tools (direct state access)
        add_paper_tool,
        search_papers_tool, 
        get_pipeline_status_tool,
        set_research_query_tool,
        
        # Screening tools (manual event creation)
        screen_paper_tool,
        batch_screen_papers_tool,
        update_screening_criteria_tool,
    ],
    # Sub-agents demonstrating output_key pattern
    sub_agents=[
        summary_agent,
        theme_agent, 
        recommendation_agent,
        query_agent
    ]
)