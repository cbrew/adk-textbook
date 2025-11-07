#!/usr/bin/env python3
"""Data Filtering Pattern Demo.

This example demonstrates the dramatic token savings achieved by processing
large datasets locally before returning results to the model.

Pattern: Fetch → Filter Locally → Return Summary

Token Savings: Up to 98.7% for large datasets (150,000 → 2,000 tokens)
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_code_agent.tools.code_executor import SafeCodeExecutor


def demo_traditional_approach() -> None:
    """Show the inefficient traditional approach (returns all data)."""
    print("=" * 80)
    print("TRADITIONAL APPROACH: Return all data to model")
    print("=" * 80)

    # Simulate fetching a large dataset
    dataset = []
    for i in range(10000):
        dataset.append(
            {
                "id": i,
                "status": "active" if i % 3 == 0 else "inactive",
                "value": i * 10,
                "category": f"cat_{i % 5}",
                "metadata": {
                    "created": "2024-01-01",
                    "updated": "2024-11-06",
                    "tags": ["research", "data", "analysis"],
                },
            }
        )

    # Convert to JSON (what would be sent to model)
    json_str = json.dumps(dataset, indent=2)
    char_count = len(json_str)
    token_estimate = char_count // 4

    print("\n📊 Dataset Statistics:")
    print(f"   Total records: {len(dataset)}")
    print(f"   JSON characters: {char_count:,}")
    print(f"   Estimated tokens: ~{token_estimate:,}")
    print("\n⚠️  Problem: ALL data sent to model!")
    print("   - Wastes context window")
    print("   - Increases latency")
    print("   - Costs more in API usage")

    # Show a sample
    print(f"\n📄 Sample records (first 3 of {len(dataset)}):")
    print(json.dumps(dataset[:3], indent=2))


def demo_data_filtering() -> None:
    """Show the efficient data filtering approach."""
    print("\n" + "=" * 80)
    print("DATA FILTERING: Process locally, return summary")
    print("=" * 80)

    # Simulate the same dataset
    dataset = []
    for i in range(10000):
        dataset.append(
            {
                "id": i,
                "status": "active" if i % 3 == 0 else "inactive",
                "value": i * 10,
                "category": f"cat_{i % 5}",
            }
        )

    print(f"\n1️⃣  FETCH: Get full dataset ({len(dataset)} records)")

    # Process locally
    print("\n2️⃣  FILTER: Process data locally")
    active_records = [r for r in dataset if r["status"] == "active"]
    high_value = [r for r in active_records if r["value"] > 50000]

    # Aggregate
    print("\n3️⃣  AGGREGATE: Generate summary statistics")
    category_counts = {}
    for record in active_records:
        cat = record["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Create summary (this is what gets sent to model)
    summary = {
        "total_records": len(dataset),
        "active_records": len(active_records),
        "high_value_records": len(high_value),
        "category_distribution": category_counts,
        "sample_high_value": high_value[:5],  # Just a few examples
        "statistics": {
            "avg_value": sum(r["value"] for r in active_records)
            / len(active_records),
            "max_value": max(r["value"] for r in active_records),
            "min_value": min(r["value"] for r in active_records),
        },
    }

    # Calculate tokens
    summary_json = json.dumps(summary, indent=2)
    summary_chars = len(summary_json)
    summary_tokens = summary_chars // 4

    print("\n4️⃣  RETURN: Send compact summary to model")
    print(f"   Summary characters: {summary_chars:,}")
    print(f"   Estimated tokens: ~{summary_tokens:,}")
    print(f"\n   Summary:\n{summary_json}")

    # Compare
    full_tokens = len(json.dumps(dataset)) // 4
    reduction = ((full_tokens - summary_tokens) / full_tokens) * 100

    print("\n5️⃣  TOKEN SAVINGS:")
    print(f"   Full dataset: ~{full_tokens:,} tokens")
    print(f"   Summary: ~{summary_tokens:,} tokens")
    print(f"   Reduction: {reduction:.1f}%")


def demo_code_execution_filtering() -> None:
    """Show data filtering within code execution."""
    print("\n" + "=" * 80)
    print("CODE EXECUTION: Data filtering in action")
    print("=" * 80)

    code = """
import json

# Fetch large dataset from MCP server
print("Fetching dataset from MCP server...")
response = call_mcp_tool("data_processing", "get_records", {"limit": 10000})
data = json.loads(response)
records = data["records"]

print(f"Received {len(records)} records")

# FILTER locally (don't return all data!)
print("\\nFiltering data locally...")
active = [r for r in records if r["status"] == "active"]
high_value = [r for r in active if r["value"] > 50000]

# AGGREGATE locally
print("Aggregating data...")
category_stats = {}
for record in active:
    cat = record["category"]
    if cat not in category_stats:
        category_stats[cat] = {"count": 0, "total_value": 0}
    category_stats[cat]["count"] += 1
    category_stats[cat]["total_value"] += record["value"]

