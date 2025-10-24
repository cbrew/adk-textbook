#!/usr/bin/env python3
"""
Offline Import Demo - "The Standard Way" Manual Event Creation

This demo shows how external systems can update literature review sessions
using manual event creation that bypasses agent execution but still goes
through the session system for proper state management.

Key scenarios demonstrated:
1. BibTeX file import from reference managers
2. External database synchronization  
3. Collaborative library merging
4. Background job processing

Based on: https://google.github.io/adk-docs/sessions/state/
"""

import asyncio
import tempfile
import uuid
from pathlib import Path
from google.adk.sessions import DatabaseSessionService
from simplified_litreview_agent.tools.offline_import import (
    import_bibtex_batch, 
    sync_external_database
)


async def demo_offline_import_scenarios():
    """
    Demonstrate various offline import scenarios.
    """
    print("🔄 Offline Import Scenarios Demo")
    print("=" * 50)
    print("Shows manual event creation for external system integration")
    print("=" * 50)
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    db_url = f"sqlite:///{temp_db.name}"
    
    session_service = DatabaseSessionService(db_url=db_url)
    
    app_name = "litreview_offline_demo"
    user_id = "researcher_alex"
    session_id = str(uuid.uuid4())
    
    print(f"📀 Database: {temp_db.name}")
    print(f"🆔 Session: {session_id}")
    print()
    
    # Create initial session
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={
            "current_search_query": "machine learning interpretability",
            "pipeline_stage": "collection",
            "papers": {},
            "user:research_interests": ["ML", "interpretability", "XAI"]
        }
    )
    
    # Scenario 1: Mendeley/Zotero BibTeX Export
    print("SCENARIO 1: Reference Manager Import")
    print("-" * 30)
    await scenario1_reference_manager(session_service, app_name, user_id, session_id)
    
    # Scenario 2: Institutional Database Sync
    print("\nSCENARIO 2: Institutional Database Sync")
    print("-" * 30)
    await scenario2_institutional_sync(session_service, app_name, user_id, session_id)
    
    # Scenario 3: arXiv Daily Feed
    print("\nSCENARIO 3: arXiv Daily Feed")
    print("-" * 30)
    await scenario3_arxiv_feed(session_service, app_name, user_id, session_id)
    
    # Scenario 4: Collaborative Library Merge
    print("\nSCENARIO 4: Collaborative Library Merge")
    print("-" * 30)
    await scenario4_collaborative_merge(session_service, app_name, user_id, session_id)
    
    # Show final state persistence
    print("\nFINAL STATE PERSISTENCE")
    print("-" * 30)
    await show_final_persistence(session_service, app_name, user_id, session_id)
    
    # Cleanup
    Path(temp_db.name).unlink()
    print(f"\n🧹 Cleaned up database: {temp_db.name}")
    
    print(f"\n✅ Offline import scenarios completed!")
    print("   Demonstrated 'The Standard Way' for external integrations!")


async def scenario1_reference_manager(session_service, app_name: str, user_id: str, session_id: str):
    """Scenario 1: Import from Mendeley/Zotero BibTeX export."""
    
    print("📚 Simulating Mendeley library export...")
    
    # Large BibTeX export from reference manager
    mendeley_bibtex = '''
    @article{ribeiro2016should,
        title={"Why Should I Trust You?" Explaining the Predictions of Any Classifier},
        author={Ribeiro, Marco Tulio and Singh, Sameer and Guestrin, Carlos},
        journal={Proceedings of the 22nd ACM SIGKDD},
        year={2016},
        abstract={Understanding why machine learning models make certain predictions is crucial for trust and debugging. We propose LIME, a technique that explains predictions of any classifier.}
    }
    
    @inproceedings{lundberg2017unified,
        title={A Unified Approach to Interpreting Model Predictions},
        author={Lundberg, Scott M and Lee, Su-In},
        booktitle={Advances in Neural Information Processing Systems},
        year={2017},
        abstract={We present SHAP values, a unified framework for interpreting predictions that connects game theory with local explanations.}
    }
    
    @article{molnar2020interpretable,
        title={Interpretable Machine Learning},
        author={Molnar, Christoph},
        journal={Lean Publishing},
        year={2020},
        abstract={A comprehensive guide to making black-box machine learning models explainable and interpretable.}
    }
    
    @inproceedings{adebayo2018sanity,
        title={Sanity Checks for Saliency Maps},
        author={Adebayo, Julius and Gilmer, Justin and Muelly, Michael and Goodfellow, Ian and Hardt, Moritz and Kim, Been},
        booktitle={Advances in Neural Information Processing Systems},
        year={2018},
        abstract={We propose sanity checks for attribution methods used in neural network interpretability research.}
    }
    '''
    
    result = await import_bibtex_batch(
        bibtex_content=mendeley_bibtex,
        session_service=session_service,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        import_tag="mendeley_export"
    )
    
    print(f"   ✅ {result['message']}")
    print(f"   📁 Import tag: {result['import_tag']}")
    print(f"   📊 Papers imported: {result['papers_imported']}")


