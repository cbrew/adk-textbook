# Chapter 2: Python Agents with Custom Tools

This chapter introduces Python-based ADK agents that use custom tools to extend their capabilities beyond configuration-only approaches. You'll build a fully functional academic paper finder that demonstrates tool creation, mock data handling, and evaluation-driven development.

## Overview

Moving beyond Chapter 1's configuration-only agents, this chapter shows how to:
- Create custom Python tools that agents can use
- Build agents using the `LlmAgent` class with programmatic configuration
- Handle mock data for demonstration and testing
- Implement comprehensive evaluation suites
- Structure production-ready agent codebases

## What You'll Build

**Paper Finder Agent** - An intelligent academic research assistant that helps users:
- Search multiple academic databases (Semantic Scholar, arXiv, ACM, ACL Anthology)
- Access institutional repositories (OSU Digital Collections)
- Get specialized library assistance for hard-to-find materials
- Navigate different types of academic sources based on research needs

## Prerequisites

- Python 3.11+
- uv package manager
- Completion of Chapter 1 (understanding of ADK basics)
- API keys: OpenAI or Anthropic (configured in `.env`)

## Quick Start

From the textbook root:

```bash
# Run the paper finder agent
uv run adk run textbook-adk-ch02/paperfinder

# Launch web interface
uv run adk web textbook-adk-ch02/paperfinder

# Run evaluations
uv run adk eval --config_file_path=textbook-adk-ch02/paperfinder/test_config.json textbook-adk-ch02/paperfinder textbook-adk-ch02/paperfinder/library_assistance.test.json
```

## Key Concepts Introduced

### 1. **Custom Tool Development**

Unlike Chapter 1's pre-built Google search tools, this chapter demonstrates creating custom Python functions that agents can call:

```python
def search_semantic_scholar(query: str, field: str) -> Dict[str, any]:
    """
    Searches Semantic Scholar for academic papers.
    """
    # Custom implementation with mock data
    return {"papers": [...], "metadata": {...}}
```

**Key Learning Points:**
- Tools are regular Python functions with type annotations
- Return dictionaries that agents can interpret and present to users
- Parameter handling without default values (for Google AI compatibility)
- Mock implementations that demonstrate real-world functionality

### 2. **Agent Architecture Evolution**

Chapter 2 agents use the `LlmAgent` class for programmatic configuration:

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

agent = LlmAgent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="paper_finder",
    instruction=agent_instruction,
    tools=[
        search_semantic_scholar,
        search_arxiv,
        search_acm_digital_library,
        # ... more tools
    ]
)
```

This approach provides:
- **Flexibility**: Programmatic control over agent configuration
- **Integration**: Direct tool function integration
- **Maintainability**: Clear separation of concerns

### 3. **Production Code Structure**

The paperfinder demonstrates professional Python project organization:

```
textbook-adk-ch02/paperfinder/
├── __init__.py              # Module exports
├── agent.py                 # Agent configuration and tools
├── *.test.json             # Evaluation test cases
└── test_config.json        # Evaluation criteria
```

## Tool Design Patterns

### Multi-Database Search Strategy

The paper finder implements a tiered search approach:

1. **Semantic Scholar** - Broad academic coverage, citation metrics
2. **arXiv** - Latest preprints, cutting-edge research  
3. **ACM Digital Library** - Computer science focus
4. **ACL Anthology** - Computational linguistics specialization
5. **OSU Digital Collections** - Institutional repository
6. **Library Services** - Human assistance for specialized needs

### Mock Data Implementation

All tools use mock data to demonstrate functionality without requiring API keys:

```python
papers_db = {
    "MACHINE LEARNING": {
        "papers": [
            {
                "title": "Deep Learning for Computer Vision: A Brief Review",
                "authors": ["Li Zhang", "Sarah Chen", "Michael Rodriguez"],
                "abstract": "This paper presents a comprehensive review...",
                "year": 2023,
                "citations": 1247,
                # ... more metadata
            }
        ]
    }
}
```

**Benefits:**
- Immediate functionality without external dependencies
- Predictable responses for testing and evaluation
- Clear demonstration of expected data structures
- Easy transition to real APIs in production

## Evaluation-Driven Development

Chapter 2 introduces comprehensive agent evaluation:

### Test Cases
- **Library Assistance** - Tests recommendation of OSU library services
- **Literature Survey** - Evaluates broad topic search capabilities  
- **Specific Paper Search** - Tests targeted paper finding

### Evaluation Metrics
- **Response Match Score** - Measures output quality against expected responses
- **Tool Trajectory** - Validates correct tool usage patterns (optional, strict)

### Configuration
```json
{
    "criteria": {
        "response_match_score": 0.1
    }
}
```

## Learning Objectives

By completing this chapter, you'll understand:

- **Custom Tool Creation**: How to build Python functions that extend agent capabilities
- **Agent Programming**: Using `LlmAgent` for flexible, code-based agent configuration
- **Mock Data Patterns**: Implementing realistic demonstrations without external APIs
- **Professional Structure**: Organizing production-ready agent codebases
- **Evaluation Systems**: Building comprehensive test suites for agent behavior
- **Academic Domain Modeling**: Structuring tools around real-world research workflows

## Transition from Chapter 1

| Chapter 1 (Config-Only) | Chapter 2 (Python + Tools) |
|-------------------------|----------------------------|
| YAML configuration | Python `LlmAgent` class |
| Built-in Google tools | Custom Python functions |
| Simple conversations | Complex multi-tool workflows |
| Basic testing | Comprehensive evaluation suites |
| Immediate deployment | Development-focused structure |

## Next Steps

After mastering Chapter 2, you'll be ready to:
- Integrate real APIs instead of mock data
- Build more sophisticated tool chains
- Implement advanced evaluation strategies
- Deploy agents in production environments

The paper finder serves as both a learning tool and a template for building domain-specific agents that combine multiple information sources to solve complex user problems.