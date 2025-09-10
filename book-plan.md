# ADK Textbook Plan

A multi-chapter demo-driven textbook for Google's Agent Development Kit (ADK) in the academic research domain, exploring evaluation-driven agent development.

## Book Overview

**Theme**: Evaluation-driven agent development in academic research
**Structure**: Progressive complexity from configuration-only to advanced Python agents
**Domain Focus**: Academic research tools and workflows

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

## Future Chapters (Planned)

### Chapter 3: Advanced Tool Integration
- Real API integrations (replacing mock data)
- Error handling and retry logic
- Rate limiting and authentication
- Tool chaining and composition patterns
- External service integration
- **MCP Integration**: Model Context Protocol implementation using Asta's Scientific Corpus Tool
  - Programmatic access to 200M+ academic papers via MCP
  - Replace Chapter 2's mock data with real Semantic Scholar API access
  - Demonstrate enterprise-grade tool integration patterns
  - API key management and rate limiting strategies

### Chapter 4: Multi-Agent Systems
- Agent composition and coordination
- Workflow orchestration
- Inter-agent communication patterns
- Complex research task automation
- Distributed agent architectures

### Chapter 5: Production Deployment
- Scaling considerations
- Monitoring and observability  
- Security best practices
- Performance optimization
- Cloud deployment patterns

### Chapter 6: Advanced Evaluation Strategies
- Custom evaluation metrics
- A/B testing frameworks
- Performance benchmarking
- Quality assurance patterns

### Chapter 7: Custom ADK Runtime with PostgreSQL Persistence
- **Custom Runtime Implementation**: Build a production-grade ADK runtime with local PostgreSQL persistence
- **Core Service Development**:
  - PostgreSQL-backed SessionService with JSONB state storage
  - ArtifactService for binary data management  
  - MemoryService with vector support (pgvector) for semantic memory
  - Event sourcing and audit trail implementation
- **ADK Compliance**: 
  - Event-driven asynchronous design patterns
  - State commitment semantics and transaction management
  - Cooperative yield/pause/resume execution cycles
  - Full compatibility with existing ADK agents and tools
- **Database Design**:
  - Schema design for sessions, events, state, and memory
  - JSONB for flexible agent state storage
  - Vector extensions for future semantic memory features
  - Migration and backup strategies
- **Development Tools**:
  - Docker Compose setup for local PostgreSQL
  - Database migration management
  - Debugging and monitoring capabilities
  - Testing with real agent workloads

### Chapter 8: Enterprise Integration  
- Authentication and authorization
- API gateway integration
- Enterprise data source connectivity
- Compliance and governance

### Chapter 9: ADK Runtime Design and Architecture
- **Core Runtime Components**:
  - Session management and state persistence
  - Agent lifecycle and execution models
  - Memory management and conversation history
  - Tool invocation and response handling
- **Runtime Configuration**:
  - Model selection and switching (LiteLLM, Vertex AI, etc.)
  - Environment variable management
  - Service integration patterns
- **Advanced Agent Patterns**:
  - Agent composition and inheritance
  - Dynamic tool loading and registration
  - Context management across interactions
  - Error handling and recovery strategies
- **Performance Considerations**:
  - Caching strategies
  - Async execution patterns
  - Resource management
  - Debugging and introspection tools

### Chapter 10: Capstone Project - Building an ADK-based Asta
**Project Overview**: Integrate all concepts from previous chapters to build a comprehensive scientific research ecosystem using ADK, inspired by Allen AI's Asta but implemented with Google's Agent Development Kit.

- **Multi-Agent Research System**:
  - Literature review coordination agent
  - Data analysis and hypothesis generation agent  
  - Citation network analysis agent
  - Research question refinement agent
- **Comprehensive Tool Integration**:
  - Real MCP-based Semantic Scholar integration (Chapter 3 foundation)
  - Multi-database search orchestration (arXiv, ACM, ACL, institutional repositories)
  - Data visualization and analysis tools
  - Research workflow automation
- **Advanced Evaluation Framework**:
  - Custom evaluation metrics for scientific research tasks
  - Benchmarking against research quality standards
  - Multi-agent coordination assessment
  - User experience and productivity measurements
- **Production Deployment**:
  - Web interface with research workflow management
  - API endpoints for integration with existing research tools
  - Collaborative features for research teams
  - Performance monitoring and optimization
- **Architecture Patterns**:
  - Demonstrates all 5 agent patterns adapted for academic research
  - Enterprise-grade scalability and reliability
  - Transparent, citation-based responses
  - Integration with institutional authentication systems

**Learning Outcomes**: Students will have built a production-ready scientific research assistant that showcases every major ADK concept covered in the textbook, creating a portfolio piece that demonstrates mastery of agent development from basic tools to enterprise systems.

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

- ✅ Chapter 1: Complete with documentation
- ✅ Chapter 2: Complete with documentation  
- ⚠️ Evaluation system: Working but experimental
- 📝 Future chapters: Planning phase

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