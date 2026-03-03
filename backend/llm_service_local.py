"""
本地模型版本 - 使用 Ollama 或其他本地 LLM
数据完全不离开服务器
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


class LocalLLMService:
    """使用本地模型的 LLM 服务（数据不上传）"""
    
    def __init__(self, base_url="http://localhost:11434"):
        """
        Args:
            base_url: Ollama 服务地址（默认 http://localhost:11434）
        """
        self.base_url = base_url
        self.model = os.getenv("LOCAL_LLM_MODEL", "llama2")  # 默认使用 llama2
        self.available = self._check_availability()
        
        if not self.available:
            print("⚠️  警告: 本地 LLM 服务不可用")
            print(f"   请确保 Ollama 正在运行: {base_url}")
            print("   安装: https://ollama.ai/download")
            print("   启动: ollama serve")
    
    def _check_availability(self):
        """检查本地 LLM 服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    async def analyze_development(self, child_info: dict, current_record: dict, previous_records: list) -> dict:
        """使用本地 LLM 分析孩子的发育情况"""
        
        if not self.available:
            return {
                "status": "本地模型不可用",
                "details": "请确保 Ollama 正在运行。安装: https://ollama.ai/download",
                "concerns": []
            }
        
        # 构建上下文
        context = f"""
        孩子信息：
        - 姓名：{child_info['name']}
        - 年龄：{child_info.get('age_months', 0)} 个月
        - 特殊情况：{child_info.get('special_conditions', '未记录')}
        
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
        
        try:
            # 调用 Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                # 尝试解析JSON
                try:
                    # 提取JSON部分
                    json_match = None
                    if "{" in result and "}" in result:
                        start = result.find("{")
                        end = result.rfind("}") + 1
                        json_str = result[start:end]
                        json_match = json.loads(json_str)
                    
                    if json_match:
                        return json_match
                    else:
                        return {
                            "status": "正常发育",
                            "details": result,
                            "concerns": []
                        }
                except:
                    return {
                        "status": "正常发育",
                        "details": result,
                        "concerns": []
                    }
            else:
                return {
                    "status": "评估失败",
                    "details": f"本地模型返回错误: {response.status_code}",
                    "concerns": []
                }
        except Exception as e:
            return {
                "status": "评估失败",
                "details": f"调用本地模型时出错: {str(e)}",
                "concerns": []
            }
    
    async def predict_milestones(self, child_info: dict, records: list) -> list:
        """使用本地 LLM 预测发育里程碑"""
        
        if not self.available:
            return [{
                "milestone": "本地模型不可用",
                "expected_age_months": 0,
                "description": "请确保 Ollama 正在运行",
                "suggestions": ""
            }]
        
        context = f"""
        孩子信息：
        - 姓名：{child_info['name']}
        - 年龄：{child_info.get('age_months', 0)} 个月
        - 特殊情况：{child_info.get('special_conditions', '未记录')}
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
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                try:
                    if "[" in result and "]" in result:
                        start = result.find("[")
                        end = result.rfind("]") + 1
                        json_str = result[start:end]
                        return json.loads(json_str)
                    else:
                        return [{
                            "milestone": "解析失败",
                            "expected_age_months": 0,
                            "description": result,
                            "suggestions": ""
                        }]
                except:
                    return [{
                        "milestone": "解析失败",
                        "expected_age_months": 0,
                        "description": result,
                        "suggestions": ""
                    }]
            else:
                return [{
                    "milestone": "预测失败",
                    "expected_age_months": 0,
                    "description": f"本地模型返回错误: {response.status_code}",
                    "suggestions": ""
                }]
        except Exception as e:
            return [{
                "milestone": "预测失败",
                "expected_age_months": 0,
                "description": f"调用本地模型时出错: {str(e)}",
                "suggestions": ""
            }]
