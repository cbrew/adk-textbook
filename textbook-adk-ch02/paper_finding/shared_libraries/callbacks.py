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

"""Callback functions for the paper finding agent."""

import logging
import asyncio
from typing import Any

logger = logging.getLogger(__name__)


async def rate_limit_callback() -> None:
    """Simple rate limiting callback to prevent API overuse."""
    await asyncio.sleep(0.1)  # 100ms delay between calls


async def before_agent(context: Any) -> None:
    """Callback executed before agent processing."""
    logger.info("Starting paper finding agent session")


async def before_tool(tool_name: str, tool_input: dict) -> None:
    """Callback executed before tool execution."""
    logger.info("Executing tool: %s with input: %s", tool_name, tool_input)


async def after_tool(tool_name: str, tool_output: Any) -> None:
    """Callback executed after tool execution."""
    logger.info("Tool %s completed successfully", tool_name)