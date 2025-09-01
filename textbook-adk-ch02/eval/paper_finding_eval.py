# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Evaluation module for the paper finding agent."""

import os
import pytest
from paper_finding.config import Config
from dotenv import find_dotenv, load_dotenv
from google.adk.evaluation.agent_evaluator import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables for testing."""
    load_dotenv(find_dotenv(".env"))
    c = Config()


@pytest.mark.asyncio
async def test_eval_basic_search():
    """Test the agent's basic paper search functionality."""
    await AgentEvaluator.evaluate(
        "paper_finding",
        os.path.join(os.path.dirname(__file__), "eval_data/basic_search.test.json"),
        num_runs=1,
    )


@pytest.mark.asyncio
async def test_eval_reading_list_management():
    """Test the agent's reading list management capabilities."""
    await AgentEvaluator.evaluate(
        "paper_finding", 
        os.path.join(os.path.dirname(__file__), "eval_data/reading_list.test.json"),
        num_runs=1,
    )


@pytest.mark.asyncio
async def test_eval_paper_recommendations():
    """Test the agent's paper recommendation functionality."""
    await AgentEvaluator.evaluate(
        "paper_finding",
        os.path.join(os.path.dirname(__file__), "eval_data/recommendations.test.json"),
        num_runs=1,
    )