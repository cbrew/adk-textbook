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

"""Callback functions for the paper finding agent."""

import logging
import asyncio
from typing import Any
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


async def rate_limit_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> None:
    """Simple rate limiting callback to prevent API overuse."""
    await asyncio.sleep(0.1)  # 100ms delay between calls


async def before_agent(callback_context: CallbackContext) -> None:
    """Callback executed before agent processing."""
    logger.info("Starting paper finding agent session")


async def before_tool(tool: BaseTool,
                      args: dict[str, Any], tool_context: ToolContext) -> None:
    """Callback executed before tool execution."""
    logger.info("Executing tool: %s with input: %s", tool.name, args)


async def after_tool(tool: BaseTool, args: dict,
                     tool_context: ToolContext,
                     tool_response:dict[str, Any]) -> None:
    """Callback executed after tool execution."""
    logger.info("Tool %s completed successfully", tool.name)