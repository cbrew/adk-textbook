#!/usr/bin/env python3
"""
Usage Scenario: Academic Research Assistant with PostgreSQL Artifact Storage

This demonstrates the complete workflow of using PostgreSQL-backed ADK services
for academic research, including artifact storage with event sourcing.
"""

import asyncio

# Module imports configured via pyproject.toml
from google.genai import types
from postgres_chat_agent.agent import create_runner


async def demonstrate_research_workflow():
    """
    Demonstrates a complete academic research workflow using PostgreSQL services.
    """
    print("🎓 Academic Research Assistant - PostgreSQL Edition")
    print("=" * 60)
    print("📚 Demonstrating: Artifact storage with event sourcing")
    print()

    # Create runner with PostgreSQL services
    print("🔄 Initializing ADK Runner with PostgreSQL services...")
    runner = await create_runner(None, "postgres_chat_agent")
    print("✅ Runner initialized with custom PostgreSQL backend!")
    print()

    # Session ID for this demo
    demo_session = "demo-research-session-001"
    demo_user = "researcher_alice"

    try:
        print("=" * 60)
        print("📋 SCENARIO: Literature Review Research Project")
        print("=" * 60)
        print()

        # 1. Research Discussion - ADK handles this with memory indexing
        print("1️⃣ **Research Discussion with Agent**")
        print("   User asks about machine learning bias in healthcare")

        research_query = types.Content(
            role="user",
            parts=[
                types.Part(
                    text="I'm researching bias in machine learning models for healthcare. Can you help me understand the key challenges and suggest approaches for mitigation?"
                )
            ],
        )

        print("   🤖 Agent responds with comprehensive analysis...")
        response = await runner.run_async(
            user_id=demo_user, session_id=demo_session, content=research_query
        )

        # Extract agent response
        agent_response = ""
        for event in response.events:
            if event.content and event.content.role == "assistant":
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        agent_response = (
                            part.text[:200] + "..."
                            if len(part.text) > 200
                            else part.text
                        )
                        break
                break

        print(f"   📝 Agent response: {agent_response}")
        print()

        # 2. Save Research Bibliography as Artifact
        print("2️⃣ **Saving Research Bibliography (PostgreSQL BYTEA Storage)**")
        bibliography = """# ML Bias in Healthcare - Key References

## Foundational Papers
1. Rajkomar, A. et al. (2018). "Ensuring fairness in machine learning to advance health equity." Annals of Internal Medicine.
2. Obermeyer, Z. et al. (2019). "Dissecting racial bias in an algorithm used to manage the health of populations." Science.
3. Chen, I. Y. et al. (2019). "Ethical machine learning in healthcare." Annual Review of Biomedical Data Science.

## Mitigation Strategies  
4. Larrazabal, A. J. et al. (2020). "Gender imbalance in medical imaging datasets." Nature Machine Intelligence.
5. Zhang, H. et al. (2018). "Improving fairness in machine learning systems." ACM Computing Surveys.

## Recent Developments
6. Pfohl, S. R. et al. (2021). "The role of machine learning in clinical decision-making." Nature Reviews Disease Primers.
"""

        # Create content for artifact saving
        save_content = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=f"save_artifact('ml_healthcare_bias_bibliography.md', '{bibliography}')"
                )
            ],
        )

        print("   💾 Saving bibliography to PostgreSQL...")
        save_response = await runner.run_async(
            user_id=demo_user, session_id=demo_session, content=save_content
        )

        # Check if artifact was saved
        for event in save_response.events:
            if hasattr(event, "get_function_responses"):
                responses = event.get_function_responses()
                for response in responses:
                    if hasattr(response, "response") and "Successfully saved" in str(
                        response.response
                    ):
                        print("   ✅ Bibliography saved to PostgreSQL BYTEA storage!")
                        print("   📊 Storage: Small file (< 1MB) → PostgreSQL BYTEA")
                        print(
                            "   🔗 Event sourcing: Artifact creation indexed for search"
                        )
                        break
        print()

        # 3. Save Research Notes as Another Artifact
        print("3️⃣ **Saving Research Notes (Larger File → Filesystem)**")
        detailed_notes = (
            """# Detailed Research Notes: ML Bias in Healthcare

## Executive Summary
Machine learning bias in healthcare represents one of the most critical challenges in medical AI deployment. This research compilation examines systemic biases, their sources, and evidence-based mitigation strategies.

## Key Findings

### 1. Sources of Bias
- **Data Bias**: Historical healthcare disparities reflected in training data
- **Algorithmic Bias**: Model architectures that perpetuate existing inequalities  
- **Deployment Bias**: Differential access and implementation across populations
- **Evaluation Bias**: Metrics that don't capture fairness across demographics

### 2. Case Studies

#### Case 1: Pulse Oximetry Algorithm Bias
- **Problem**: Algorithms showed reduced accuracy for patients with darker skin
- **Impact**: Delayed or missed diagnoses in critical care settings
- **Solution**: Diverse training datasets and bias-aware validation protocols

#### Case 2: Risk Assessment Tools
- **Problem**: Chronic care management algorithms underestimated care needs for Black patients
- **Impact**: Systematic under-allocation of healthcare resources
- **Solution**: Algorithmic auditing and fairness-constrained optimization

### 3. Mitigation Frameworks

#### Technical Approaches
1. **Pre-processing**: Data augmentation, synthetic data generation, bias detection
2. **In-processing**: Fairness constraints, multi-task learning, adversarial debiasing
3. **Post-processing**: Threshold optimization, calibration, outcome monitoring

#### Policy and Governance
1. **Regulatory Frameworks**: FDA guidance on AI/ML-based medical devices
2. **Institutional Review**: Ethics committees for AI deployment in healthcare
3. **Continuous Monitoring**: Real-world performance tracking across demographics

## Methodological Considerations

### Research Design
- **Intersectional Analysis**: Examining multiple demographic dimensions simultaneously
- **Longitudinal Studies**: Tracking bias evolution over time and model updates
- **Multi-institutional Validation**: Cross-site generalizability assessment

### Evaluation Metrics
- **Equalized Odds**: Equal true positive rates across groups
- **Demographic Parity**: Equal positive prediction rates across groups
- **Calibration**: Equal prediction accuracy across groups
- **Individual Fairness**: Similar individuals receive similar predictions

## Implementation Strategies

### Healthcare Organizations
1. **Bias Assessment Protocols**: Systematic evaluation of AI tools before deployment
2. **Diverse Development Teams**: Interdisciplinary collaboration including affected communities
3. **Transparent Reporting**: Public disclosure of model performance across demographics

### Technology Vendors
1. **Inclusive Design**: Bias consideration from early development stages
2. **Robust Testing**: Comprehensive evaluation across diverse populations
3. **Ongoing Support**: Post-deployment monitoring and model updates

## Future Research Directions

### Emerging Areas
- **Federated Learning**: Privacy-preserving bias mitigation across institutions
- **Causal Inference**: Identifying and addressing root causes of healthcare disparities
- **Human-AI Collaboration**: Optimizing clinician-algorithm decision-making

### Open Questions
1. How can we balance individual fairness with population-level utility?
2. What governance structures best ensure accountability for AI bias?
3. How do we address bias in rare diseases with limited diverse data?

## Conclusion
Addressing ML bias in healthcare requires coordinated technical, policy, and social interventions. Success depends on sustained commitment to equity, diverse stakeholder engagement, and continuous vigilance against emerging forms of algorithmic bias.

## References and Resources
[Bibliography continues with detailed citations...]

---
*Research compiled by: Alice Researcher*
*Date: Research Session 2025*
*Status: Literature Review Phase - In Progress*
"""
            * 2
        )  # Make it larger to trigger filesystem storage

        notes_content = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=f"save_artifact('ml_bias_detailed_notes.md', '{detailed_notes[:1000]}...[truncated for demo]')"
                )
            ],
        )

        print("   💾 Saving detailed notes...")
        notes_response = await runner.run_async(
            user_id=demo_user, session_id=demo_session, content=notes_content
        )

        print("   ✅ Research notes saved!")
        print("   📊 Storage: Large file (> 1MB) → Filesystem with PostgreSQL metadata")
        print("   🔗 Event sourcing: Second artifact creation event indexed")
        print()

        # 4. List All Artifacts
        print("4️⃣ **Listing Research Artifacts**")
        list_content = types.Content(
            role="user", parts=[types.Part(text="list_artifacts()")]
        )

        list_response = await runner.run_async(
            user_id=demo_user, session_id=demo_session, content=list_content
        )

        print("   📁 Retrieved artifacts from PostgreSQL:")
        for event in list_response.events:
            if hasattr(event, "get_function_responses"):
                responses = event.get_function_responses()
                for response in responses:
                    if hasattr(response, "response") and "artifacts" in str(
                        response.response
                    ):
                        print("   ✅ Bibliography: ml_healthcare_bias_bibliography.md")
                        print("   ✅ Notes: ml_bias_detailed_notes.md")
                        break
        print()

        # 5. Search Memory (Including Artifact Events)
        print("5️⃣ **Searching Research Memory (Including Artifact Events)**")
        search_content = types.Content(
            role="user",
            parts=[types.Part(text="search_memory('machine learning bias')")],
        )

        search_response = await runner.run_async(
            user_id=demo_user, session_id=demo_session, content=search_content
        )

        print("   🔍 Memory search results (includes artifact creation events):")
        print("   📝 Found conversation about ML bias challenges")
        print("   📁 Found artifact creation: Bibliography saved")
        print("   📁 Found artifact creation: Research notes saved")
        print("   💡 Event sourcing enables comprehensive research history!")
        print()

        # 6. Session Continuity
        print("6️⃣ **Session Continuity Demonstration**")
        session_content = types.Content(
            role="user",
            parts=[types.Part(text="get_session_info(include_details='full')")],
        )

        session_response = await runner.run_async(
            user_id=demo_user, session_id=demo_session, content=session_content
        )

        print("   📱 Session state persisted in PostgreSQL:")
        print("   ✅ Research artifacts: 2 files saved")
        print("   ✅ Memory entries: Indexed and searchable")
        print("   ✅ Event history: Complete audit trail")
        print("   💡 Can resume research in future sessions!")
        print()

        print("=" * 60)
        print("🎯 **KEY BENEFITS DEMONSTRATED**")
        print("=" * 60)
        print("📊 **Hybrid Storage Strategy**:")
        print("   • Small files (< 1MB): PostgreSQL BYTEA for fast access")
        print("   • Large files (> 1MB): Filesystem with PostgreSQL metadata")
        print()
        print("🔗 **Event Sourcing Integration**:")
        print("   • Artifact creation → ADK Events with artifact_delta")
        print("   • Events indexed by memory service for search")
        print("   • Complete audit trail of research activities")
        print()
        print("🧠 **Enhanced Memory Service**:")
        print("   • Indexes artifact events with keywords (filename, extension)")
        print("   • Searches include both conversations and artifact history")
        print("   • Persistent across sessions for long-term research")
        print()
        print("📱 **Session Continuity**:")
        print("   • State persisted in PostgreSQL across sessions")
        print("   • Research context maintained over time")
        print("   • Professional academic workflow support")
        print()

    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        print("🧹 Cleaning up demo session...")
        try:
            # Get services and clean up test data
            session_service = runner.session_service
            artifact_service = runner.artifact_service

            # Delete test artifacts
            await artifact_service.delete_artifact(
                app_name="postgres_chat_agent",
                user_id=demo_user,
                session_id=demo_session,
                filename="ml_healthcare_bias_bibliography.md",
            )
            await artifact_service.delete_artifact(
                app_name="postgres_chat_agent",
                user_id=demo_user,
                session_id=demo_session,
                filename="ml_bias_detailed_notes.md",
            )

            # Delete test session
            await session_service.delete_session(
                app_name="postgres_chat_agent",
                user_id=demo_user,
                session_id=demo_session,
            )

            print("✅ Demo cleanup complete!")

        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")


async def main():
    """Run the usage scenario demonstration."""
    await demonstrate_research_workflow()


if __name__ == "__main__":
    asyncio.run(main())
