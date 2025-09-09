"""
Event and artifact handling logic for the chat interface.
"""

import time
from typing import TYPE_CHECKING

from textual.widgets import DataTable, Static

if TYPE_CHECKING:
    from .main import ChatInterface


class EventHandler:
    """Handles event storage and table updates."""
    
    def __init__(self, chat_interface: "ChatInterface"):
        self.chat_interface = chat_interface
    
    def setup_events_table(self) -> None:
        """Setup the events table with columns."""
        table = self.chat_interface.query_one("#events-table", DataTable)
        table.add_columns("Time", "Type", "Author", "Text", "Function Calls", "Error")
    
    def store_event_record(self, extracted: dict) -> None:
        """Store an event record and update the events table."""
        # Create a simplified record for the table
        record = {
            "time": time.strftime("%H:%M:%S"),
            "type": extracted.get("type", ""),
            "author": extracted.get("author", "") or "",
            "text": (
                (extracted.get("text", "") or "")[:50] +
                ("..." if len(extracted.get("text", "") or "") > 50 else "")
            ),
            "function_calls": (
                str(len(extracted.get("function_calls", []) or []))
                if extracted.get("function_calls") else ""
            ),
            "error": extracted.get("error", "") or ""
        }

        # Store full record
        self.chat_interface.event_records.append(extracted)

        # Add to table if events tab is active or table exists
        try:
            table = self.chat_interface.query_one("#events-table", DataTable)
            table.add_row(
                record["time"],
                record["type"],
                record["author"],
                record["text"],
                record["function_calls"],
                record["error"]
            )
        except Exception:
            pass  # Table might not be ready yet


