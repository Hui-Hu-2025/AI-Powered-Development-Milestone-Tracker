# 后端配置说明

## 环境变量配置

在 `backend` 目录下创建 `.env` 文件，包含以下配置：

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./child_development.db
CHROMA_DB_PATH=./chroma_db
```

### 配置说明

- **OPENAI_API_KEY**: 你的OpenAI API密钥（必需）
  - 获取方式：访问 https://platform.openai.com/api-keys
  - 如果没有API Key，AI评估功能将无法使用

- **DATABASE_URL**: SQLite数据库路径（可选，默认值已设置）
  - 默认：`sqlite:///./child_development.db`
  - 数据库文件会自动创建

- **CHROMA_DB_PATH**: ChromaDB向量数据库路径（可选，默认值已设置）
  - 默认：`./chroma_db`
  - 用于存储知识库向量（未来功能）

## 文件上传配置

上传的文件会保存在 `backend/uploads/` 目录下，按孩子ID组织：
```
uploads/
  ├── 1/
  │   ├── images/
  │   └── videos/
  └── 2/
      ├── images/
      └── videos/
```

## 数据库初始化

首次运行时会自动创建数据库表结构，无需手动操作。

## 端口配置

默认后端运行在 `http://localhost:8000`

如需修改，编辑 `main.py` 文件末尾的端口设置。
