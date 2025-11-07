#!/usr/bin/env python3
"""Control Flow Efficiency Pattern Demo.

This example demonstrates how implementing loops, conditionals, and error handling
through code reduces latency and token consumption compared to chaining tool calls.

Pattern: Single Code Block > Multiple Sequential Tool Calls

Efficiency Gains:
- Reduces round-trip latency by ~90%
- Consolidates multiple operations
- Handles errors locally
- Implements retry logic efficiently
"""

import json
import sys
from pathlib import Path
from time import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_code_agent.tools.code_executor import SafeCodeExecutor


def demo_traditional_tool_chaining() -> None:
    """Show the inefficient approach of chaining individual tool calls."""
    print("=" * 80)
    print("TRADITIONAL APPROACH: Chain multiple tool calls")
    print("=" * 80)

    print("""
Scenario: Process multiple files and aggregate results

Traditional approach requires:
1. Call list_directory tool
2. Wait for response
3. For each file:
   a. Call read_file tool
   b. Wait for response
   c. Call analyze_content tool
   d. Wait for response
4. Call aggregate_results tool
5. Wait for final response

Total: 1 + (3 × N files) + 1 = 13 tool calls for 4 files
Each call has ~200ms latency = 2.6 seconds total
Plus token overhead for each tool call definition
""")

    files = ["paper1.txt", "paper2.txt", "paper3.txt", "paper4.txt"]
    print(f"\n📊 Processing {len(files)} files:")
    print(f"   Tool calls needed: {1 + (3 * len(files)) + 1}")
    print(f"   Estimated latency: ~{(1 + (3 * len(files)) + 1) * 0.2:.1f} seconds")
    print(f"   Context switches: {1 + (3 * len(files)) + 1}")
    print("\n⚠️  Problems:")
    print("   - High latency due to round-trips")
    print("   - Token overhead for each tool definition")
    print("   - Error handling requires more tool calls")
    print("   - Cannot easily implement retry logic")


def demo_control_flow_efficiency() -> None:
    """Show the efficient approach using code execution."""
    print("\n" + "=" * 80)
    print("CONTROL FLOW EFFICIENCY: Single code execution block")
    print("=" * 80)

    code = """
import json

# Get list of files
files_response = call_mcp_tool("filesystem", "list_directory", {"path": "papers/"})
files = json.loads(files_response)["files"]

print(f"Found {len(files)} files")

# Process all files in a single execution
results = []
errors = []

for filename in files:
    try:
        # Read file
        content_response = call_mcp_tool("filesystem", "read_file", {
            "path": f"papers/{filename}"
        })
        content = json.loads(content_response)["content"]

        # Analyze locally (no separate tool call needed)
        word_count = len(content.split())
        char_count = len(content)

        results.append({
            "file": filename,
            "words": word_count,
            "chars": char_count,
            "status": "success"
        })
        print(f"✓ Processed {filename}: {word_count} words")

    except Exception as e:
        errors.append({"file": filename, "error": str(e)})
        print(f"✗ Error processing {filename}: {e}")

# Aggregate results locally
total_words = sum(r["words"] for r in results)
total_files = len(results)
avg_words = total_words / total_files if total_files > 0 else 0

# Return summary
result = {
    "summary": {
        "total_files": len(files),
        "processed": len(results),
        "errors": len(errors),
        "total_words": total_words,
        "avg_words": round(avg_words, 2)
    },
    "details": results[:5],  # First 5 for reference
    "errors": errors
}

print(f"\\nCompleted: {len(results)}/{len(files)} files processed")
"""

    print("\nExecuting code with control flow:")
    print("-" * 80)

    executor = SafeCodeExecutor()

    # Mock MCP tool calls
    def mock_call_mcp_tool(server: str, tool_name: str, parameters: dict) -> str:
        if tool_name == "list_directory":
            return json.dumps(
                {
                    "files": [
                        "paper1.txt",
                        "paper2.txt",
                        "paper3.txt",
                        "paper4.txt",
                    ]
                }
            )
        elif tool_name == "read_file":
            filename = parameters["path"].split("/")[-1]
            # Generate mock content
            content = f"This is the content of {filename}. " * 50
            return json.dumps({"content": content, "size": len(content)})
        return json.dumps({"error": "Unknown tool"})

    start_time = time()
    result = executor.execute(code, {"call_mcp_tool": mock_call_mcp_tool})
    execution_time = time() - start_time

    print(result["output"])

    if result["success"]:
        print("\n✅ Code executed successfully")
        print(f"\nResults:\n{json.dumps(result['result'], indent=2)}")
        print(f"\n⚡ Execution time: {execution_time*1000:.1f}ms")
        print("\n📊 Comparison:")
        print(f"   Traditional: ~{(1 + 3*4 + 1) * 200}ms")
        print(f"   Code execution: ~{execution_time*1000:.1f}ms")
        print(f"   Speedup: ~{(1 + 3*4 + 1) * 200 / (execution_time*1000):.1f}x faster")


