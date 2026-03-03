from datetime import datetime, date
from typing import List
from models import Child, DevelopmentRecord
try:
    from llm_service_secure import SecureLLMService as LLMService
except:
    from llm_service import LLMService


class DevelopmentService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def assess_development(self, child: Child, record: DevelopmentRecord, language: str = 'zh') -> dict:
        """评估孩子的发育情况"""
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            # 获取历史记录
            previous_records = db.query(DevelopmentRecord).filter(
                DevelopmentRecord.child_id == child.id,
                DevelopmentRecord.id != record.id
            ).order_by(DevelopmentRecord.record_date.desc()).limit(5).all()
            
            # 计算年龄（月）
            today = date.today()
            age_months = (today.year - child.birth_date.year) * 12 + \
                        (today.month - child.birth_date.month)
            
            child_info = {
                "name": child.name,
                "birth_date": str(child.birth_date),
                "special_conditions": child.special_conditions,
                "age_months": age_months
            }
            
            current_record = {
                "height": record.height,
                "weight": record.weight,
                "head_circumference": record.head_circumference,
                "gross_motor": record.gross_motor,
                "language": record.language,
                "fine_motor": record.fine_motor,
                "sleep": record.sleep,
                "diet": record.diet
            }
            
            previous_records_data = [
                {
                    "record_date": str(r.record_date),
                    "height": r.height,
                    "weight": r.weight,
                    "gross_motor": r.gross_motor,
                    "language": r.language,
                    "fine_motor": r.fine_motor
                }
                for r in previous_records
            ]
            
            assessment = await self.llm_service.analyze_development(
                child_info, current_record, previous_records_data, language=language
            )
            
            return assessment
        finally:
            db.close()


class MilestoneService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def predict_milestones(self, child: Child, records: List[DevelopmentRecord], language: str = 'zh') -> List[dict]:
        """预测发育里程碑"""
        from datetime import date
        
        today = date.today()
        age_months = (today.year - child.birth_date.year) * 12 + \
                    (today.month - child.birth_date.month)
        
        child_info = {
            "name": child.name,
            "birth_date": str(child.birth_date),
            "special_conditions": child.special_conditions,
            "age_months": age_months
        }
        
        records_data = [
            {
                "gross_motor": r.gross_motor,
                "language": r.language,
                "fine_motor": r.fine_motor
            }
            for r in records[:5]
        ]
        
        milestones = await self.llm_service.predict_milestones(child_info, records_data, language=language)
        return milestones
    
    async def get_development_comparison(self, child: Child, record: DevelopmentRecord, age_months: int, language: str = 'zh') -> dict:
        """获取与正常发育标准的对比"""
        child_info = {
            "name": child.name,
            "birth_date": str(child.birth_date),
            "special_conditions": child.special_conditions,
            "age_months": age_months
        }
        
        current_record = {
            "height": record.height,
            "weight": record.weight,
            "head_circumference": record.head_circumference,
            "gross_motor": record.gross_motor,
            "language": record.language,
            "fine_motor": record.fine_motor,
            "sleep": record.sleep,
            "diet": record.diet
        }
        
        comparison = await self.llm_service.get_development_comparison(child_info, current_record, age_months, language=language)
        return comparison
