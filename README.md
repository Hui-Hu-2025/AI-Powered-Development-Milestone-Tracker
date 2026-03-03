# 儿童发育里程碑追踪工具

一个基于AI的儿童发育监测系统，专门用于追踪有特殊情况孩子的发育里程碑。

## 功能特性

1. **孩子档案管理** - 创建和管理孩子的特殊情况信息
2. **发育记录追踪** - 记录身高、体重、头围、大运动、语言、精细动作、睡眠、饮食等
3. **AI智能评估** - 使用OpenAI GPT-4自动评估孩子的发育状态（正常发育/良性发育/倒退）
4. **里程碑预测** - 预测孩子下一个可能达到的发育里程碑及时间节点
5. **多媒体支持** - 支持图片、视频、文字等多种输入格式

## 技术架构

```
React 前端
    |
    v
FastAPI 后端
    |
    v
SQLite 数据库 (结构化数据)
ChromaDB (向量数据库)
    |
    v
OpenAI GPT-4 (LLM)
```

## 项目结构

```
.
├── backend/          # FastAPI 后端
│   ├── main.py      # API 主文件
│   ├── models.py    # 数据库模型
│   ├── database.py  # 数据库配置
│   ├── llm_service.py  # LLM 服务
│   ├── services.py  # 业务逻辑服务
│   └── requirements.txt
├── frontend/        # React 前端
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
└── README.md
```

## 安装和运行

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key
```

5. 运行后端：
```bash
python main.py
# 或使用 uvicorn
uvicorn main:app --reload --port 8000
```

后端将在 `http://localhost:8000` 运行

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 运行前端：
```bash
npm start
```

前端将在 `http://localhost:3000` 运行

## API 端点

### 孩子管理
- `POST /api/children` - 创建孩子档案
- `GET /api/children` - 获取所有孩子列表
- `GET /api/children/{child_id}` - 获取单个孩子信息

### 发育记录
- `POST /api/records` - 创建发育记录（支持文件上传）
- `GET /api/children/{child_id}/records` - 获取孩子的所有记录

### 里程碑预测
- `GET /api/children/{child_id}/milestones` - 预测下一个发育里程碑

## 使用说明

1. **创建孩子档案**
   - 点击"新建档案"按钮
   - 填写孩子的基本信息和特殊情况
   - 提交创建

2. **添加发育记录**
   - 选择要记录的孩子
   - 点击"新建记录"
   - 填写各项发育指标
   - 可选择上传图片或视频
   - 提交后系统会自动使用AI评估发育状态

3. **查看里程碑预测**
   - 选择孩子后，系统会自动显示预测的发育里程碑
   - 里程碑包括预计时间和达成建议

## 环境变量

在 `backend/.env` 文件中配置：

```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./child_development.db
CHROMA_DB_PATH=./chroma_db
```

## 注意事项

1. 需要有效的 OpenAI API Key 才能使用AI评估功能
2. 上传的图片和视频会保存在 `backend/uploads/` 目录下
3. 数据库文件会自动创建在项目根目录
4. 首次运行会自动初始化数据库表结构

## 开发计划

- [ ] 添加用户认证系统
- [ ] 支持更多文件格式
- [ ] 添加数据可视化图表
- [ ] 导出报告功能
- [ ] 多语言支持
- [ ] 移动端适配

## 许可证

MIT License