async def scenario2_institutional_sync(session_service, app_name: str, user_id: str, session_id: str):
    """Scenario 2: Sync with institutional research database."""
    
    print("🏛️ Syncing with institutional database...")
    
    # Simulate institutional database with specific search
    result = await sync_external_database(
        session_service=session_service,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        search_query="explainable AI interpretability",
        max_papers=4
    )
    
    print(f"   ✅ {result['message']}")
    print(f"   🔍 Query: {result['search_query']}")
    print(f"   📊 Papers synced: {result['papers_synced']}")
    
    # Simulate second sync with different query
    print("   🔄 Running follow-up sync...")
    
    result2 = await sync_external_database(
        session_service=session_service,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        search_query="SHAP values feature importance",
        max_papers=2
    )
    
    print(f"   ✅ Follow-up: {result2['papers_synced']} more papers")


async def scenario3_arxiv_feed(session_service, app_name: str, user_id: str, session_id: str):
    """Scenario 3: Daily arXiv feed processing."""
    
    print("📡 Processing arXiv daily feed...")
    
    # Simulate arXiv API results 
    result = await sync_external_database(
        session_service=session_service,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        search_query="interpretable machine learning",
        max_papers=3
    )
    
    print(f"   ✅ {result['message']}")
    print(f"   📈 New papers from arXiv: {result['papers_synced']}")
    print("   ⏰ This would typically run as a daily cron job")


async def scenario4_collaborative_merge(session_service, app_name: str, user_id: str, session_id: str):
    """Scenario 4: Import colleague's library for collaboration."""
    
    print("🤝 Importing collaborator's reference library...")
    
    # Colleague's BibTeX export focusing on related work
    collaborator_bibtex = '''
    @article{chen2022interpretable,
        title={Interpretable Convolutional Neural Networks},
        author={Chen, Zifeng and Bei, Yinda and Rudin, Cynthia},
        journal={Pattern Recognition},
        year={2022},
        abstract={We propose inherently interpretable convolutional neural networks that provide explanations without requiring post-hoc analysis.}
    }
    
    @inproceedings{kim2018interpretability,
        title={Interpretability Beyond Feature Attribution: Quantitative Testing with Concept Activation Vectors},
        author={Kim, Been and Wattenberg, Martin and Gilmer, Justin and Cai, Carrie and Wexler, James and Viegas, Fernanda and Sayres, Rory},
        booktitle={International Conference on Machine Learning},
        year={2018},
        abstract={We introduce Testing with Concept Activation Vectors (TCAV) to provide quantitative interpretability for neural networks.}
    }
    '''
    
    result = await import_bibtex_batch(
        bibtex_content=collaborator_bibtex,
        session_service=session_service,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        import_tag="collaborator_library"
    )
    
    print(f"   ✅ {result['message']}")
    print(f"   👥 Collaboration tag: {result['import_tag']}")
    print(f"   🔬 Research overlap identified for discussion")


async def show_final_persistence(session_service, app_name: str, user_id: str, session_id: str):
    """Show how all imported papers persist in the database."""
    
    print("💾 Checking state persistence across all imports...")
    
    session = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    if not session:
        print("   ❌ Session not found!")
        return
    
    papers = session.state.get("papers", {})
    
    # Count papers by import source
    import_sources = {}
    for paper in papers.values():
        source = paper.get("import_source", "unknown")
        import_sources[source] = import_sources.get(source, 0) + 1
    
    # Count papers by tag
    tags = {}
    for paper in papers.values():
        for tag in paper.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1
    
    print(f"   📊 Total papers: {len(papers)}")
    print(f"   📁 Import sources: {import_sources}")
    print(f"   🏷️  Tags: {tags}")
    print(f"   🔍 Search query: {session.state.get('current_search_query')}")
    print(f"   📈 User imports: {session.state.get('user:papers_imported', 0)}")
    print(f"   🌐 App-level imports: {session.state.get('app:total_imports', 0)}")
    
    print("   ✅ All imports persisted with full metadata!")
    
    # Show sample paper details
    if papers:
        sample_paper = next(iter(papers.values()))
        print(f"\n   📄 Sample paper: '{sample_paper['title'][:50]}...'")
        print(f"      Authors: {sample_paper['authors']}")
        print(f"      Import source: {sample_paper.get('import_source', 'unknown')}")
        print(f"      Tags: {sample_paper.get('tags', [])}")


if __name__ == "__main__":
    print("Offline Import Demo - The Standard Way")
    print("Demonstrates manual event creation for external integrations")  
    print("Based on: https://google.github.io/adk-docs/sessions/state/")
    print()
    
    asyncio.run(demo_offline_import_scenarios())