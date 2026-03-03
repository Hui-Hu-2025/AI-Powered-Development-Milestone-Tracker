# 启用数据脱敏功能

## 快速启用

### 方法 1：修改 main.py（推荐）

在 `backend/main.py` 中，将：

```python
from llm_service import LLMService
```

改为：

```python
from llm_service_secure import SecureLLMService as LLMService
```

然后修改初始化：

```python
# 启用数据脱敏（推荐）
llm_service = LLMService(anonymize=True)

# 或者禁用脱敏（不推荐，除非你确定数据安全）
# llm_service = LLMService(anonymize=False)
```

### 方法 2：通过环境变量控制

在 `.env` 文件中添加：

```env
ENABLE_DATA_ANONYMIZATION=true
```

然后修改 `main.py` 读取这个配置。

## 数据脱敏功能说明

### 脱敏内容

✅ **已脱敏：**
- 真实姓名 → 代号（如"孩子A1B2"）
- 出生日期 → 只发送年龄（月）
- 备注信息 → 不发送（可能包含个人信息）

✅ **保留（用于评估）：**
- 身体指标（身高、体重、头围）
- 发育指标（大运动、语言、精细动作）
- 特殊情况类型（用于专业评估）

### 脱敏效果示例

**原始数据：**
```
姓名：张三
出生日期：2020-01-15
特殊情况：自闭症谱系障碍
```

**脱敏后：**
```
代号：孩子A1B2
年龄：48个月
特殊情况：自闭症谱系障碍
```

## 注意事项

1. **评估准确性**：脱敏不会影响AI评估的准确性
2. **数据映射**：同一孩子的代号在会话中保持一致
3. **历史记录**：历史记录也会被脱敏处理
4. **完全隐私**：真实姓名和出生日期不会发送到OpenAI

## 验证脱敏是否生效

1. 启动应用
2. 创建一条记录
3. 查看后端日志，检查发送到API的数据
4. 确认姓名已被替换为代号

## 其他安全措施

1. **检查 OpenAI 设置**：
   - 访问 https://platform.openai.com/settings/data-usage
   - 禁用 "Data usage for training"（如果可用）

2. **使用企业版 API**：
   - 企业版保证数据不用于训练
   - 需要付费订阅

3. **本地模型**：
   - 考虑使用本地部署的模型（如 Ollama）
   - 数据完全不离开服务器
