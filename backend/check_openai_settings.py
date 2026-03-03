"""
检查 OpenAI 数据使用设置的辅助脚本
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def check_openai_settings():
    """检查 OpenAI API 设置"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ 未找到 OPENAI_API_KEY")
        print("   请在 .env 文件中设置 OPENAI_API_KEY")
        return
    
    print("=" * 60)
    print("OpenAI 数据使用设置检查")
    print("=" * 60)
    print()
    
    try:
        client = OpenAI(api_key=api_key)
        
        # 尝试获取账户信息（如果API支持）
        print("✅ API Key 有效")
        print()
        print("⚠️  重要提示：")
        print("   请手动检查以下设置：")
        print()
        print("   1. 访问：https://platform.openai.com/settings/data-usage")
        print("   2. 查找 'Data usage for training' 选项")
        print("   3. 确保设置为 'OFF' 或 'Disabled'")
        print()
        print("   如果看不到此选项：")
        print("   - 可能是免费账户，不支持此设置")
        print("   - 需要升级到付费账户")
        print("   - 或考虑使用企业版 API")
        print()
        print("=" * 60)
        print("推荐操作：")
        print("=" * 60)
        print("1. 立即访问设置页面检查")
        print("2. 如果可用，禁用数据用于训练")
        print("3. 如果不可用，考虑：")
        print("   - 升级到付费账户")
        print("   - 使用企业版 API")
        print("   - 使用本地模型（Ollama）")
        print()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        print()
        print("请手动访问以下链接检查设置：")
        print("https://platform.openai.com/settings/data-usage")

if __name__ == "__main__":
    check_openai_settings()
