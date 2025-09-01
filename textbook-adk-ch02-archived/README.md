# Academic Paper Finding Agent

This project implements an AI-powered research assistant agent that helps researchers find relevant academic papers, manage reading lists, and discover new research. The agent is designed to streamline the academic research process by providing intelligent paper search, personalized recommendations, and research organization tools.

## Overview

The Academic Paper Finding Agent is designed to assist researchers in discovering, organizing, and managing academic literature. It leverages Gemini to understand research interests, provide tailored paper recommendations, manage reading lists, and analyze citation networks. The agent is designed to be knowledgeable, helpful, and efficient in supporting academic research workflows.

## Agent Details

The key features of the Paper Finding Agent include:

| Feature            | Description             |
| ------------------ | ----------------------- |
| _Interaction Type_ | Conversational          |
| _Complexity_       | Intermediate            |
| _Agent Type_       | Single Agent            |
| _Components_       | Tools, Academic APIs    |
| _Vertical_         | Academic Research       |

### Agent Architecture

The agent is built using a conversational architecture that interacts with academic databases and research management systems. It mocks interactions with various academic services, including arXiv search, citation databases, reading list management, and paper recommendation engines. The agent maintains context across interactions to provide personalized research assistance.

It is important to notice that this agent is not integrated to actual academic APIs and the behavior is based on mocked tools. If you would like to implement this agent with actual backend integration you will need to edit [paper_finding/tools/tools.py](paper_finding/tools/tools.py)

Because the tools are mocked, you might notice that some requested changes will not persist. For instance, papers added to reading lists will not appear in subsequent queries in the same session.

### Key Features

- **Academic Paper Search:**
  - Searches arXiv and other academic databases for relevant research papers.
  - Supports advanced queries with customizable result limits.
  - Maintains a knowledgeable and helpful tone for academic assistance.
- **Research Organization:**
  - Manages personal reading lists with priority levels (high, medium, low).
  - Tracks reading progress and paper metadata.
  - Provides organized access to saved research papers.
- **Personalized Recommendations:**
  - Generates paper recommendations based on research interests.
  - Analyzes relevance scores and provides reasoning for suggestions.
  - Adapts recommendations to user's academic focus areas.
- **Citation Network Analysis:**
  - Explores citation relationships between papers.
  - Identifies influential papers and emerging research trends.
  - Maps research connections and dependencies.
- **Paper Summarization:**
  - Generates concise summaries of paper contributions.
  - Extracts key points and methodological approaches.
  - Identifies main contributions and research significance.
- **Tool-Based Interactions:**
  - The agent interacts with users through a comprehensive set of academic tools.
  - Multiple tools can be used in a single interaction for complex research tasks.
  - Tools provide access to academic databases and research management functions.
- **Evaluation:**
  - The agent can be evaluated using comprehensive test cases.
  - Evaluation focuses on academic accuracy and research assistance capabilities.

#### Agent State - Default user information

The agent's session state includes a default user ID ("user123") for demonstration purposes. In a production environment, this would be replaced with actual user authentication and profile management. User research profiles would include research interests, reading history, and personalized preferences.

#### Tools

The agent has access to the following academic research tools:

- `search_arxiv(query: str, max_results: int = 10) -> Dict`: Searches arXiv for papers matching the query.
- `add_to_reading_list(user_id: str, paper_id: str, priority: str = "medium") -> Dict`: Adds a paper to the user's reading list.
- `get_reading_list(user_id: str) -> Dict`: Retrieves the user's reading list with paper details.
- `get_paper_recommendations(user_id: str, research_interests: List[str]) -> Dict`: Provides personalized paper recommendations.
- `get_citation_network(paper_id: str, depth: int = 1) -> Dict`: Retrieves citation network for analysis.
- `summarize_paper(paper_id: str) -> Dict`: Generates summaries of paper contributions and key findings.

## Setup and Installations

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Google ADK SDK (installed via Poetry)
- Google Cloud Project (for Vertex AI Gemini integration)