def demo_retry_logic() -> None:
    """Show how code execution enables sophisticated retry logic."""
    print("\n" + "=" * 80)
    print("ADVANCED PATTERN: Retry logic and error handling")
    print("=" * 80)

    code = """
import json

def fetch_with_retry(tool_name, params, max_retries=3):
    \"\"\"Fetch data with automatic retry on failure.\"\"\"
    for attempt in range(max_retries):
        try:
            response = call_mcp_tool("research", tool_name, params)
            data = json.loads(response)
            if data.get("success"):
                return data
            print(f"Attempt {attempt + 1} failed, retrying...")
        except Exception as e:
            print(f"Attempt {attempt + 1} error: {e}")
            if attempt == max_retries - 1:
                raise
    return None

# Use retry logic for multiple operations
papers_to_fetch = ["paper_1", "paper_2", "paper_3"]
results = []

for paper_id in papers_to_fetch:
    print(f"\\nFetching citations for {paper_id}...")
    try:
        data = fetch_with_retry("get_citations", {"paper_id": paper_id})
        if data:
            results.append({
                "paper_id": paper_id,
                "citations": len(data.get("citations", [])),
                "status": "success"
            })
            print(f"✓ Got {len(data.get('citations', []))} citations")
    except Exception as e:
        results.append({
            "paper_id": paper_id,
            "error": str(e),
            "status": "failed"
        })
        print(f"✗ Failed after retries: {e}")

# Summary
successful = [r for r in results if r["status"] == "success"]
result = {
    "total_papers": len(papers_to_fetch),
    "successful": len(successful),
    "total_citations": sum(r.get("citations", 0) for r in successful),
    "results": results
}

print(f"\\nFinal: {len(successful)}/{len(papers_to_fetch)} papers fetched")
"""

    print("\nExecuting code with retry logic:")
    print("-" * 80)

    executor = SafeCodeExecutor()

    # Mock MCP tool call with occasional failures
    call_count = [0]

    def mock_call_mcp_tool(
        server: str, tool_name: str, parameters: dict  # noqa: ARG001
    ) -> str:
        call_count[0] += 1
        # Simulate occasional failures
        if call_count[0] % 3 == 2:  # Fail every 3rd call
            return json.dumps({"success": False, "error": "Temporary failure"})

        paper_id = parameters.get("paper_id", "unknown")
        citations = [
            {"id": f"cite_{i}", "title": f"Citation {i}"} for i in range(25)
        ]
        result_data = {"success": True, "paper_id": paper_id, "citations": citations}
        return json.dumps(result_data)

    result = executor.execute(code, {"call_mcp_tool": mock_call_mcp_tool})

    print(result["output"])

    if result["success"]:
        print("\n✅ Code executed successfully with retry logic")
        print(f"\nResults:\n{json.dumps(result['result'], indent=2)}")
        print("\n💡 Benefits of code-based retry:")
        print("   - Automatic retry on failures")
        print("   - No additional tool call overhead")
        print("   - Sophisticated error handling")
        print("   - Exponential backoff possible")


