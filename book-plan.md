# ADK Textbook Plan

A multi-chapter demo-driven textbook for Google's Agent Development Kit (ADK) in the academic research domain, exploring evaluation-driven agent development.

## Book Overview

**Theme**: Evaluation-driven agent development in academic research
**Structure**: Progressive complexity from configuration-only to production systems
**Domain Focus**: Academic research tools and workflows

## Current Status: Advanced Production Systems ✅

The textbook has evolved beyond the initial plan to include **complete production-ready implementations**:

- **6 Complete Chapters** covering fundamentals through production PostgreSQL runtimes
- **Custom ADK Runtime** with full PostgreSQL persistence and event sourcing
- **Production UI Systems** including FastAPI servers and custom Textual interfaces  
- **Advanced State Management** demonstrating both simple and EventActions.state_delta patterns
- **Enterprise Patterns** ready for real-world deployment

The textbook now provides a complete learning path from basic ADK concepts to building sophisticated, scalable agent systems that can be deployed in production environments.

## Chapter Structure

### Chapter 1: Agents Without Code ✅
- **Status**: Complete
- **Approach**: Configuration-only agents using YAML
- **Key Concepts**: 
  - ADK fundamentals
  - Google search tool integration
  - CLI and web interfaces
  - Anti-cheating detection example
- **Files**: `textbook-adk-ch01/`

### Chapter 2: Python Agents with Custom Tools ✅  
- **Status**: Complete
- **Approach**: Python-based agents with custom tool functions
- **Key Concepts**:
  - `LlmAgent` class and programmatic configuration
  - Custom tool development patterns
  - Mock data implementation
  - Multi-database search strategies
  - Professional project structure
- **Demo**: Paper finder agent with academic database search
- **Files**: `textbook-adk-ch02/paperfinder/`

### Chapter 3: Artifacts and State Management ✅
- **Status**: Complete
- **Approach**: Agent artifact management and persistence
- **Key Concepts**:
  - Artifact creation, storage, and retrieval
  - State persistence across sessions
  - File management and binary data handling
- **Files**: `textbook-adk-ch03-artifacts/`

### Chapter 6: ADK Runtime Fundamentals ✅
- **Status**: Complete
- **Approach**: Understanding ADK runtime architecture and building contract-compliant systems
- **Key Concepts**:
  - ADK UI Contract implementation with FastAPI
  - State management patterns (simple updates vs EventActions.state_delta)
  - Agent state visibility and external state mutation
  - Server-sent events and real-time streaming
  - Event sourcing fundamentals
- **Demo**: Complete FastAPI server with state-aware research agents
- **Files**: `textbook-adk-ch06-runtime/`

### Chapter 7: Custom PostgreSQL Runtime Implementation ✅
- **Status**: Complete
- **Approach**: Building production systems with custom database backends
- **Key Concepts**:
  - PostgreSQL-backed SessionService, MemoryService, and ArtifactService
  - Database schema design and migration management
  - Event sourcing with complete audit trails
  - Hybrid storage strategies (BYTEA + filesystem)
  - Production deployment patterns and web UI plugins
- **Demo**: Complete PostgreSQL-backed agent with persistent memory and slash commands
- **Files**: `textbook-adk-ch07-runtime/`

### Chapter 8: UI Frameworks and Custom Interfaces ✅
- **Status**: Complete  
- **Approach**: Building custom user interfaces for agent systems
- **Key Concepts**:
  - Textual-based chat interfaces
  - Artifact tracking and visualization
  - Modal dialogs and interactive components
  - Event handling and real-time updates
- **Demo**: Complete Textual chat interface with artifact management
- **Files**: `textbook-adk-ch08-ui/`

## Technical Notes

### ADK Evaluation System
⚠️ **Important**: The `adk eval` command is currently **EXPERIMENTAL** and has significant limitations:

- **Local evaluation service**: Incomplete and requires additional configuration
- **Tool trajectory matching**: Extremely strict, often fails on minor parameter differences
- **Google Cloud dependency**: Appears designed primarily for cloud-based evaluation
- **Limited documentation**: Configuration options not well documented
- **Workaround**: Focus on `response_match_score` metrics only, avoid `tool_trajectory_avg_score`

