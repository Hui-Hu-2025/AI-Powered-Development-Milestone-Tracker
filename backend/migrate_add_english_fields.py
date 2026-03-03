"""
数据库迁移脚本：为发育记录表添加英文字段
运行此脚本将为现有的 development_records 表添加英文版本的字段
"""
import sqlite3
import os

def migrate_database():
    db_path = "child_development.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在，无需迁移。")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(development_records)")
        columns = [row[1] for row in cursor.fetchall()]
        
        fields_to_add = [
            ("gross_motor_en", "TEXT"),
            ("language_en", "TEXT"),
            ("fine_motor_en", "TEXT"),
            ("sleep_en", "TEXT"),
            ("diet_en", "TEXT"),
            ("notes_en", "TEXT")
        ]
        
        added_fields = []
        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE development_records ADD COLUMN {field_name} {field_type}")
                    added_fields.append(field_name)
                    print(f"✅ 已添加字段: {field_name}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️  添加字段 {field_name} 失败: {e}")
            else:
                print(f"ℹ️  字段 {field_name} 已存在，跳过")
        
        conn.commit()
        
        if added_fields:
            print(f"\n✅ 迁移完成！已添加 {len(added_fields)} 个新字段。")
        else:
            print("\nℹ️  所有字段已存在，无需迁移。")
            
    except Exception as e:
        print(f"❌ 迁移过程中出现错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("开始数据库迁移...")
    migrate_database()
    print("迁移完成！")
