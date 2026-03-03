# 数据存储说明

## 存储位置

孩子档案信息存储在 **SQLite 数据库文件** 中：

**文件路径：** `backend/child_development.db`

这是一个本地数据库文件，所有数据都保存在这个文件中。

## 数据库结构

### 1. 孩子档案表 (children)

存储孩子的基本信息：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自动生成 |
| name | String | 孩子姓名 |
| birth_date | Date | 出生日期 |
| special_conditions | Text | 特殊情况描述 |
| gender | String | 性别（可选） |
| created_at | DateTime | 创建时间 |

### 2. 发育记录表 (development_records)

存储每次的发育记录：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自动生成 |
| child_id | Integer | 关联的孩子ID |
| record_date | DateTime | 记录日期 |
| height | Float | 身高 (cm) |
| weight | Float | 体重 (kg) |
| head_circumference | Float | 头围 (cm) |
| gross_motor | Text | 大运动描述 |
| language | Text | 语言发展描述 |
| fine_motor | Text | 精细动作描述 |
| sleep | Text | 睡眠情况 |
| diet | Text | 饮食情况 |
| notes | Text | 其他备注 |
| image_paths | Text | 图片路径（JSON格式） |
| video_paths | Text | 视频路径（JSON格式） |
| assessment | String | AI评估结果 |
| assessment_details | Text | 评估详情 |

## 文件存储

### 上传的图片和视频

存储在文件系统中：

**路径结构：**
```
backend/
  └── uploads/
      └── {child_id}/
          ├── images/
          │   └── {唯一文件名}.jpg/png/...
          └── videos/
              └── {唯一文件名}.mp4/...
```

例如：
- `backend/uploads/1/images/abc123.jpg`
- `backend/uploads/1/videos/def456.mp4`

## 查看数据

### 方法 1：使用 SQLite 命令行工具

```bash
cd backend
sqlite3 child_development.db

# 查看所有孩子
SELECT * FROM children;

# 查看某个孩子的记录
SELECT * FROM development_records WHERE child_id = 1;

# 退出
.quit
```

### 方法 2：使用数据库可视化工具

可以使用以下工具打开 `.db` 文件：
- **DB Browser for SQLite** (免费): https://sqlitebrowser.org/
- **DBeaver** (免费): https://dbeaver.io/
- **VS Code 扩展**: SQLite Viewer

### 方法 3：通过 API 查看

```bash
# 获取所有孩子
curl http://localhost:8000/api/children

# 获取某个孩子的记录
curl http://localhost:8000/api/children/1/records
```

## 数据备份

### 备份数据库

```bash
# Windows
copy backend\child_development.db backend\child_development.db.backup

# Linux/Mac
cp backend/child_development.db backend/child_development.db.backup
```

### 备份上传的文件

```bash
# Windows
xcopy backend\uploads backend\uploads_backup /E /I

# Linux/Mac
cp -r backend/uploads backend/uploads_backup
```

## 数据迁移

如果需要迁移到其他服务器：

1. 复制 `child_development.db` 文件
2. 复制整个 `uploads/` 目录
3. 在新服务器上运行应用即可

## 注意事项

- ⚠️ **数据安全**: 数据库文件包含敏感信息，请妥善保管
- ⚠️ **定期备份**: 建议定期备份数据库文件
- ⚠️ **文件大小**: 如果上传大量图片/视频，`uploads/` 目录可能会变得很大
- ✅ **可移植性**: SQLite 数据库文件可以轻松复制和迁移