# Create compact summary to return to model
result = {
    "summary": {
        "total": len(records),
        "active": len(active),
        "high_value": len(high_value),
        "categories": category_stats
    },
    "sample": high_value[:3],  # Just a few examples
    "insights": [
        f"{len(active)}/{len(records)} records are active "
        f"({len(active)/len(records)*100:.1f}%)",
        f"{len(high_value)} high-value records found",
        f"Most common category: "
        f"{max(category_stats.items(), key=lambda x: x[1]['count'])[0]}"
    ]
}

print(f"\\nReturning compact summary ({len(json.dumps(result))} characters)")
"""

    print("\nExecuting code with data filtering:")
    print("-" * 80)

    executor = SafeCodeExecutor()

    # Mock MCP tool call
    def mock_call_mcp_tool(
        server: str, tool_name: str, parameters: dict  # noqa: ARG001
    ) -> str:
        # Generate mock dataset
        records = []
        for i in range(10000):
            records.append(
                {
                    "id": i,
                    "status": "active" if i % 3 == 0 else "inactive",
                    "value": i * 10,
                    "category": f"cat_{i % 5}",
                }
            )
        return json.dumps({"success": True, "records": records})

    result = executor.execute(
        code,
        {"call_mcp_tool": mock_call_mcp_tool},
    )

    print(result["output"])

    if result["success"]:
        print("\n✅ Code executed successfully")
        print(f"\nFinal result:\n{json.dumps(result['result'], indent=2)}")

        # Calculate actual savings
        full_data = [{"id": i, "status": "active"} for i in range(10000)]
        full_size = len(json.dumps(full_data))
        summary_size = len(json.dumps(result["result"]))
        savings = ((full_size - summary_size) / full_size) * 100

        print(f"\n💰 Actual Token Savings: {savings:.1f}%")
    else:
        print(f"\n❌ Error: {result['error']}")


def demo_real_world_scenario() -> None:
    """Demonstrate a real-world academic research scenario."""
    print("\n" + "=" * 80)
    print("REAL-WORLD SCENARIO: Academic paper analysis")
    print("=" * 80)

    code = """
import json

# Fetch papers from academic database (simulate 1000 papers)
print("Fetching papers from research database...")
response = call_mcp_tool("research", "search_papers", {
    "query": "machine learning",
    "max_results": 1000
})
papers = json.loads(response)["papers"]

print(f"Retrieved {len(papers)} papers")

# Local analysis - find highly cited recent papers
print("\\nAnalyzing papers locally...")
current_year = 2024
recent_papers = [p for p in papers if p["year"] >= current_year - 5]
highly_cited = [p for p in recent_papers if p.get("citations", 0) > 100]

# Sort by citations
highly_cited.sort(key=lambda x: x["citations"], reverse=True)

# Create summary for model
result = {
    "analysis": {
        "total_papers": len(papers),
        "recent_papers": len(recent_papers),
        "highly_cited": len(highly_cited),
        "date_range": f"{current_year - 5}-{current_year}"
    },
    "top_papers": highly_cited[:10],  # Top 10 only
    "recommendations": [
        f"Found {len(highly_cited)} highly-cited recent papers",
        f"Top paper has {highly_cited[0]['citations']} citations",
        "Consider reviewing papers from 2020-2024 with 100+ citations"
    ]
}

print(f"\\nReturning top 10 papers from {len(papers)} total")
"""

    print("\nExecuting academic research scenario:")
    print("-" * 80)

    executor = SafeCodeExecutor()

    def mock_call_mcp_tool(
        server: str, tool_name: str, parameters: dict  # noqa: ARG001
    ) -> str:
        papers = []
        for i in range(1000):
            papers.append(
                {
                    "id": f"paper_{i}",
                    "title": f"Machine Learning Research Paper {i}",
                    "year": 2020 + (i % 5),
                    "citations": 50 + (i * 2) if i < 100 else 30 + i // 10,
                }
            )
        return json.dumps({"success": True, "papers": papers})

    result = executor.execute(
        code,
        {"call_mcp_tool": mock_call_mcp_tool},
    )

    print(result["output"])

    if result["success"]:
        print("\n✅ Analysis complete")
        print(f"\nResults:\n{json.dumps(result['result'], indent=2)}")


def main() -> None:
    """Run all data filtering demos."""
    print("\n" + "📊" * 40)
    print("DATA FILTERING PATTERN DEMONSTRATION")
    print("📊" * 40)

    demo_traditional_approach()
    demo_data_filtering()
    demo_code_execution_filtering()
    demo_real_world_scenario()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. ✅ Fetch full dataset from MCP server
2. ✅ Filter, transform, and aggregate LOCALLY
3. ✅ Return only summary/insights to model
4. ✅ Keep raw data in execution environment
5. ✅ Save up to 98.7% tokens (150,000 → 2,000)

This pattern is especially valuable when:
- Working with large datasets (1,000+ records)
- Model only needs summary/insights
- Multiple data sources need combining
- Statistical analysis is required
- Privacy is a concern (keep PII local)

Real-world applications:
- Academic paper analysis (1000s of papers → top 10)
- Log file analysis (millions of lines → error summary)
- Database queries (large tables → aggregated results)
- API responses (full data → relevant subset)
""")


if __name__ == "__main__":
    main()
