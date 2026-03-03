"""
数据库迁移脚本：为孩子表添加英文字段
运行此脚本将为现有的 children 表添加英文版本的 special_conditions 字段
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
        cursor.execute("PRAGMA table_info(children)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'special_conditions_en' not in columns:
            try:
                cursor.execute("ALTER TABLE children ADD COLUMN special_conditions_en TEXT")
                conn.commit()
                print("✅ 已添加字段: special_conditions_en")
            except sqlite3.OperationalError as e:
                print(f"⚠️  添加字段 special_conditions_en 失败: {e}")
        else:
            print("ℹ️  字段 special_conditions_en 已存在，跳过")
            
        print("\n✅ 迁移完成！")
            
    except Exception as e:
        print(f"❌ 迁移过程中出现错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("开始数据库迁移...")
    migrate_database()
    print("迁移完成！")