class ArtifactHandler:
    """Handles artifact management and table updates."""
    
    def __init__(self, chat_interface: "ChatInterface"):
        self.chat_interface = chat_interface
    
    def setup_artifacts_table(self) -> None:
        """Setup the artifacts table with columns."""
        try:
            table = self.chat_interface.query_one("#artifacts-table", DataTable)
            table.add_columns("Time", "Filename", "Version", "Size (bytes)", "Status")
            # Make sure the table is selectable and shows cursor
            table.cursor_type = "row"
            table.show_cursor = True
        except Exception:
            pass  # Table might not be ready yet
    
    def handle_artifact_update(self, extracted: dict) -> None:
        """Handle artifact creation/update events (original method)."""
        artifact_delta = extracted.get("artifact_delta", {})
        if not artifact_delta:
            return

        # Create artifact record
        artifact_record = {
            "time": time.strftime("%H:%M:%S"),
            "filename": "Unknown",
            "version": "Unknown",
            "size_bytes": "Unknown",
            "status": "Created",
            "delta": artifact_delta
        }

        # Try to extract filename/version from the delta or function calls
        function_calls = extracted.get("function_calls", [])
        if function_calls:
            for call in function_calls:
                if isinstance(call, dict) and call.get("name") == "save_text_artifact":
                    args = call.get("args", {})
                    if "filename" in args:
                        artifact_record["filename"] = args["filename"]
                    if "text" in args:
                        artifact_record["size_bytes"] = str(
                            len(args["text"].encode("utf-8"))
                        )

        # Try to get version from artifact delta keys
        if isinstance(artifact_delta, dict):
            for key, value in artifact_delta.items():
                if "version" in key.lower():
                    artifact_record["version"] = str(value)
                elif "filename" in key.lower():
                    artifact_record["filename"] = str(value)
                elif "size" in key.lower():
                    artifact_record["size_bytes"] = str(value)

        # Store the record
        self.chat_interface.artifact_records.append(artifact_record)

        # Add to artifacts table
        try:
            table = self.chat_interface.query_one("#artifacts-table", DataTable)
            table.add_row(
                artifact_record["time"],
                artifact_record["filename"],
                artifact_record["version"],
                artifact_record["size_bytes"],
                artifact_record["status"]
            )

            # Also show a system message about the artifact
            self.chat_interface.add_system_message(
                f"📁 Artifact created: {artifact_record['filename']}"
            )

        except Exception:
            pass  # Table might not be ready yet

    def handle_enhanced_artifact_update(self, enhanced_info: dict) -> None:
        """Handle artifact updates using enhanced artifact consumer information."""
        # Check for artifact-related events
        artifact_delta = enhanced_info.get("artifact_delta", {})
        function_calls = enhanced_info.get("function_calls", [])
        function_responses = enhanced_info.get("function_responses", [])
        all_artifacts = enhanced_info.get("all_artifacts", {})

        # Create records for newly created or updated artifacts
        if artifact_delta or function_responses:
            artifact_record = {
                "time": time.strftime("%H:%M:%S"),
                "filename": "Unknown",
                "version": "Unknown",
                "size_bytes": "Unknown",
                "status": "Created"
            }

            # Extract artifact details from function calls (creation)
            if function_calls:
                for call in function_calls:
                    if isinstance(call, dict) and "artifact_info" in call:
                        artifact_info = call["artifact_info"]
                        filename = artifact_info.get("filename", "Unknown")
                        content = artifact_info.get("content", "")
                        artifact_record["filename"] = filename
                        artifact_record["size_bytes"] = str(
                            artifact_info.get("content_length", 0)
                        )
                        artifact_record["status"] = "Creating"

                        # Cache the artifact content for viewing
                        if filename != "Unknown" and content:
                            self.chat_interface.artifact_content_cache[filename] = content

            # Extract artifact details from function responses (completion)
            if function_responses:
                for resp in function_responses:
                    is_save_artifact = (
                        isinstance(resp, dict) and
                        resp.get("name") == "save_text_artifact"
                    )
                    if is_save_artifact:
                        response_data = resp.get("response", {})
                        if isinstance(response_data, dict):
                            artifact_record["filename"] = response_data.get(
                                "filename", "Unknown"
                            )
                            artifact_record["version"] = str(
                                response_data.get("version", 0)
                            )
                            artifact_record["status"] = response_data.get(
                                "status", "Created"
                            )

            # Extract from artifact delta
            if artifact_delta:
                for filename, version in artifact_delta.items():
                    if artifact_record["filename"] == "Unknown":
                        artifact_record["filename"] = filename
                    if artifact_record["version"] == "Unknown":
                        artifact_record["version"] = str(version)

            # Use information from all_artifacts if available
            if all_artifacts and artifact_record["filename"] != "Unknown":
                artifact_info = all_artifacts.get(artifact_record["filename"])
                if artifact_info:
                    artifact_record["version"] = str(
                        artifact_info.get("version", "Unknown")
                    )
                    if artifact_record["size_bytes"] == "Unknown":
                        content_preview = artifact_info.get("content_preview", "")
                        # Estimate size if we have preview
                        if content_preview and content_preview.endswith("..."):
                            artifact_record["size_bytes"] = "100+"  # Approximate
                        else:
                            artifact_record["size_bytes"] = str(
                                len(content_preview.encode("utf-8"))
                            )

            # Only store and display if we have meaningful data
            if artifact_record["filename"] != "Unknown":
                self.chat_interface.artifact_records.append(artifact_record)

                # Add to artifacts table
                try:
                    table = self.chat_interface.query_one("#artifacts-table", DataTable)
                    table.add_row(
                        artifact_record["time"],
                        artifact_record["filename"],
                        artifact_record["version"],
                        artifact_record["size_bytes"],
                        artifact_record["status"]
                    )
                except Exception:
                    pass  # Table might not be ready yet

    def get_artifact_content(self, filename: str, artifact_record: dict) -> str:
        """Get artifact content from cache or enhanced consumer."""
        # Check cache first - if we have the actual content
        if filename in self.chat_interface.artifact_content_cache:
            cached_content = self.chat_interface.artifact_content_cache[filename]
            # If it looks like actual content (not just metadata), display it
            if not cached_content.startswith("**Artifact Information:**"):
                return f"""**Content:**

{cached_content}

---
**Metadata:**
- Status: {artifact_record.get('status', 'Unknown')}
- Version: {artifact_record.get('version', 'Unknown')}
- Size: {artifact_record.get('size_bytes', 'Unknown')} bytes
- Created: {artifact_record.get('time', 'Unknown')}"""
            else:
                return cached_content

        # Try to get content from enhanced consumer
        if self.chat_interface.artifact_consumer:
            summary = self.chat_interface.artifact_consumer.get_conversation_summary()
            if filename in summary.get("artifacts", {}):
                # Show artifact metadata since we don't have direct content access
                artifact_info = summary["artifacts"][filename]
                content = f"""**Artifact Information:**
- Filename: {artifact_info.get('filename', 'Unknown')}
- Version: {artifact_info.get('version', 'Unknown')}
- Content Length: {artifact_info.get('content_length', 'Unknown')} characters
- Created In: {artifact_info.get('created_in', 'Unknown')[:16]}...

**Status:**
This artifact was created during the conversation.
The actual content is stored in the ADK artifact system.

**Record Details:**
- Status: {artifact_record.get('status', 'Unknown')}
- Size: {artifact_record.get('size_bytes', 'Unknown')} bytes
- Time Created: {artifact_record.get('time', 'Unknown')}

💡 Tip: Artifacts are stored persistently and can be retrieved via ADK."""
                self.chat_interface.artifact_content_cache[filename] = content
                return content

        # Fallback to basic info
        return f"""**{filename}**

Status: {artifact_record.get('status', 'Unknown')}
Version: {artifact_record.get('version', 'Unknown')}
Size: {artifact_record.get('size_bytes', 'Unknown')} bytes
Created: {artifact_record.get('time', 'Unknown')}

Select different artifacts to view their details."""