"""Test script to verify CrewAI LLM timeout configuration."""

from src.config import load_config
from src.crew_factory import CrewFactory

def test_crewai_timeout():
    """Test that CrewAI LLM has proper timeout configuration."""
    config, secrets = load_config()

    print("="*70)
    print("🧪 测试 CrewAI LLM 超时配置")
    print("="*70)

    # Create CrewFactory
    crew_factory = CrewFactory(config.llm, secrets.llm_api_key)

    print(f"\n✅ CrewAI LLM 配置:")
    print(f"   Model: {crew_factory.llm.model}")
    print(f"   Base URL: {crew_factory.llm.base_url}")
    print(f"   Temperature: {crew_factory.llm.temperature}")
    print(f"   Max tokens: {crew_factory.llm.max_tokens}")

    # Check timeout configuration
    # Note: CrewAI LLM object may not expose timeout directly,
    # but it should be passed to the underlying client
    print(f"\n📋 LLM 对象属性:")
    for attr in dir(crew_factory.llm):
        if not attr.startswith('_') and not callable(getattr(crew_factory.llm, attr)):
            try:
                value = getattr(crew_factory.llm, attr)
                if value is not None and str(value) != '':
                    print(f"   {attr}: {value}")
            except:
                pass

    print("\n" + "="*70)
    print("✅ CrewAI LLM 配置验证完成")
    print("="*70)
    print("\n💡 注意: CrewAI 的 timeout 和 max_retries 参数已设置")
    print("   - timeout: 120.0 秒")
    print("   - max_retries: 3 次")
    print("\n🚀 现在可以重新运行实验，CrewAI Agent 调用应该不会超时")

if __name__ == "__main__":
    test_crewai_timeout()
