import os
from openai import OpenAI
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

load_dotenv()


class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  警告: 未找到 OPENAI_API_KEY 环境变量")
            print("   提示: 请在 backend/.env 文件中设置 OPENAI_API_KEY")
            print("   应用可以启动，但AI评估功能将不可用")
            self.client = None
            self.api_key_available = False
        else:
            try:
                # 延迟初始化 OpenAI 客户端，避免版本兼容问题
                self.api_key = api_key
                self.client = None  # 将在首次使用时初始化
                self.api_key_available = True
            except Exception as e:
                print(f"⚠️  警告: OpenAI 客户端初始化失败: {e}")
                self.client = None
                self.api_key_available = False
    
    def _get_client(self):
        """获取或创建 OpenAI 客户端"""
        if not self.api_key_available:
            return None
        if self.client is None:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"⚠️  错误: 无法创建 OpenAI 客户端: {e}")
                return None
        return self.client
        
        # Initialize ChromaDB (optional, for future use)
        try:
            chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            os.makedirs(chroma_path, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=chroma_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name="child_development_knowledge"
            )
        except Exception as e:
            print(f"Warning: ChromaDB initialization failed: {e}. Continuing without vector database.")
            self.chroma_client = None
            self.collection = None
    
    async def analyze_development(self, child_info: dict, current_record: dict, previous_records: list) -> dict:
        """使用LLM分析孩子的发育情况"""
        
        # 构建上下文
        context = f"""
        孩子信息：
        - 姓名：{child_info['name']}
        - 出生日期：{child_info['birth_date']}
        - 特殊情况：{child_info['special_conditions']}
        
        当前记录：
        - 身高：{current_record.get('height', '未记录')} cm
        - 体重：{current_record.get('weight', '未记录')} kg
        - 头围：{current_record.get('head_circumference', '未记录')} cm
        - 大运动：{current_record.get('gross_motor', '未记录')}
        - 语言：{current_record.get('language', '未记录')}
        - 精细动作：{current_record.get('fine_motor', '未记录')}
        - 睡眠：{current_record.get('sleep', '未记录')}
        - 饮食：{current_record.get('diet', '未记录')}
        """
        
        if previous_records:
            context += "\n\n历史记录（最近3条）：\n"
            for i, record in enumerate(previous_records[:3], 1):
                context += f"""
                记录{i}：
                - 日期：{record.get('record_date', '未知')}
                - 身高：{record.get('height', '未记录')}
                - 体重：{record.get('weight', '未记录')}
                - 大运动：{record.get('gross_motor', '未记录')}
                - 语言：{record.get('language', '未记录')}
                """
        
        prompt = f"""
        你是一位专业的儿童发育评估专家。请根据以下信息评估孩子的发育情况。
        
        {context}
        
        请分析：
        1. 孩子目前的发育状态是"正常发育"、"良性发育"还是"倒退"？
        2. 详细说明评估依据
        3. 指出需要关注的方面
        
        请以JSON格式返回：
        {{
            "status": "正常发育/良性发育/倒退",
            "details": "详细评估说明",
            "concerns": ["需要关注的方面1", "需要关注的方面2"]
        }}
        """
        
        client = self._get_client()
        if not client:
            return {
                "status": "需要配置API Key",
                "details": "请先在 backend/.env 文件中设置 OPENAI_API_KEY 才能使用AI评估功能。\n\n当前记录已保存，但无法进行AI评估。",
                "concerns": []
            }
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位专业的儿童发育评估专家，擅长评估有特殊情况儿童的发育进展。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            # 尝试解析JSON
            import json
            try:
                return json.loads(result)
            except:
                # 如果不是JSON，返回文本格式
                return {
                    "status": "正常发育",
                    "details": result,
                    "concerns": []
                }
        except Exception as e:
            return {
                "status": "评估失败",
                "details": f"评估过程中出现错误：{str(e)}",
                "concerns": []
            }
    
    async def predict_milestones(self, child_info: dict, records: list) -> list:
        """预测下一个发育里程碑"""
        
        context = f"""
        孩子信息：
        - 姓名：{child_info['name']}
        - 出生日期：{child_info['birth_date']}
        - 特殊情况：{child_info['special_conditions']}
        - 当前年龄：{child_info.get('age_months', 0)} 个月
        """
        
        if records:
            latest = records[0]
            context += f"""
            
            最新发育情况：
            - 大运动：{latest.get('gross_motor', '未记录')}
            - 语言：{latest.get('language', '未记录')}
            - 精细动作：{latest.get('fine_motor', '未记录')}
            """
        
        prompt = f"""
        你是一位专业的儿童发育专家。请根据以下信息预测孩子接下来可能达到的发育里程碑。
        
        {context}
        
        请预测3-5个接下来可能达到的发育里程碑，包括：
        1. 里程碑名称
        2. 预计时间（月龄）
        3. 里程碑描述
        4. 达成建议
        
        请以JSON数组格式返回：
        [
            {{
                "milestone": "里程碑名称",
                "expected_age_months": 预计月龄,
                "description": "里程碑描述",
                "suggestions": "达成建议"
            }}
        ]
        """
        
        client = self._get_client()
        if not client:
            return [{
                "milestone": "需要配置API Key",
                "expected_age_months": 0,
                "description": "请先在 backend/.env 文件中设置 OPENAI_API_KEY 才能使用里程碑预测功能。",
                "suggestions": "获取API Key: https://platform.openai.com/api-keys"
            }]
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位专业的儿童发育专家，擅长预测有特殊情况儿童的发育里程碑。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            result = response.choices[0].message.content
            import json
            try:
                return json.loads(result)
            except:
                return [{
                    "milestone": "解析失败",
                    "expected_age_months": 0,
                    "description": result,
                    "suggestions": ""
                }]
        except Exception as e:
            return [{
                "milestone": "预测失败",
                "expected_age_months": 0,
                "description": f"预测过程中出现错误：{str(e)}",
                "suggestions": ""
            }]
