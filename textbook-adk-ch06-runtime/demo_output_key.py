#!/usr/bin/env python3
"""
Demonstration of output_key pattern for automatic state saving.

This script shows how LlmAgent's output_key parameter automatically saves
agent responses to session state. This is the simplest ADK state management
pattern for capturing agent outputs.

Key characteristics:
- Agent response automatically saved to specified state key
- No manual state management required
- Perfect for capturing generated content, summaries, analyses
- Works with state injection via {key} templating in instructions

Based on: https://google.github.io/adk-docs/sessions/state/
"""

import asyncio
import uuid
from datetime import datetime
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import Session
from google.adk.sessions.session_service import SessionService


async def demonstrate_output_key():
    """
    Demonstrate output_key pattern with multiple agents saving to state.
    """
    print("🔑 Starting output_key Pattern Demo")
    print("=" * 50)
    
    # Create session for demonstration
    session_service = SessionService()
    session = Session(
        session_id=str(uuid.uuid4()),
        created_at=datetime.utcnow(),
        state={"research_topic": "Quantum Computing Applications"}
    )
    
    print(f"📋 Created session: {session.session_id}")
    print(f"   Initial state: {session.state}")
    print()
    
    # Demo 1: Simple greeting agent with output_key
    print("Demo 1: Greeting Agent with output_key")
    await demo_greeting_agent(session)
    
    # Demo 2: Research summary agent with state injection and output_key
    print("\nDemo 2: Research Summary with State Injection + output_key")
    await demo_research_summary_agent(session)
    
    # Demo 3: Analysis agent that builds on previous outputs
    print("\nDemo 3: Analysis Agent Building on Previous Outputs")
    await demo_analysis_agent(session)
    
    # Demo 4: Multiple output keys in sequence
    print("\nDemo 4: Sequential Output Keys Building Research")
    await demo_sequential_outputs(session)
    
    # Show final state with all saved outputs
    print("\n" + "=" * 50)
    print("📊 FINAL SESSION STATE (All output_key saves):")
    for key, value in sorted(session.state.items()):
        if len(str(value)) > 100:
            print(f"   {key}: {str(value)[:100]}...")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n✅ output_key pattern demo completed!")
    print("   Agent responses automatically saved to state!")


async def demo_greeting_agent(session: Session):
    """Demo simplest output_key usage - greeting saved to state."""
    
    greeting_agent = LlmAgent(
        name="GreetingAgent",
        model=LiteLlm(model="gemini-2.0-flash-exp"),
        instruction="Generate a friendly greeting for a research session. Be encouraging and mention the topic.",
        output_key="last_greeting"  # Response automatically saved here
    )
    
    print("   🤖 Running GreetingAgent with output_key='last_greeting'")
    
    # Run the agent - its response will automatically be saved to state["last_greeting"]
    response = await greeting_agent.run(
        session=session,
        input_text="Welcome me to the research session"
    )
    
    print(f"   ✅ Agent response saved to state['last_greeting']")
    print(f"   Response: {response.content.text[:100]}...")


async def demo_research_summary_agent(session: Session):
    """Demo output_key with state injection via {key} templating."""
    
    summary_agent = LlmAgent(
        name="ResearchSummaryAgent", 
        model=LiteLlm(model="gemini-2.0-flash-exp"),
        instruction="""
        Create a brief research summary for the topic: {research_topic}
        
        Previous greeting: {last_greeting}
        
        Focus on key areas to investigate and potential applications.
        """,
        output_key="research_summary"  # Summary automatically saved here
    )
    
    print("   🤖 Running ResearchSummaryAgent with state injection + output_key")
    print("      Uses {research_topic} and {last_greeting} from state")
    
    response = await summary_agent.run(
        session=session,
        input_text="Create a research summary"
    )
    
    print(f"   ✅ Summary saved to state['research_summary']")
    print(f"   Summary: {response.content.text[:100]}...")


async def demo_analysis_agent(session: Session):
    """Demo agent that analyzes previous outputs using state injection."""
    
    analysis_agent = LlmAgent(
        name="AnalysisAgent",
        model=LiteLlm(model="gemini-2.0-flash-exp"), 
        instruction="""
        Analyze the research summary and provide next steps.
        
        Topic: {research_topic}
        Summary to analyze: {research_summary}
        
        Suggest 3 specific research questions to explore.
        """,
        output_key="research_analysis"  # Analysis automatically saved
    )
    
    print("   🤖 Running AnalysisAgent building on previous outputs")
    print("      Analyzes research_summary from previous agent")
    
    response = await analysis_agent.run(
        session=session,
        input_text="Analyze the research summary and suggest next steps"
    )
    
    print(f"   ✅ Analysis saved to state['research_analysis']")
    print(f"   Analysis: {response.content.text[:100]}...")


async def demo_sequential_outputs(session: Session):
    """Demo multiple agents in sequence, each building on previous outputs."""
    
    # Agent 1: Literature review suggestions
    literature_agent = LlmAgent(
        name="LiteratureAgent",
        model=LiteLlm(model="gemini-2.0-flash-exp"),
        instruction="""
        Based on the research topic {research_topic} and analysis {research_analysis},
        suggest 5 key papers or books to review. Be specific with titles and authors if possible.
        """,
        output_key="literature_suggestions"
    )
    
    # Agent 2: Methodology recommendations  
    methodology_agent = LlmAgent(
        name="MethodologyAgent",
        model=LiteLlm(model="gemini-2.0-flash-exp"),
        instruction="""
        Given the research topic {research_topic} and literature {literature_suggestions},
        recommend specific research methodologies and experimental approaches.
        """,
        output_key="methodology_recommendations"
    )
    
    # Agent 3: Timeline creation
    timeline_agent = LlmAgent(
        name="TimelineAgent", 
        model=LiteLlm(model="gemini-2.0-flash-exp"),
        instruction="""
        Create a 6-month research timeline based on:
        - Topic: {research_topic}
        - Literature: {literature_suggestions}  
        - Methodology: {methodology_recommendations}
        
        Break it down into monthly milestones.
        """,
        output_key="research_timeline"
    )
    
    print("   🤖 Running sequential agents with chained output_key saves:")
    
    # Run agents in sequence, each building on previous outputs
    print("      1. Literature suggestions...")
    await literature_agent.run(session=session, input_text="Suggest key literature")
    
    print("      2. Methodology recommendations...")
    await methodology_agent.run(session=session, input_text="Recommend methodologies")
    
    print("      3. Research timeline...")  
    await timeline_agent.run(session=session, input_text="Create research timeline")
    
    print("   ✅ Three sequential outputs saved to state!")
    print(f"      - literature_suggestions: saved")
    print(f"      - methodology_recommendations: saved")  
    print(f"      - research_timeline: saved")


if __name__ == "__main__":
    print("output_key Pattern Demo")
    print("Demonstrates automatic state saving from agent responses")
    print("Based on: https://google.github.io/adk-docs/sessions/state/")
    print()
    
    asyncio.run(demonstrate_output_key())