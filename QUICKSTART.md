# 快速启动指南

## 前置要求

- Python 3.8+
- Node.js 16+
- OpenAI API Key

## 快速开始

### 1. 配置后端

```bash
cd backend
pip install -r requirements.txt
```

创建 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 OpenAI API Key：
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 2. 启动后端

```bash
# Windows
python main.py
# 或
start.bat

# Linux/Mac
python main.py
# 或
chmod +x start.sh
./start.sh
```

后端将在 http://localhost:8000 运行

### 3. 配置前端

```bash
cd frontend
npm install
```

### 4. 启动前端

```bash
npm start
```

前端将在 http://localhost:3000 运行

## 使用流程

1. **创建孩子档案**
   - 在首页点击"新建档案"
   - 填写孩子的基本信息和特殊情况
   - 提交创建

2. **添加发育记录**
   - 选择要记录的孩子
   - 点击"新建记录"
   - 填写各项发育指标（身高、体重、大运动、语言等）
   - 可选择上传图片或视频
   - 提交后系统会自动使用AI评估

3. **查看评估结果**
   - 记录提交后，系统会自动显示AI评估结果
   - 评估状态：正常发育 / 良性发育 / 倒退

4. **查看里程碑预测**
   - 选择孩子后，自动显示预测的发育里程碑
   - 包括预计时间和达成建议

## 常见问题

### 后端启动失败

- 检查是否安装了所有依赖：`pip install -r requirements.txt`
- 检查 `.env` 文件中的 OpenAI API Key 是否正确
- 确保端口 8000 未被占用

### 前端无法连接后端

- 确保后端正在运行
- 检查 `src/App.js` 中的 `API_BASE_URL` 是否正确
- 检查浏览器控制台是否有CORS错误

### AI评估失败

- 检查 OpenAI API Key 是否有效
- 检查网络连接
- 查看后端日志了解详细错误信息

## 下一步

- 查看 `README.md` 了解详细功能
- 根据需要自定义AI提示词（在 `backend/llm_service.py` 中）
- 添加更多功能或优化界面