### Evaluation Configuration
Current working pattern for test configs:
```json
{
    "criteria": {
        "response_match_score": 0.1
    }
}
```

Avoid `tool_trajectory_avg_score` due to overly strict matching requirements.

## Learning Progression

The textbook follows a carefully designed progression from fundamental concepts to production systems:

1. **Chapters 1-2**: Foundation (Config-based agents → Python agents with tools)
2. **Chapter 3**: Persistence (Artifacts and state management)  
3. **Chapter 6**: Runtime Architecture (ADK internals and contract compliance)
4. **Chapter 7**: Production Systems (Custom PostgreSQL runtime)
5. **Chapter 8**: User Interfaces (Custom UI frameworks)

## Future Chapters (Planned)

### Chapter 4: Advanced Tool Integration
- Real API integrations (replacing mock data)
- Model Context Protocol (MCP) implementation using Asta's Scientific Corpus Tool
- Error handling, retry logic, and rate limiting
- Tool chaining and composition patterns
- Enterprise-grade tool integration patterns

### Chapter 5: Multi-Agent Systems  
- Agent composition and coordination
- Workflow orchestration patterns
- Inter-agent communication
- Complex research task automation
- Distributed agent architectures

### Chapter 9: Advanced Evaluation Strategies
- Custom evaluation metrics beyond response matching
- A/B testing frameworks for agent performance
- Benchmarking and quality assurance patterns
- Production monitoring and observability

### Chapter 10: Capstone Project - Academic Research Ecosystem
**Project Overview**: Integrate all concepts to build a comprehensive scientific research system using ADK, inspired by Allen AI's Asta.

- **Multi-Agent Research System**: Literature review, data analysis, citation network analysis agents
- **Production Integration**: Real MCP-based Semantic Scholar access, multi-database orchestration
- **Advanced Evaluation**: Custom metrics for scientific research quality and productivity
- **Enterprise Deployment**: Web interface, API endpoints, collaborative features, institutional auth

**Learning Outcomes**: Students build a production-ready scientific research assistant showcasing every major ADK concept, creating a portfolio piece demonstrating mastery from basic tools to enterprise systems.

## Development Patterns

### Mock Data Strategy
- All Chapter 2 tools use mock data for immediate functionality
- Realistic data structures that mirror real APIs
- Easy transition path to production APIs
- Predictable responses for testing and evaluation

### Evaluation-Driven Development
- Each chapter includes comprehensive test suites
- Multiple evaluation scenarios per agent
- Focus on response quality over strict tool matching
- Incremental complexity in test cases

### Professional Structure
```
textbook-adk-ch0X/
├── agent_name/
│   ├── __init__.py
│   ├── agent.py
│   ├── *.test.json
│   └── test_config.json
├── chapterXX.md
└── README.md
```

## Known Issues

1. **ADK Evaluation Limitations**: Local eval service needs significant work
2. **Google AI Function Schemas**: Don't support default parameters in function definitions
3. **Documentation Gaps**: ADK evaluation system lacks comprehensive documentation
4. **Cloud Dependencies**: Many features appear to require Google Cloud setup

## Repository Status

### Completed Chapters
- ✅ **Chapter 1**: Complete with documentation (Config-only agents)
- ✅ **Chapter 2**: Complete with documentation (Python agents with tools)  
- ✅ **Chapter 3**: Complete with documentation (Artifacts and state management)
- ✅ **Chapter 6**: Complete with documentation (ADK Runtime Fundamentals)
- ✅ **Chapter 7**: Complete with documentation (PostgreSQL Runtime Implementation)
- ✅ **Chapter 8**: Complete with documentation (UI Frameworks and Custom Interfaces)

### Infrastructure & Tooling
- ✅ **Core Runtime**: Complete `adk_runtime` package with PostgreSQL services
- ✅ **Development Environment**: Docker Compose, migrations, testing frameworks
- ✅ **Documentation**: Comprehensive READMEs, technical guides, and examples
- ⚠️ **Evaluation System**: Working but experimental (ADK eval limitations remain)

