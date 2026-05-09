"""Simple test script to verify LLM API connectivity."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import load_config
from src.llm_client import LLMClient, LLMClientFactory


def test_llm_connection():
    """Test LLM connection with a simple hello message."""
    print("=" * 60)
    print("LLM Connection Test")
    print("=" * 60)
    
    # Load configuration
    print("\n[1/3] Loading configuration...")
    config, secrets = load_config()
    print(f"  ✓ Provider: {config.llm.provider}")
    print(f"  ✓ Base URL: {config.llm.base_url}")
    print(f"  ✓ Model: {config.llm.default_model}")
    print(f"  ✓ Temperature: {config.llm.temperature}")
    print(f"  ✓ Max tokens: {config.llm.max_tokens}")
    
    # Create LLM client
    print("\n[2/3] Creating LLM client...")
    client = LLMClientFactory.create_generation_client(config.llm, secrets)
    print("  ✓ Client created successfully")
    
    # Test with hello message
    print("\n[3/3] Sending test message...")
    messages = [
        {"role": "user", "content": "hello"}
    ]
    
    try:
        result = client.chat_completion(messages=messages)
        print(f"  ✓ Response received!")
        print(f"\n  Model: {result.model}")
        print(f"  Latency: {result.latency_ms:.2f} ms")
        print(f"  Tokens: {result.total_tokens} (input: {result.input_tokens}, output: {result.output_tokens})")
        print(f"\n  Response content:")
        print(f"  {'-' * 56}")
        print(f"  {result.content}")
        print(f"  {'-' * 56}")
        print("\n✅ Test PASSED - LLM connection working correctly!")
        return True
    except Exception as e:
        print(f"\n❌ Test FAILED - LLM connection error:")
        print(f"   {e}")
        return False


if __name__ == "__main__":
    success = test_llm_connection()
    sys.exit(0 if success else 1)
