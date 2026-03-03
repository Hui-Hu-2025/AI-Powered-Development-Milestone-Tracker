"""
辅助脚本：创建 .env 文件
"""
import os

def create_env_file():
    env_path = ".env"
    
    if os.path.exists(env_path):
        print(f"⚠️  {env_path} 文件已存在")
        response = input("是否要覆盖现有文件？(y/n): ")
        if response.lower() != 'y':
            print("已取消操作")
            return
    
    print("\n=== 创建 .env 配置文件 ===\n")
    
    api_key = input("请输入你的 OpenAI API Key (留空跳过): ").strip()
    
    if not api_key:
        api_key = "your_openai_api_key_here"
        print("⚠️  未输入 API Key，请稍后手动编辑 .env 文件")
    
    content = f"""# OpenAI API 配置
# 获取API Key: https://platform.openai.com/api-keys
OPENAI_API_KEY={api_key}

# 数据库配置（可选，使用默认值即可）
DATABASE_URL=sqlite:///./child_development.db

# ChromaDB 向量数据库路径（可选，使用默认值即可）
CHROMA_DB_PATH=./chroma_db
"""
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\n✅ {env_path} 文件已创建！")
    if api_key == "your_openai_api_key_here":
        print("⚠️  请记得编辑 .env 文件，填入你的 OpenAI API Key")

if __name__ == "__main__":
    create_env_file()
