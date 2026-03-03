"""
修复依赖版本兼容性问题
"""
import subprocess
import sys

def fix_dependencies():
    print("正在更新依赖包以修复兼容性问题...")
    print("-" * 50)
    
    packages = [
        "openai>=1.12.0",
        "httpx>=0.25.0",
    ]
    
    for package in packages:
        print(f"正在安装/更新: {package}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
            print(f"✅ {package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} 安装失败: {e}")
    
    print("-" * 50)
    print("依赖更新完成！")
    print("\n如果问题仍然存在，请尝试：")
    print("  pip install --upgrade openai httpx")

if __name__ == "__main__":
    fix_dependencies()