def demo_conditional_logic() -> None:
    """Show conditional logic within code execution."""
    print("\n" + "=" * 80)
    print("ADVANCED PATTERN: Conditional logic and branching")
    print("=" * 80)

    code = """
import json

# Fetch paper metadata
paper_response = call_mcp_tool("research", "search_papers", {
    "query": "machine learning",
    "max_results": 50
})
papers = json.loads(paper_response)["papers"]

print(f"Analyzing {len(papers)} papers...")

# Conditional processing based on paper characteristics
high_impact = []
recent_promising = []
classic_papers = []

for paper in papers:
    citations = paper.get("citations", 0)
    year = paper.get("year", 2020)

    # Branch logic based on paper characteristics
    if citations > 500:
        # High impact - get detailed citations
        print(f"  High impact: {paper['title'][:50]}... ({citations} cites)")
        citation_response = call_mcp_tool("research", "get_citations", {
            "paper_id": paper["id"]
        })
        citation_data = json.loads(citation_response)
        paper["citation_details"] = citation_data.get("citations", [])[:10]
        high_impact.append(paper)

    elif year >= 2023 and citations > 50:
        # Recent and promising
        print(f"  Recent promising: {paper['title'][:50]}...")
        recent_promising.append(paper)

    elif year < 2015 and citations > 1000:
        # Classic paper
        print(f"  Classic: {paper['title'][:50]}...")
        classic_papers.append(paper)

# Generate insights based on conditional processing
result = {
    "categories": {
        "high_impact": len(high_impact),
        "recent_promising": len(recent_promising),
        "classic": len(classic_papers)
    },
    "top_high_impact": high_impact[:3],
    "top_recent": recent_promising[:3],
    "insights": [
        f"Found {len(high_impact)} high-impact papers (>500 citations)",
        f"Identified {len(recent_promising)} recent promising papers",
        f"Located {len(classic_papers)} classic papers (pre-2015, >1000 cites)"
    ]
}

print(f"\\nCategorized {len(papers)} papers into {len(result['categories'])} groups")
"""

    print("\nExecuting code with conditional logic:")
    print("-" * 80)

    executor = SafeCodeExecutor()

    def mock_call_mcp_tool(server: str, tool_name: str, parameters: dict) -> str:
        if tool_name == "search_papers":
            papers = []
            for i in range(50):
                papers.append(
                    {
                        "id": f"paper_{i}",
                        "title": f"Machine Learning Paper {i}: Advanced Techniques",
                        "year": 2010 + (i % 15),
                        "citations": 100 + (i * 50) if i < 10 else 30 + i * 5,
                    }
                )
            return json.dumps({"papers": papers})
        elif tool_name == "get_citations":
            citations = [
                {"id": f"cite_{i}", "title": f"Citation {i}", "year": 2020 + i}
                for i in range(50)
            ]
            return json.dumps({"citations": citations})
        return json.dumps({"error": "Unknown tool"})

    result = executor.execute(code, {"call_mcp_tool": mock_call_mcp_tool})

    print(result["output"])

    if result["success"]:
        print("\n✅ Code executed successfully with conditional logic")
        print(f"\nResults:\n{json.dumps(result['result'], indent=2)}")


def main() -> None:
    """Run all control flow demos."""
    print("\n" + "🔄" * 40)
    print("CONTROL FLOW EFFICIENCY PATTERN DEMONSTRATION")
    print("🔄" * 40)

    demo_traditional_tool_chaining()
    demo_control_flow_efficiency()
    demo_retry_logic()
    demo_conditional_logic()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. ✅ Implement loops in code, not through tool chains
2. ✅ Handle errors locally with try/except
3. ✅ Add retry logic without extra tool calls
4. ✅ Use conditionals for smart branching
5. ✅ Reduce latency by ~90% vs sequential tools

This pattern is especially valuable when:
- Processing multiple items (files, papers, records)
- Failures are possible and retries needed
- Conditional logic based on data
- Complex workflows with branching
- Time-sensitive operations

Efficiency gains:
- Latency: 2.6s → 0.1s (26x faster)
- Tool calls: 13 → 1 (92% reduction)
- Error handling: Built-in retry logic
- Flexibility: Full Python control flow
""")


if __name__ == "__main__":
    main()