### Planned Development
- 📝 **Chapter 4**: Advanced Tool Integration (MCP, real APIs)
- 📝 **Chapter 5**: Multi-Agent Systems
- 📝 **Chapter 9**: Advanced Evaluation Strategies  
- 📝 **Chapter 10**: Capstone Project (Academic Research Ecosystem)

### Key Achievements
- **Production-Ready Runtime**: Custom PostgreSQL backend with event sourcing
- **Complete UI Contract Implementation**: FastAPI with ADK Web UI compatibility  
- **Advanced State Management**: Both simple tools and EventActions.state_delta patterns
- **Custom User Interfaces**: Textual-based chat with artifact management
- **Comprehensive Documentation**: Learning progression from basics to production systems

## References and Further Reading

### Official ADK Resources
- [Google ADK Documentation](https://cloud.google.com/adk) - Official documentation and API reference
- [ADK GitHub Repository](https://github.com/GoogleCloudPlatform/adk) - Source code and examples

### Agent Pattern Articles
- [Agent Patterns with ADK: 1 Agent, 5 Ways](https://medium.com/google-cloud/agent-patterns-with-adk-1-agent-5-ways-58bff801c2d6) - Medium article exploring different approaches to implementing agents with ADK, covering various architectural patterns and use cases

### Production Scientific Agent Systems
- [Asta: Accelerating science through trustworthy agentic AI](https://allenai.org/blog/asta) - Allen AI's comprehensive blog post detailing Asta, a production-grade scientific research ecosystem consisting of:
  - **Asta Agents**: Domain-specific AI research assistants designed for transparency and reproducibility
  - **AstaBench**: Rigorous benchmarking framework with 2,400+ problems across 11 benchmarks (literature understanding, code execution, data analysis, end-to-end discovery)
  - **Asta Resources**: Open-source toolkit including Scientific Corpus Tool, post-trained language models, and modular research tools
  - Demonstrates enterprise-level agent development with emphasis on augmenting (not replacing) human researchers
  - Provides real-world example of domain-specific agent architecture and comprehensive evaluation frameworks

### Example Repositories
- [ADK Agent Patterns Demo](https://github.com/GoogleCloudPlatform/devrel-demos/tree/main/ai-ml/agent-patterns) - Comprehensive repository demonstrating 5 different ADK agent patterns using a customer support refund system for "Crabby's Taffy" candy company:
  - **Single-Agent with Tools**: Basic agent with tool integration
  - **Multi-Agent (LLM-based orchestration)**: LLM-driven agent coordination
  - **Sequential Agent Workflow**: Non-LLM orchestrated sequential execution
  - **Parallel Agent with Sequential Workflow**: Hybrid parallel/sequential patterns
  - **Custom Agent Control Flow**: Advanced control flow with parallel agents
  - Includes web UI, real-world scenarios (damaged orders, missing shipments), and comprehensive setup instructions
  
  **Note for Textbook Development**: The 5 agent patterns from this repository will be adapted to fit our academic research domain rather than used directly. Customer support workflows will be translated into academic research scenarios (e.g., literature review coordination, multi-database search orchestration, citation analysis workflows) to maintain consistency with our book's focus while demonstrating the same architectural patterns.

### Related Technologies
- [LiteLLM Documentation](https://docs.litellm.ai/) - Multi-provider LLM interface used in Chapter 2
- [Google Cloud Vertex AI](https://cloud.google.com/vertex-ai) - Cloud AI platform integration
- [Anthropic Claude API](https://docs.anthropic.com/) - AI model provider used in examples
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - Protocol for connecting AI assistants to data sources
- [Asta Scientific Corpus Tool (MCP)](https://allenai.org/asta/resources/mcp) - MCP-enabled access to 200M+ academic papers via Semantic Scholar API
  - HTTP endpoint: https://asta-tools.allen.ai/mcp/v1
  - Functions: `get_papers()`, `get_citations()`, `search_papers_by_relevance()`, `search_authors_by_name()`
  - API key management and rate limiting
  - Planned for Chapter 3 to replace mock data with real academic search capabilities

## Target Audience

- Developers learning ADK framework
- Academic researchers building AI tools
- Students studying agent development
- Practitioners interested in evaluation-driven development