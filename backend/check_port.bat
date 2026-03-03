@echo off
echo 检查端口 8000 占用情况...
netstat -ano | findstr :8000
echo.
echo 如果看到进程，请记录 PID，然后运行:
echo taskkill /F /PID <PID>
echo.
echo 或直接运行: python kill_port.py
