# Copyright 2025 Medbrook Systems
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

"""Unit tests for paper finding configuration."""

import pytest
from paper_finding.config import Config, AgentModel


def test_agent_model_defaults():
    """Test AgentModel default values."""
    model = AgentModel()

    assert model.name == "paper_finding_agent"
    assert model.model == "gemini-2.5-flash"


def test_config_defaults():
    """Test Config default values."""
    config = Config()

    assert config.app_name == "paper_finding_app"
    assert config.CLOUD_PROJECT == "my_project"
    assert config.CLOUD_LOCATION == "us-central1"
    assert config.GENAI_USE_VERTEXAI == "1"
    assert config.agent_settings.name == "paper_finding_agent"


def test_custom_agent_model():
    """Test custom AgentModel configuration."""
    custom_model = AgentModel(name="custom_paper_agent", model="gemini-2.5-pro")

    assert custom_model.name == "custom_paper_agent"
    assert custom_model.model == "gemini-2.5-pro"
