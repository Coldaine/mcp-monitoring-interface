"""
Quick test script to verify all components are working
"""
import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import gradio as gr
        print("[OK] Gradio imported successfully")

        import pandas as pd
        print("[OK] Pandas imported successfully")

        import plotly.graph_objects as go
        print("[OK] Plotly imported successfully")

        import config
        print("[OK] Config imported successfully")

        from utils import LogManager, generate_sample_logs
        print("[OK] Utils imported successfully")

        from mcp_integration import mcp_integration
        print("[OK] MCP Integration imported successfully")

        print("\n[OK] All imports successful!")
        return True
    except ImportError as e:
        print(f"\n[ERROR] Import error: {e}")
        return False


def test_log_manager():
    """Test LogManager functionality"""
    print("\nTesting LogManager...")
    try:
        from utils import LogManager, generate_sample_logs

        log_manager = LogManager()

        # Generate and add sample logs
        for log in generate_sample_logs():
            log_manager.add_log(log)

        # Test retrieval
        logs_df = log_manager.get_logs(limit=10)
        print(f"[OK] Added {len(logs_df)} sample logs")

        # Test metrics
        metrics = log_manager.get_metrics()
        print(f"[OK] Metrics calculated: {metrics}")

        return True
    except Exception as e:
        print(f"[ERROR] LogManager test failed: {e}")
        return False


def test_mcp_integration():
    """Test MCP Integration"""
    print("\nTesting MCP Integration...")
    try:
        from mcp_integration import mcp_integration

        # Test metrics retrieval
        metrics = mcp_integration.get_monitoring_metrics()
        print(f"[OK] MCP metrics: {metrics}")

        # Test logs retrieval
        logs = mcp_integration.get_session_logs(limit=5)
        print(f"[OK] Retrieved {len(logs)} logs")

        return True
    except Exception as e:
        print(f"[ERROR] MCP Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration"""
    print("\nTesting Configuration...")
    try:
        import config

        print(f"[OK] Gradio port: {config.GRADIO_SERVER_PORT}")
        print(f"[OK] MCP server URL: {config.MCP_SERVER_URL}")
        print(f"[OK] Max log entries: {config.MAX_LOG_ENTRIES}")

        return True
    except Exception as e:
        print(f"[ERROR] Config test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("MCP Monitoring Interface - Component Tests")
    print("=" * 60)

    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_config),
        ("LogManager Tests", test_log_manager),
        ("MCP Integration Tests", test_mcp_integration),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{'=' * 60}")
        result = test_func()
        results.append((name, result))

    print(f"\n{'=' * 60}")
    print("Test Summary")
    print("=" * 60)

    for name, result in results:
        status = "[PASSED]" if result else "[FAILED]"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n[SUCCESS] All tests passed! Ready to launch the application.")
        print("\nTo start the Gradio interface, run:")
        print("  python gradio_app.py")
        print("\nTo start the Slack bot (optional), run:")
        print("  python slack_bot.py")
        return 0
    else:
        print("\n[FAILED] Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
