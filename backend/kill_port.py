"""
Windows: 杀死占用指定端口的进程
"""
import subprocess
import sys

def kill_port(port=8000):
    """杀死占用指定端口的进程"""
    try:
        # 查找占用端口的进程
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        # 查找占用端口的进程ID
        lines = result.stdout.split('\n')
        pids = []
        
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.append(pid)
        
        if not pids:
            print(f"✅ 端口 {port} 未被占用")
            return True
        
        # 杀死进程
        print(f"找到 {len(pids)} 个占用端口 {port} 的进程:")
        for pid in set(pids):
            print(f"  - PID: {pid}")
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], 
                             capture_output=True, shell=True)
                print(f"  ✅ 已终止进程 {pid}")
            except Exception as e:
                print(f"  ❌ 无法终止进程 {pid}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n手动方法:")
        print(f"1. 打开任务管理器")
        print(f"2. 查找占用端口 {port} 的进程")
        print(f"3. 或运行: netstat -ano | findstr :{port}")
        print(f"4. 然后运行: taskkill /F /PID <进程ID>")
        return False

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print("使用默认端口 8000")
    
    print(f"正在检查端口 {port}...")
    kill_port(port)
