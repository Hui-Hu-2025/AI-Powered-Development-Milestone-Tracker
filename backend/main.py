from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import sys
from dotenv import load_dotenv
import json
import uuid

from database import SessionLocal, init_db
from models import Child, DevelopmentRecord
from services import DevelopmentService, MilestoneService
# 使用安全版本，启用数据脱敏
from llm_service_secure import SecureLLMService as LLMService

load_dotenv()

app = FastAPI(title="Child Development Monitoring API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Initialize services with data anonymization enabled
# 启用数据脱敏：真实姓名、出生日期等敏感信息将被替换为匿名标识
llm_service = LLMService(anonymize=True)
dev_service = DevelopmentService(llm_service)
milestone_service = MilestoneService(llm_service)

# Mount static files for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


class ChildCreate(BaseModel):
    name: str
    birth_date: str
    special_conditions: str
    gender: Optional[str] = None


class DevelopmentRecordCreate(BaseModel):
    child_id: int
    height: Optional[float] = None
    weight: Optional[float] = None
    head_circumference: Optional[float] = None
    gross_motor: Optional[str] = None
    language: Optional[str] = None
    fine_motor: Optional[str] = None
    sleep: Optional[str] = None
    diet: Optional[str] = None
    notes: Optional[str] = None


@app.get("/")
async def root():
    return {"message": "Child Development Monitoring API"}


@app.post("/api/children")
async def create_child(
    name: str = Form(...),
    birth_date: str = Form(...),
    special_conditions: str = Form(...),
    gender: Optional[str] = Form(None),
    request_language: Optional[str] = Form('zh')
):
    """创建孩子档案"""
    db = SessionLocal()
    try:
        # 根据请求语言决定保存到哪个字段并翻译
        if request_language == 'en':
            # 用户用英文界面输入，保存到英文字段
            special_conditions_en_val = special_conditions
            # 翻译到中文字段
            special_conditions_val = await llm_service.translate_text(special_conditions, 'zh') if special_conditions else None
        else:
            # 用户用中文界面输入，保存到中文字段
            special_conditions_val = special_conditions
            # 翻译到英文字段
            special_conditions_en_val = await llm_service.translate_text(special_conditions, 'en') if special_conditions else None
        
        db_child = Child(
            name=name,
            birth_date=datetime.strptime(birth_date, "%Y-%m-%d").date(),
            special_conditions=special_conditions_val,
            special_conditions_en=special_conditions_en_val,
            gender=gender
        )
        db.add(db_child)
        db.commit()
        db.refresh(db_child)
        return {"id": db_child.id, "message": "Child created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/children")
async def get_children(language: str = 'zh'):
    """获取所有孩子列表"""
    db = SessionLocal()
    try:
        children = db.query(Child).all()
        result = []
        for c in children:
            # 安全地获取英文字段
            try:
                special_conditions_en = getattr(c, 'special_conditions_en', None)
            except:
                special_conditions_en = None
            
            # 根据语言选择显示内容
            if language == 'en':
                # 如果请求英文，优先显示英文，如果为空则回退到中文
                special_conditions = special_conditions_en if special_conditions_en else c.special_conditions
                # 如果没有英文版本，自动翻译并保存
                if not special_conditions_en and c.special_conditions:
                    try:
                        translated = await llm_service.translate_text(c.special_conditions, 'en')
                        c.special_conditions_en = translated
                        db.commit()
                        special_conditions = translated
                    except Exception as e:
                        print(f"翻译special_conditions失败: {e}")
                        special_conditions = c.special_conditions
            else:
                special_conditions = c.special_conditions if c.special_conditions else special_conditions_en
            
            result.append({
                "id": c.id,
                "name": c.name,
                "birth_date": str(c.birth_date),
                "special_conditions": special_conditions,
                "gender": c.gender
            })
        return result
    finally:
        db.close()


@app.get("/api/children/{child_id}")
async def get_child(child_id: int, language: str = 'zh'):
    """获取单个孩子信息"""
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")
        
        # 安全地获取英文字段
        try:
            special_conditions_en = getattr(child, 'special_conditions_en', None)
        except:
            special_conditions_en = None
        
        # 根据语言选择显示内容
        if language == 'en':
            # 如果请求英文，优先显示英文，如果为空则回退到中文
            special_conditions = special_conditions_en if special_conditions_en else child.special_conditions
            # 如果没有英文版本，自动翻译并保存
            if not special_conditions_en and child.special_conditions:
                try:
                    translated = await llm_service.translate_text(child.special_conditions, 'en')
                    child.special_conditions_en = translated
                    db.commit()
                    special_conditions = translated
                except Exception as e:
                    print(f"翻译special_conditions失败: {e}")
                    special_conditions = child.special_conditions
        else:
            special_conditions = child.special_conditions if child.special_conditions else special_conditions_en
        
        return {
            "id": child.id,
            "name": child.name,
            "birth_date": str(child.birth_date),
            "special_conditions": special_conditions,
            "gender": child.gender
        }
    finally:
        db.close()


@app.put("/api/children/{child_id}")
async def update_child(child_id: int, child: ChildCreate, request_language: Optional[str] = 'zh'):
    """更新孩子档案"""
    db = SessionLocal()
    try:
        db_child = db.query(Child).filter(Child.id == child_id).first()
        if not db_child:
            raise HTTPException(status_code=404, detail="Child not found")
        
        db_child.name = name
        db_child.birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        db_child.gender = gender
        
        # 根据请求语言决定保存到哪个字段并翻译
        if request_language == 'en':
            # 用户用英文界面输入，保存到英文字段
            db_child.special_conditions_en = special_conditions
            # 翻译到中文字段
            db_child.special_conditions = await llm_service.translate_text(special_conditions, 'zh') if special_conditions else None
        else:
            # 用户用中文界面输入，保存到中文字段
            db_child.special_conditions = special_conditions
            # 翻译到英文字段
            db_child.special_conditions_en = await llm_service.translate_text(special_conditions, 'en') if special_conditions else None
        
        db.commit()
        db.refresh(db_child)
        return {"id": db_child.id, "message": "Child updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


def parse_form_float(value: Optional[str]) -> Optional[float]:
    """解析表单中的浮点数，处理空字符串"""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def parse_json_safe(value, default=None):
    """安全地解析JSON，如果失败返回默认值或原始值"""
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # 如果不是JSON格式，返回原始字符串（兼容旧数据）
        return value if default is None else default

@app.post("/api/records")
async def create_record(
    child_id: int = Form(...),
    request_language: Optional[str] = Form('zh'),  # 请求语言参数，用于LLM生成
    height: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
    head_circumference: Optional[str] = Form(None),
    gross_motor: Optional[str] = Form(None),
    language: Optional[str] = Form(None),  # 孩子的语言发展情况
    fine_motor: Optional[str] = Form(None),
    sleep: Optional[str] = Form(None),
    diet: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    videos: Optional[List[UploadFile]] = File(None)
):
    """创建发育记录（支持图片和视频）"""
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")
        
        # 保存文件路径
        image_paths = []
        video_paths = []
        
        if images:
            os.makedirs(f"uploads/{child_id}/images", exist_ok=True)
            for img in images:
                if img.filename:
                    # 生成唯一文件名
                    file_ext = os.path.splitext(img.filename)[1]
                    unique_filename = f"{uuid.uuid4()}{file_ext}"
                    file_path = f"uploads/{child_id}/images/{unique_filename}"
                    with open(file_path, "wb") as f:
                        f.write(await img.read())
                    image_paths.append(file_path)
        
        if videos:
            os.makedirs(f"uploads/{child_id}/videos", exist_ok=True)
            for vid in videos:
                if vid.filename:
                    # 生成唯一文件名
                    file_ext = os.path.splitext(vid.filename)[1]
                    unique_filename = f"{uuid.uuid4()}{file_ext}"
                    file_path = f"uploads/{child_id}/videos/{unique_filename}"
                    with open(file_path, "wb") as f:
                        f.write(await vid.read())
                    video_paths.append(file_path)
        
        # 根据请求语言决定保存到哪个字段并翻译
        if request_language == 'en':
            # 用户用英文界面输入，保存到英文字段
            gross_motor_en_val = gross_motor if gross_motor else None
            language_en_val = language if language else None
            fine_motor_en_val = fine_motor if fine_motor else None
            sleep_en_val = sleep if sleep else None
            diet_en_val = diet if diet else None
            notes_en_val = notes if notes else None
            
            # 翻译到中文字段
            gross_motor_val = await llm_service.translate_text(gross_motor, 'zh') if gross_motor else None
            language_val = await llm_service.translate_text(language, 'zh') if language else None
            fine_motor_val = await llm_service.translate_text(fine_motor, 'zh') if fine_motor else None
            sleep_val = await llm_service.translate_text(sleep, 'zh') if sleep else None
            diet_val = await llm_service.translate_text(diet, 'zh') if diet else None
            notes_val = await llm_service.translate_text(notes, 'zh') if notes else None
        else:
            # 用户用中文界面输入，保存到中文字段
            gross_motor_val = gross_motor if gross_motor else None
            language_val = language if language else None
            fine_motor_val = fine_motor if fine_motor else None
            sleep_val = sleep if sleep else None
            diet_val = diet if diet else None
            notes_val = notes if notes else None
            
            # 翻译到英文字段
            gross_motor_en_val = await llm_service.translate_text(gross_motor, 'en') if gross_motor else None
            language_en_val = await llm_service.translate_text(language, 'en') if language else None
            fine_motor_en_val = await llm_service.translate_text(fine_motor, 'en') if fine_motor else None
            sleep_en_val = await llm_service.translate_text(sleep, 'en') if sleep else None
            diet_en_val = await llm_service.translate_text(diet, 'en') if diet else None
            notes_en_val = await llm_service.translate_text(notes, 'en') if notes else None
        
        record = DevelopmentRecord(
            child_id=child_id,
            height=parse_form_float(height),
            weight=parse_form_float(weight),
            head_circumference=parse_form_float(head_circumference),
            gross_motor=gross_motor_val,
            language=language_val,
            fine_motor=fine_motor_val,
            sleep=sleep_val,
            diet=diet_val,
            notes=notes_val,
            gross_motor_en=gross_motor_en_val,
            language_en=language_en_val,
            fine_motor_en=fine_motor_en_val,
            sleep_en=sleep_en_val,
            diet_en=diet_en_val,
            notes_en=notes_en_val,
            image_paths=json.dumps(image_paths) if image_paths else None,
            video_paths=json.dumps(video_paths) if video_paths else None
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        # 使用LLM评估发育情况（传递语言参数）
        assessment = await dev_service.assess_development(child, record, language=request_language)
        
        # 更新记录（保存完整的评估信息，包括依据）
        record.assessment = assessment.get("status", assessment.get("assessment", "评估中"))
        # 将完整的评估信息（包括依据）保存为JSON
        assessment_json = {
            "summary": assessment.get("summary", ""),
            "details": assessment.get("details", ""),
            "evidence": assessment.get("evidence", {}),
            "concerns": assessment.get("concerns", []),
            "recommendations": assessment.get("recommendations", [])
        }
        record.assessment_details = json.dumps(assessment_json, ensure_ascii=False)
        db.commit()
        
        return {
            "id": record.id,
            "assessment": assessment,
            "message": "Record created and assessed successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/children/{child_id}/records")
async def get_records(child_id: int, language: str = 'zh'):
    """获取孩子的所有发育记录"""
    db = SessionLocal()
    try:
        # 先检查表结构，看是否有英文字段
        from sqlalchemy import text
        result = db.execute(text("PRAGMA table_info(development_records)"))
        columns = [row[1] for row in result.fetchall()]
        has_english_fields = any(col.endswith('_en') for col in columns)
        
        if has_english_fields:
            # 如果有英文字段，使用SQLAlchemy查询
            records = db.query(DevelopmentRecord).filter(
                DevelopmentRecord.child_id == child_id
            ).order_by(DevelopmentRecord.record_date.desc()).all()
        else:
            # 如果没有英文字段，使用原始SQL查询，只查询存在的字段
            sql = """
                SELECT id, child_id, record_date, height, weight, head_circumference,
                       gross_motor, language, fine_motor, sleep, diet, notes,
                       assessment, assessment_details, image_paths, video_paths
                FROM development_records
                WHERE child_id = :child_id
                ORDER BY record_date DESC
            """
            result = db.execute(text(sql), {"child_id": child_id})
            # 将结果转换为类似ORM对象的格式
            class Record:
                pass
            records = []
            for row in result.fetchall():
                r = Record()
                r.id = row[0]
                r.child_id = row[1]
                r.record_date = row[2]
                r.height = row[3]
                r.weight = row[4]
                r.head_circumference = row[5]
                r.gross_motor = row[6]
                r.language = row[7]
                r.fine_motor = row[8]
                r.sleep = row[9]
                r.diet = row[10]
                r.notes = row[11]
                r.assessment = row[12]
                r.assessment_details = row[13]
                r.image_paths = row[14]
                r.video_paths = row[15]
                records.append(r)
        
        result = []
        for r in records:
            # 安全地获取字段值（兼容旧数据，如果字段不存在则返回None）
            try:
                gross_motor_en = getattr(r, 'gross_motor_en', None)
                language_en = getattr(r, 'language_en', None)
                fine_motor_en = getattr(r, 'fine_motor_en', None)
                sleep_en = getattr(r, 'sleep_en', None)
                diet_en = getattr(r, 'diet_en', None)
                notes_en = getattr(r, 'notes_en', None)
            except:
                gross_motor_en = language_en = fine_motor_en = sleep_en = diet_en = notes_en = None
            
            # 根据语言选择显示内容，优先显示对应语言，如果为空则回退到另一种语言
            # 如果请求英文但只有中文，自动翻译并保存
            if language == 'en':
                # 需要翻译的字段列表
                fields_to_translate = []
                
                if not gross_motor_en and r.gross_motor:
                    fields_to_translate.append(('gross_motor', r.gross_motor))
                if not language_en and r.language:
                    fields_to_translate.append(('language', r.language))
                if not fine_motor_en and r.fine_motor:
                    fields_to_translate.append(('fine_motor', r.fine_motor))
                if not sleep_en and r.sleep:
                    fields_to_translate.append(('sleep', r.sleep))
                if not diet_en and r.diet:
                    fields_to_translate.append(('diet', r.diet))
                if not notes_en and r.notes:
                    fields_to_translate.append(('notes', r.notes))
                
                # 如果有需要翻译的字段，且数据库有英文字段，则翻译并保存
                if fields_to_translate and has_english_fields:
                    record_obj = db.query(DevelopmentRecord).filter(DevelopmentRecord.id == r.id).first()
                    if record_obj:
                        for field_name, field_value in fields_to_translate:
                            try:
                                translated = await llm_service.translate_text(field_value, 'en')
                                setattr(record_obj, f'{field_name}_en', translated)
                                # 更新对应的英文字段变量
                                if field_name == 'gross_motor':
                                    gross_motor_en = translated
                                elif field_name == 'language':
                                    language_en = translated
                                elif field_name == 'fine_motor':
                                    fine_motor_en = translated
                                elif field_name == 'sleep':
                                    sleep_en = translated
                                elif field_name == 'diet':
                                    diet_en = translated
                                elif field_name == 'notes':
                                    notes_en = translated
                            except Exception as e:
                                print(f"翻译字段 {field_name} 失败: {e}")
                                # 翻译失败时使用原文
                                setattr(record_obj, f'{field_name}_en', field_value)
                        
                        db.commit()
                
                # 使用翻译后的英文或回退到中文
                gross_motor = gross_motor_en if gross_motor_en else r.gross_motor
                lang_field = language_en if language_en else r.language
                fine_motor = fine_motor_en if fine_motor_en else r.fine_motor
                sleep = sleep_en if sleep_en else r.sleep
                diet = diet_en if diet_en else r.diet
                notes = notes_en if notes_en else r.notes
            else:
                gross_motor = r.gross_motor if r.gross_motor else gross_motor_en
                lang_field = r.language if r.language else language_en
                fine_motor = r.fine_motor if r.fine_motor else fine_motor_en
                sleep = r.sleep if r.sleep else sleep_en
                diet = r.diet if r.diet else diet_en
                notes = r.notes if r.notes else notes_en
            
            # 处理评估状态和评估详情的语言切换
            assessment_status = r.assessment
            assessment_details_data = parse_json_safe(r.assessment_details)
            
            # 评估状态翻译映射
            status_translation = {
                '正常发育': 'Normal Development',
                '良性发育': 'Benign Development',
                '倒退': 'Regression',
                '评估中': 'Assessing',
                '需要配置API Key': 'API Key Required',
                '评估失败': 'Assessment Failed'
            }
            
            if language == 'en' and assessment_status:
                # 如果请求英文，翻译评估状态
                assessment_status = status_translation.get(assessment_status, assessment_status)
                # 如果不在映射中，尝试翻译
                if assessment_status not in status_translation.values():
                    try:
                        assessment_status = await llm_service.translate_text(assessment_status, 'en')
                    except:
                        pass
            
            # 处理评估详情的语言切换
            if language == 'en' and assessment_details_data:
                if isinstance(assessment_details_data, dict):
                    # 创建翻译后的副本
                    translated_details = {}
                    for key, value in assessment_details_data.items():
                        if key == 'evidence' and isinstance(value, dict):
                            # 翻译 evidence 中的内容
                            translated_evidence = {}
                            for ev_key, ev_value in value.items():
                                if isinstance(ev_value, str):
                                    try:
                                        translated_evidence[ev_key] = await llm_service.translate_text(ev_value, 'en')
                                    except:
                                        translated_evidence[ev_key] = ev_value
                                elif isinstance(ev_value, list):
                                    translated_list = []
                                    for item in ev_value:
                                        if isinstance(item, str):
                                            try:
                                                translated_list.append(await llm_service.translate_text(item, 'en'))
                                            except:
                                                translated_list.append(item)
                                        else:
                                            translated_list.append(item)
                                    translated_evidence[ev_key] = translated_list
                                else:
                                    translated_evidence[ev_key] = ev_value
                            translated_details[key] = translated_evidence
                        elif key in ['concerns', 'recommendations'] and isinstance(value, list):
                            # 翻译列表中的字符串
                            translated_list = []
                            for item in value:
                                if isinstance(item, str):
                                    try:
                                        translated_list.append(await llm_service.translate_text(item, 'en'))
                                    except:
                                        translated_list.append(item)
                                else:
                                    translated_list.append(item)
                            translated_details[key] = translated_list
                        elif isinstance(value, str):
                            # 翻译字符串值
                            try:
                                translated_details[key] = await llm_service.translate_text(value, 'en')
                            except:
                                translated_details[key] = value
                        else:
                            translated_details[key] = value
                    assessment_details_data = translated_details
            
            result.append({
                "id": r.id,
                "record_date": str(r.record_date),
                "height": r.height,
                "weight": r.weight,
                "head_circumference": r.head_circumference,
                "gross_motor": gross_motor,
                "language": lang_field,
                "fine_motor": fine_motor,
                "sleep": sleep,
                "diet": diet,
                "notes": notes,
                "assessment": assessment_status,
                "assessment_details": assessment_details_data,
                "image_paths": parse_json_safe(r.image_paths, default=[]),
                "video_paths": parse_json_safe(r.video_paths, default=[])
            })
        
        return result
    except Exception as e:
        # 如果出错，返回错误信息以便调试
        import traceback
        print(f"获取记录时出错: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get records: {str(e)}")
    finally:
        db.close()


@app.get("/api/children/{child_id}/milestones")
async def predict_milestones(child_id: int, language: str = 'zh'):
    """预测下一个发育里程碑（仅返回3岁及之前的里程碑）"""
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")
        
        records = db.query(DevelopmentRecord).filter(
            DevelopmentRecord.child_id == child_id
        ).order_by(DevelopmentRecord.record_date.desc()).all()
        
        milestones = await milestone_service.predict_milestones(child, records, language=language)
        
        # 过滤：只返回3岁（36个月）及之前的里程碑
        MAX_AGE_MONTHS = 36
        filtered_milestones = [
            milestone for milestone in milestones
            if milestone.get('expected_age_months', 0) <= MAX_AGE_MONTHS
        ]
        
        return filtered_milestones
    finally:
        db.close()


@app.put("/api/records/{record_id}")
async def update_record(
    record_id: int,
    child_id: int = Form(...),
    request_language: Optional[str] = Form('zh'),  # 请求语言参数
    height: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
    head_circumference: Optional[str] = Form(None),
    gross_motor: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    fine_motor: Optional[str] = Form(None),
    sleep: Optional[str] = Form(None),
    diet: Optional[str] = Form(None),
    notes: Optional[str] = Form(None)
):
    """更新发育记录"""
    db = SessionLocal()
    try:
        record = db.query(DevelopmentRecord).filter(DevelopmentRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        if record.child_id != child_id:
            raise HTTPException(status_code=400, detail="Child ID mismatch")
        
        record.height = parse_form_float(height)
        record.weight = parse_form_float(weight)
        record.head_circumference = parse_form_float(head_circumference)
        
        # 根据请求语言决定保存到哪个字段并翻译
        if request_language == 'en':
            # 用户用英文界面输入，保存到英文字段
            record.gross_motor_en = gross_motor if gross_motor else None
            record.language_en = language if language else None
            record.fine_motor_en = fine_motor if fine_motor else None
            record.sleep_en = sleep if sleep else None
            record.diet_en = diet if diet else None
            record.notes_en = notes if notes else None
            
            # 翻译到中文字段
            record.gross_motor = await llm_service.translate_text(gross_motor, 'zh') if gross_motor else None
            record.language = await llm_service.translate_text(language, 'zh') if language else None
            record.fine_motor = await llm_service.translate_text(fine_motor, 'zh') if fine_motor else None
            record.sleep = await llm_service.translate_text(sleep, 'zh') if sleep else None
            record.diet = await llm_service.translate_text(diet, 'zh') if diet else None
            record.notes = await llm_service.translate_text(notes, 'zh') if notes else None
        else:
            # 用户用中文界面输入，保存到中文字段
            record.gross_motor = gross_motor if gross_motor else None
            record.language = language if language else None
            record.fine_motor = fine_motor if fine_motor else None
            record.sleep = sleep if sleep else None
            record.diet = diet if diet else None
            record.notes = notes if notes else None
            
            # 翻译到英文字段
            record.gross_motor_en = await llm_service.translate_text(gross_motor, 'en') if gross_motor else None
            record.language_en = await llm_service.translate_text(language, 'en') if language else None
            record.fine_motor_en = await llm_service.translate_text(fine_motor, 'en') if fine_motor else None
            record.sleep_en = await llm_service.translate_text(sleep, 'en') if sleep else None
            record.diet_en = await llm_service.translate_text(diet, 'en') if diet else None
            record.notes_en = await llm_service.translate_text(notes, 'en') if notes else None
        
        db.commit()
        db.refresh(record)
        
        # 重新评估
        child = db.query(Child).filter(Child.id == child_id).first()
        assessment = await dev_service.assess_development(child, record, language=request_language)
        
        record.assessment = assessment.get("status", assessment.get("assessment", "评估中"))
        assessment_json = {
            "summary": assessment.get("summary", ""),
            "details": assessment.get("details", ""),
            "evidence": assessment.get("evidence", {}),
            "concerns": assessment.get("concerns", []),
            "recommendations": assessment.get("recommendations", [])
        }
        record.assessment_details = json.dumps(assessment_json, ensure_ascii=False)
        db.commit()
        
        return {"id": record.id, "message": "Record updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.delete("/api/records/{record_id}")
async def delete_record(record_id: int):
    """删除发育记录"""
    db = SessionLocal()
    try:
        record = db.query(DevelopmentRecord).filter(DevelopmentRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        child_id = record.child_id
        
        # 删除关联的文件
        if record.image_paths:
            try:
                image_paths = json.loads(record.image_paths)
                for img_path in image_paths:
                    if os.path.exists(img_path):
                        os.remove(img_path)
            except:
                pass
        
        if record.video_paths:
            try:
                video_paths = json.loads(record.video_paths)
                for vid_path in video_paths:
                    if os.path.exists(vid_path):
                        os.remove(vid_path)
            except:
                pass
        
        # 删除记录
        db.delete(record)
        db.commit()
        
        return {"message": "Record deleted successfully", "child_id": child_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/children/{child_id}/comparison")
async def get_development_comparison(child_id: int, language: str = 'zh'):
    """获取与正常发育标准的对比"""
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")
        
        # 获取最新记录
        latest_record = db.query(DevelopmentRecord).filter(
            DevelopmentRecord.child_id == child_id
        ).order_by(DevelopmentRecord.record_date.desc()).first()
        
        if not latest_record:
            raise HTTPException(status_code=404, detail="No records found")
        
        # 计算年龄
        from datetime import date
        today = date.today()
        age_months = (today.year - child.birth_date.year) * 12 + \
                    (today.month - child.birth_date.month)
        
        # 使用LLM获取正常发育标准和对比
        comparison = await milestone_service.get_development_comparison(child, latest_record, age_months, language=language)
        return comparison
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    import socket
    
    # 从环境变量获取端口，默认8000
    port = int(os.getenv("PORT", 8000))
    
    # 检查端口是否可用
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return True
            except OSError:
                return False
    
    # 如果端口被占用，尝试其他端口
    if not is_port_available(port):
        print(f"⚠️  端口 {port} 已被占用，尝试其他端口...")
        for alt_port in range(8001, 8010):
            if is_port_available(alt_port):
                port = alt_port
                print(f"✅ 使用端口 {port}")
                break
        else:
            print(f"❌ 无法找到可用端口 (8000-8009)")
            print("请运行以下命令释放端口 8000:")
            print("  python kill_port.py")
            sys.exit(1)
    
    print(f"🚀 启动服务器: http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
