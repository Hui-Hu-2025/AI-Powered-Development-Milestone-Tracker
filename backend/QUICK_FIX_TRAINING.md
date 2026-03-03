# 🚀 快速操作：防止数据被用于训练

## 立即操作（5分钟）

### 步骤 1：检查 OpenAI 设置（最重要）

1. **打开浏览器，访问：**
   ```
   https://platform.openai.com/settings/data-usage
   ```

2. **查找 "Data usage for training" 选项**

3. **如果看到此选项：**
   - ✅ 设置为 **OFF** 或 **Disabled**
   - ✅ 保存设置
   - ✅ 完成！数据不会被用于训练

4. **如果看不到此选项：**
   - ⚠️ 可能是免费账户，不支持此设置
   - ⚠️ 需要升级到付费账户
   - 继续看下面的其他方案

### 步骤 2：运行检查脚本（可选）

```bash
cd backend
python check_openai_settings.py
```

## 如果设置页面没有选项怎么办？

### 方案 A：升级到付费账户（推荐）

1. 访问：https://platform.openai.com/account/billing
2. 添加付款方式
3. 升级后，设置选项应该会出现

### 方案 B：使用企业版 API（最可靠）

- 联系 OpenAI 销售：https://openai.com/enterprise
- 企业版保证数据不用于训练（合同保证）

### 方案 C：使用本地模型（完全不上传）

**使用 Ollama（推荐）：**

1. **安装 Ollama**
   ```bash
   # Windows: 下载安装
   # https://ollama.ai/download
   
   # 或使用 winget
   winget install Ollama.Ollama
   ```

2. **启动 Ollama**
   ```bash
   ollama serve
   ```

3. **下载模型**
   ```bash
   ollama pull llama2
   # 或
   ollama pull mistral
   ```

4. **修改代码使用本地模型**
   
   在 `backend/main.py` 中，将：
   ```python
   from llm_service_secure import SecureLLMService as LLMService
   ```
   
   改为：
   ```python
   from llm_service_local import LocalLLMService as LLMService
   ```
   
   然后修改初始化：
   ```python
   llm_service = LLMService()  # 使用本地模型
   ```

5. **配置环境变量（可选）**
   
   在 `.env` 文件中添加：
   ```env
   LOCAL_LLM_MODEL=llama2
   LOCAL_LLM_URL=http://localhost:11434
   ```

## 当前保护措施

✅ **已启用：**
- 数据脱敏（真实姓名、出生日期已匿名化）
- 敏感信息过滤（备注不发送）

⚠️ **还需要：**
- 在 OpenAI 设置中禁用数据用于训练
- 或使用企业版/本地模型

## 推荐方案优先级

1. **🥇 最佳：企业版 API**（如果预算允许）
   - 合同保证数据不用于训练
   - 符合合规要求

2. **🥈 推荐：付费账户 + 禁用设置**
   - 成本较低
   - 设置简单

3. **🥉 备选：本地模型（Ollama）**
   - 完全不上传数据
   - 免费使用
   - 需要本地硬件支持

## 验证设置是否生效

### 方法 1：检查设置页面
- 访问：https://platform.openai.com/settings/data-usage
- 确认 "Data usage for training" 为 OFF

### 方法 2：查看 API 使用日志
- 访问：https://platform.openai.com/usage
- 检查数据使用情况

## 重要提示

- ⚠️ 即使禁用了训练，数据仍会发送到 OpenAI 服务器进行处理
- ⚠️ 只有使用本地模型才能完全避免数据上传
- ✅ 数据脱敏功能已启用，降低了隐私风险
- ✅ 企业版提供最强的数据保护保证

## 下一步

1. **立即检查** OpenAI 设置页面
2. **如果可用**：禁用数据用于训练
3. **如果不可用**：考虑升级账户或使用本地模型
4. **长期**：评估是否需要企业版或完全本地化

---

**记住：数据脱敏已启用，这是第一层保护！** 🔒