### Installation
1.  **Prerequisites:**

    For the Agent Engine deployment steps, you will need
    a Google Cloud Project. Once you have created your project,
    [install the Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
    Then run the following command to authenticate with your project:
    ```bash
    gcloud auth login
    ```
    You also need to enable certain APIs. Run the following command to enable
    the required APIs:
    ```bash
    gcloud services enable aiplatform.googleapis.com
    ```

1.  Navigate to the paper finding agent directory:

    ```bash
    cd textbook-adk-ch02
    ```

    For the rest of this tutorial **ensure you remain in the `textbook-adk-ch02` directory**.

2.  Install dependencies using Poetry:

- if you have not installed poetry before then run `pip install poetry` first. then you can create your virtual environment and install all dependencies using:

  **Note for Linux users:** If you get an error related to `keyring` during the installation, you can disable it by running the following command:
  ```bash
  poetry config keyring.enabled false
  ```
  This is a one-time setup.

  ```bash
  poetry install
  ```

  To activate the virtual environment run:

  ```bash
  poetry env activate
  ```

3.  Set up Google Cloud credentials:

    - Ensure you have a Google Cloud project.
    - Make sure you have the Vertex AI API enabled in your project.
    - Set the `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION` environment variables. You can set them in your `.env` file or directly in your shell. Alternatively you can edit [paper_finding/config.py](paper_finding/config.py)

    ```bash
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_NAME_HERE
    export GOOGLE_GENAI_USE_VERTEXAI=1
    export GOOGLE_CLOUD_LOCATION=us-central1
    ```

## Running the Agent

You can run the agent using the ADK command in your terminal.
from the root project directory:

1.  Run agent in CLI:

    ```bash
    adk run paper_finding
    ```

2.  Run agent with ADK Web UI:
    ```bash
    adk web
    ```
    Select the paper_finding from the dropdown

### Example Interaction

Here's a quick example of how a researcher might interact with the agent:

**User:**:
Hi, I'm looking for recent papers about transformer models in natural language processing.

**Agent**:
I'd be happy to help you find papers about transformer models in NLP! Let me search arXiv for the most relevant recent research.

```tool_code
search_arxiv("transformer models natural language processing", max_results=10)
```

```tool_outputs
{"papers": [{"id": "2101.00001", "title": "Deep Learning for Academic Research: A Survey", "authors": ["Smith, J.", "Doe, A."], "abstract": "A comprehensive survey..."}], "total_results": 2, "query": "transformer models natural language processing"}
```

**User**:
Great! Can you add that first paper to my reading list with high priority?

**Agent**:
Absolutely! I'll add "Deep Learning for Academic Research: A Survey" to your reading list with high priority.

```tool_code
add_to_reading_list("user123", "2101.00001", "high")
```

```tool_outputs
{"status": "success", "message": "Paper 2101.00001 added to reading list with high priority"}
```

**User**:
Can you also recommend some related papers based on my interest in machine learning and NLP?

**Agent**:
Certainly! Let me get some personalized recommendations based on your research interests in machine learning and NLP.

```tool_code
get_paper_recommendations("user123", ["machine learning", "NLP"])
```

## Evaluating the Agent

Evaluation tests assess the overall performance and capabilities of the agent in a holistic manner.

**Steps:**

1.  **Run Evaluation Tests:**

    ```bash
    pytest eval
    ```

    - This command executes all test files within the `eval` directory.

## Unit Tests

Unit tests focus on testing individual units or components of the code in isolation.

**Steps:**

1.  **Run Unit Tests:**

    ```bash
    pytest tests/unit
    ```

    - This command executes all test files within the `tests/unit` directory.

## Configuration

You can find further configuration parameters in [paper_finding/config.py](paper_finding/config.py). This includes parameters such as agent name, app name and LLM model used by the agent.

## Deployment on Google Agent Engine

In order to inherit all dependencies of your agent you can build the wheel file of the agent and run the deployment.

1.  **Build Paper Finding Agent WHL file**

    ```bash
    poetry build --format=wheel --output=deployment
    ```

1.  **Deploy the agent to agents engine**
    It is important to run deploy.py from within deployment folder so paths are correct

    ```bash
    cd deployment
    python deploy.py
    ```

### Testing deployment

This code snippet is an example of how to test the deployed agent.

```python
import vertexai
from paper_finding.config import Config
from vertexai.preview.reasoning_engines import AdkApp

configs = Config()

vertexai.init(
    project="<GOOGLE_CLOUD_PROJECT>",
    location="<GOOGLE_CLOUD_LOCATION>"
)

# get the agent based on resource id
agent_engine = vertexai.agent_engines.get('DEPLOYMENT_RESOURCE_NAME')

for event in remote_agent.stream_query(
    user_id=USER_ID,
    session_id=session["id"],
    message="Find papers about deep learning",
):
    print(event)
```

## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended for production use. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

This sample has not been rigorously tested, may contain bugs or limitations, and does not include features or optimizations typically required for a production environment (e.g., robust error handling, security measures, scalability, performance considerations, comprehensive logging, or advanced configuration options).

Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample. We recommend thorough review, testing, and the implementation of appropriate safeguards before using any derived agent in a live or critical system.