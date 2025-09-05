#!/usr/bin/env python3
"""
Run PostgreSQL agent examples.

This script provides an easy way to run the various PostgreSQL integration examples.

Usage:
    # Run automated demo
    uv run python textbook-adk-ch07-runtime/examples/run_examples.py

    # Run interactive demo  
    uv run python textbook-adk-ch07-runtime/examples/run_examples.py --interactive

    # Test agent tools
    uv run python textbook-adk-ch07-runtime/examples/run_examples.py --test-tools

    # Check services status
    uv run python textbook-adk-ch07-runtime/examples/run_examples.py --check

Prerequisites:
    # Make sure PostgreSQL services are running:
    cd textbook-adk-ch07-runtime && make dev-setup
"""

import argparse
import asyncio
import sys

from basic_agent import run_automated_example, run_interactive_demo
from test_services import main as test_services_main

from adk_runtime.runtime.adk_runtime import PostgreSQLADKRuntime


async def check_services():
    """Check if PostgreSQL services are available."""
    print("🔍 Checking PostgreSQL services...")

    try:
        runtime = await PostgreSQLADKRuntime.create_and_initialize()

        print("✅ PostgreSQL runtime: OK")
        print("✅ Session service: OK")
        print("✅ Memory service: OK")
        print("✅ Artifact service: OK")
        print("\n🎉 All services are ready!")

        await runtime.shutdown()
        return True

    except Exception as e:
        print(f"❌ Service check failed: {e}")
        print("\n💡 To fix this, run:")
        print("   cd textbook-adk-ch07-runtime && make dev-setup")
        return False


async def test_agent_tools():
    """Test the agent tools integration."""
    print("🧪 Testing PostgreSQL agent tools integration...")

    from persistent_chat_agent.agent import PersistentChatTools

    tools = PersistentChatTools("tool_test_agent")

    try:
        print("\n1. Initializing tools...")
        await tools.initialize()
        print("   ✅ Tools initialized")

        print("\n2. Testing save_to_memory...")
        result = await tools.save_to_memory()
        print(f"   {result}")

        print("\n3. Testing search_memory...")
        result = await tools.search_memory("test conversation")
        print(f"   {result}")

        print("\n4. Testing save_artifact...")
        result = await tools.save_artifact(
            "tool_test.txt",
            "This artifact was created during tool testing.\n\nContents:\n- Tool integration test\n- PostgreSQL persistence\n- ADK compatibility"
        )
        print(f"   {result}")

        print("\n✅ Agent tools test completed successfully!")

    except Exception as e:
        print(f"❌ Agent tools test failed: {e}")
        return False

    finally:
        await tools.cleanup()

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run PostgreSQL agent examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run automated demo
  %(prog)s --interactive      # Run interactive chat demo  
  %(prog)s --test-tools       # Test agent tools
  %(prog)s --check            # Check service status
  %(prog)s --test-services    # Run full service test suite
        """
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--interactive', action='store_true',
                      help='Run interactive chat demo')
    group.add_argument('--test-tools', action='store_true',
                      help='Test agent tools integration')
    group.add_argument('--check', action='store_true',
                      help='Check PostgreSQL services status')
    group.add_argument('--test-services', action='store_true',
                      help='Run full service test suite')

    args = parser.parse_args()

    print("🐘 PostgreSQL Agent Examples")
    print("=" * 40)

    if args.check:
        asyncio.run(check_services())

    elif args.test_services:
        print("🧪 Running full service test suite...")
        test_services_main()

    elif args.test_tools:
        success = asyncio.run(test_agent_tools())
        if not success:
            sys.exit(1)

    elif args.interactive:
        print("🚀 Starting interactive demo...")
        print("💡 Make sure services are running: make dev-setup")
        asyncio.run(run_interactive_demo())

    else:
        print("🤖 Running automated example...")
        print("💡 Make sure services are running: make dev-setup")
        asyncio.run(run_automated_example())


if __name__ == "__main__":
    main()
