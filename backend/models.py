from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Child(Base):
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    special_conditions = Column(Text, nullable=False)  # 特殊情况（中文）
    special_conditions_en = Column(Text, nullable=True)  # Special Conditions (English)
    gender = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    records = relationship("DevelopmentRecord", back_populates="child")


class DevelopmentRecord(Base):
    __tablename__ = "development_records"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    record_date = Column(DateTime, default=datetime.utcnow)
    
    # 身体指标
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    head_circumference = Column(Float, nullable=True)
    
    # 发育指标（中文版本）
    gross_motor = Column(Text, nullable=True)  # 大运动
    language = Column(Text, nullable=True)  # 语言
    fine_motor = Column(Text, nullable=True)  # 精细动作
    sleep = Column(Text, nullable=True)  # 睡眠
    diet = Column(Text, nullable=True)  # 饮食
    
    # 发育指标（英文版本）
    gross_motor_en = Column(Text, nullable=True)  # Gross Motor (English)
    language_en = Column(Text, nullable=True)  # Language (English)
    fine_motor_en = Column(Text, nullable=True)  # Fine Motor (English)
    sleep_en = Column(Text, nullable=True)  # Sleep (English)
    diet_en = Column(Text, nullable=True)  # Diet (English)
    
    # 其他
    notes = Column(Text, nullable=True)
    notes_en = Column(Text, nullable=True)  # Notes (English)
    image_paths = Column(Text, nullable=True)  # JSON格式存储多个图片路径
    video_paths = Column(Text, nullable=True)  # JSON格式存储多个视频路径
    
    # 评估结果
    assessment = Column(String, nullable=True)  # "正常发育", "良性发育", "倒退"
    assessment_details = Column(Text, nullable=True)  # 详细评估说明（JSON格式，包含依据）
    
    child = relationship("Child", back_populates="records")
