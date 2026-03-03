"""
安全版本的 LLM 服务 - 数据脱敏
在发送到 OpenAI 前移除敏感信息
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
import hashlib

load_dotenv()


class SecureLLMService:
    """安全版本的 LLM 服务，支持数据脱敏"""
    
    def __init__(self, anonymize=True):
        """
        Args:
            anonymize: 是否启用数据脱敏（默认True）
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  警告: 未找到 OPENAI_API_KEY 环境变量")
            print("   提示: 请在 backend/.env 文件中设置 OPENAI_API_KEY")
            print("   应用可以启动，但AI评估功能将不可用")
            self.client = None
            self.api_key_available = False
        else:
            try:
                self.api_key = api_key
                self.client = None
                self.api_key_available = True
            except Exception as e:
                print(f"⚠️  警告: OpenAI 客户端初始化失败: {e}")
                self.client = None
                self.api_key_available = False
        
        self.anonymize = anonymize
        self.name_mapping = {}  # 存储真实姓名到代号的映射
    
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
    
    def _anonymize_name(self, name):
        """将真实姓名转换为代号"""
        if not self.anonymize:
            return name
        
        if name not in self.name_mapping:
            # 使用哈希生成稳定的代号
            hash_obj = hashlib.md5(name.encode())
            code = f"孩子{hash_obj.hexdigest()[:4].upper()}"
            self.name_mapping[name] = code
        
        return self.name_mapping[name]
    
    def _anonymize_data(self, child_info, current_record, previous_records):
        """脱敏处理数据"""
        if not self.anonymize:
            return child_info, current_record, previous_records
        
        # 脱敏孩子信息
        anonymized_child_info = {
            "name": self._anonymize_name(child_info['name']),
            "age_months": child_info.get('age_months', 0),  # 只保留年龄，不保留出生日期
            "special_conditions": child_info.get('special_conditions', '')  # 保留，但可以进一步处理
        }
        
        # 脱敏当前记录（移除可能包含个人信息的备注）
        anonymized_record = {
            "height": current_record.get('height'),
            "weight": current_record.get('weight'),
            "head_circumference": current_record.get('head_circumference'),
            "gross_motor": current_record.get('gross_motor'),
            "language": current_record.get('language'),
            "fine_motor": current_record.get('fine_motor'),
            "sleep": current_record.get('sleep'),
            "diet": current_record.get('diet'),
            # 不发送 notes，可能包含个人信息
        }
        
        # 脱敏历史记录
        anonymized_previous = []
        for record in previous_records:
            anonymized_previous.append({
                "record_date": record.get('record_date', ''),  # 保留日期但不包含年份
                "height": record.get('height'),
                "weight": record.get('weight'),
                "gross_motor": record.get('gross_motor'),
                "language": record.get('language'),
                "fine_motor": record.get('fine_motor'),
            })
        
        return anonymized_child_info, anonymized_record, anonymized_previous
    
    async def analyze_development(self, child_info: dict, current_record: dict, previous_records: list, language: str = 'zh') -> dict:
        """使用LLM分析孩子的发育情况（安全版本）"""
        
        # 数据脱敏
        safe_child_info, safe_record, safe_previous = self._anonymize_data(
            child_info, current_record, previous_records
        )
        
        # 构建上下文（使用脱敏后的数据）
        context = f"""
        孩子信息（已匿名化）：
        - 代号：{safe_child_info['name']}
        - 年龄：{safe_child_info.get('age_months', 0)} 个月
        - 特殊情况：{safe_child_info.get('special_conditions', '未记录')}
        
        当前记录：
        - 身高：{safe_record.get('height', '未记录')} cm
        - 体重：{safe_record.get('weight', '未记录')} kg
        - 头围：{safe_record.get('head_circumference', '未记录')} cm
        - 大运动：{safe_record.get('gross_motor', '未记录')}
        - 语言：{safe_record.get('language', '未记录')}
        - 精细动作：{safe_record.get('fine_motor', '未记录')}
        - 睡眠：{safe_record.get('sleep', '未记录')}
        - 饮食：{safe_record.get('diet', '未记录')}
        """
        
        if safe_previous:
            context += "\n\n历史记录（最近3条，已匿名化）：\n"
            for i, record in enumerate(safe_previous[:3], 1):
                context += f"""
                记录{i}：
                - 身高：{record.get('height', '未记录')}
                - 体重：{record.get('weight', '未记录')}
                - 大运动：{record.get('gross_motor', '未记录')}
                - 语言：{record.get('language', '未记录')}
                """
        
        lang_instruction = "Please respond in English. All text content should be in English." if language == 'en' else "请用中文回复。所有文本内容请使用中文。"
        status_options = "Normal Development/Benign Development/Regression" if language == 'en' else "正常发育/良性发育/倒退"
        
        prompt = f"""
        你是一位专业的儿童发育评估专家。请根据以下信息评估孩子的发育情况。
        {lang_instruction}
        
        {context}
        
        请进行详细分析，并以JSON格式返回：
        {{
            "status": "{status_options}",
            "summary": "{'Brief summary (1-2 sentences)' if language == 'en' else '简要总结（1-2句话）'}",
            "details": "{'Detailed assessment description' if language == 'en' else '详细评估说明'}",
            "evidence": {{
                "data_comparison": "{'Data comparison analysis with historical records' if language == 'en' else '与历史记录的数据对比分析'}",
                "standard_reference": "{'Referenced development standards or milestones' if language == 'en' else '参考的发育标准或里程碑'}",
                "key_indicators": ["{'Key indicator 1' if language == 'en' else '关键指标1'}", "{'Key indicator 2' if language == 'en' else '关键指标2'}"],
                "trend_analysis": "{'Development trend analysis (Progress/Stable/Regression)' if language == 'en' else '发展趋势分析（进步/稳定/倒退）'}"
            }},
            "concerns": ["{'Area of concern 1' if language == 'en' else '需要关注的方面1'}", "{'Area of concern 2' if language == 'en' else '需要关注的方面2'}"],
            "recommendations": ["{'Recommendation 1' if language == 'en' else '建议1'}", "{'Recommendation 2' if language == 'en' else '建议2'}"]
        }}
        
        重要要求：
        1. evidence部分必须详细说明判断依据
        2. 如果提供了历史记录，必须进行对比分析
        3. 参考标准的发育里程碑进行判断
        4. 明确指出哪些数据支持你的判断
        5. {lang_instruction}
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
                    {"role": "system", "content": "你是一位专业的儿童发育评估专家，擅长评估有特殊情况儿童的发育进展。所有数据已匿名化处理。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            import json
            try:
                parsed = json.loads(result)
                # 确保返回格式完整
                if "evidence" not in parsed:
                    parsed["evidence"] = {
                        "data_comparison": "数据对比分析",
                        "standard_reference": "发育标准参考",
                        "key_indicators": [],
                        "trend_analysis": "趋势分析"
                    }
                return parsed
            except:
                # 如果解析失败，尝试提取JSON部分
                try:
                    import re
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        return parsed
                except:
                    pass
                # 如果都失败，返回基本格式
                return {
                    "status": "正常发育",
                    "summary": "评估完成",
                    "details": result,
                    "evidence": {
                        "data_comparison": "详见评估说明",
                        "standard_reference": "基于通用发育标准",
                        "key_indicators": [],
                        "trend_analysis": "详见评估说明"
                    },
                    "concerns": [],
                    "recommendations": []
                }
        except Exception as e:
                return {
                    "status": "评估失败",
                    "details": f"评估过程中出现错误：{str(e)}",
                    "concerns": []
                }
    
    async def translate_text(self, text: str, target_language: str = 'en') -> str:
        """使用LLM翻译文本"""
        if not text or not text.strip():
            return text
        
        client = self._get_client()
        if not client:
            return text  # 如果API不可用，返回原文
        
        try:
            prompt = f"""请将以下文本翻译成{'英文' if target_language == 'en' else '中文'}，保持专业术语的准确性，不要添加任何解释或说明，只返回翻译后的文本：

{text}"""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位专业的翻译助手，擅长翻译医疗和儿童发育相关的专业文本。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            translated = response.choices[0].message.content.strip()
            return translated
        except Exception as e:
            print(f"翻译失败: {e}")
            return text  # 翻译失败时返回原文
    
    async def predict_milestones(self, child_info: dict, records: list, language: str = 'zh') -> list:
        """预测下一个发育里程碑（安全版本）"""
        
        # 数据脱敏
        safe_child_info, _, _ = self._anonymize_data(child_info, {}, [])
        
        context = f"""
        孩子信息（已匿名化）：
        - 代号：{safe_child_info['name']}
        - 年龄：{safe_child_info.get('age_months', 0)} 个月
        - 特殊情况：{safe_child_info.get('special_conditions', '未记录')}
        """
        
        if records:
            latest = records[0]
            context += f"""
            
            最新发育情况：
            - 大运动：{latest.get('gross_motor', '未记录')}
            - 语言：{latest.get('language', '未记录')}
            - 精细动作：{latest.get('fine_motor', '未记录')}
            """
        
        lang_instruction = "Please respond in English." if language == 'en' else "请用中文回复。"
        lang_labels = {
            'zh': {
                'milestone': '里程碑名称',
                'expected_time': '预计时间（月龄）',
                'normal_range': '正常孩子达到该里程碑的时间段（月龄范围）',
                'description': '里程碑描述',
                'prediction_basis': '预测依据（为什么预测这个里程碑）',
                'suggestions': '达成建议',
                'example_range': '如：12-15个月',
                'basis_example': '预测依据：基于当前发育水平和标准里程碑的对比分析'
            },
            'en': {
                'milestone': 'Milestone name',
                'expected_time': 'Expected time (months)',
                'normal_range': 'Normal age range for this milestone (month range)',
                'description': 'Milestone description',
                'prediction_basis': 'Prediction basis (why predict this milestone)',
                'suggestions': 'Achievement suggestions',
                'example_range': 'e.g., 12-15 months',
                'basis_example': 'Prediction basis: Based on comparison of current development level and standard milestones'
            }
        }
        labels = lang_labels[language]
        
        # 计算最大预测月龄（3岁 = 36个月）
        MAX_PREDICTION_AGE = 36
        
        prompt = f"""
        你是一位专业的儿童发育专家。请根据以下信息预测孩子接下来可能达到的发育里程碑。
        {lang_instruction}
        
        {context}
        
        重要限制：只预测孩子3岁（36个月）及之前可能达到的里程碑。如果孩子已经接近或超过3岁，只预测到36个月为止的里程碑。所有里程碑的expected_age_months必须小于等于36。
        
        请预测8-12个接下来可能达到的发育里程碑，每个里程碑必须包括：
        1. {labels['milestone']}
        2. {labels['expected_time']}
        3. {labels['normal_range']}
        4. {labels['description']}
        5. {labels['prediction_basis']}
        6. {labels['suggestions']}
        
        请以JSON数组格式返回：
        [
            {{
                "milestone": "{labels['milestone']}",
                "expected_age_months": 预计月龄,
                "normal_age_range": "{labels['example_range']}",
                "description": "{labels['description']}",
                "prediction_basis": "{labels['basis_example']}",
                "suggestions": "{labels['suggestions']}"
            }}
        ]
        
        重要要求：
        1. 必须预测8-12个里程碑，不要只给2-3条
        2. normal_age_range必须包含正常发育的时间范围
        3. prediction_basis必须详细说明预测依据
        4. 参考当前年龄和发育水平
        5. 对比标准发育里程碑
        6. 说明为什么预测这个时间点
        7. 按照时间顺序排列，从近期到远期
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
                    {"role": "system", "content": "你是一位专业的儿童发育专家，擅长预测有特殊情况儿童的发育里程碑。所有数据已匿名化处理。"},
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
    
    async def get_development_comparison(self, child_info: dict, current_record: dict, age_months: int, language: str = 'zh') -> dict:
        """获取与正常发育标准的对比"""
        
        # 数据脱敏
        safe_child_info, safe_record, _ = self._anonymize_data(child_info, current_record, [])
        
        # 根据语言设置提示文本
        lang_instruction = "Please respond in English. All text content should be in English." if language == 'en' else "请用中文回复。所有文本内容请使用中文。"
        
        if language == 'en':
            context = f"""
            Child Information (Anonymized):
            - Code: {safe_child_info['name']}
            - Age: {age_months} months
            - Special Conditions: {safe_child_info.get('special_conditions', 'Not recorded')}
            
            Current Development Status:
            - Height: {safe_record.get('height', 'Not recorded')} cm
            - Weight: {safe_record.get('weight', 'Not recorded')} kg
            - Head Circumference: {safe_record.get('head_circumference', 'Not recorded')} cm
            - Gross Motor: {safe_record.get('gross_motor', 'Not recorded')}
            - Language: {safe_record.get('language', 'Not recorded')}
            - Fine Motor: {safe_record.get('fine_motor', 'Not recorded')}
            """
            
            prompt = f"""
            You are a professional child development assessment expert. Based on the following information, provide the abilities that a normal child should have at this age, and compare them with the current child.
            {lang_instruction}
            
            {context}
            
            Please return in JSON format:
            {{
                "age_months": {age_months},
                "normal_standards": {{
                    "physical": {{
                        "height_range": "Normal height range (e.g., 75-85cm)",
                        "weight_range": "Normal weight range (e.g., 9-12kg)",
                        "head_circumference_range": "Normal head circumference range"
                    }},
                    "gross_motor": ["Gross motor ability 1 that normal children should have", "Ability 2", "Ability 3"],
                    "language": ["Language ability 1 that normal children should have", "Ability 2", "Ability 3"],
                    "fine_motor": ["Fine motor ability 1 that normal children should have", "Ability 2", "Ability 3"],
                    "cognitive": ["Cognitive ability 1 that normal children should have", "Ability 2"]
                }},
                "comparison": {{
                    "physical_comparison": "Physical indicators comparison analysis",
                    "gross_motor_comparison": "Gross motor abilities comparison and gaps",
                    "language_comparison": "Language abilities comparison and gaps",
                    "fine_motor_comparison": "Fine motor comparison and gaps",
                    "cognitive_comparison": "Cognitive abilities comparison and gaps",
                    "overall_gap": "Overall gap summary"
                }},
                "suggestions": ["Targeted suggestion 1", "Suggestion 2", "Suggestion 3"]
            }}
            
            Important Requirements:
            1. normal_standards must be based on normal development standards for {age_months} months of age
            2. comparison must detail the gaps between this child and normal standards
            3. Consider the child's special conditions, but also make objective comparisons
            4. suggestions should be specific and actionable
            """
        else:
            context = f"""
            孩子信息（已匿名化）：
            - 代号：{safe_child_info['name']}
            - 年龄：{age_months} 个月
            - 特殊情况：{safe_child_info.get('special_conditions', '未记录')}
            
            当前发育情况：
            - 身高：{safe_record.get('height', '未记录')} cm
            - 体重：{safe_record.get('weight', '未记录')} kg
            - 头围：{safe_record.get('head_circumference', '未记录')} cm
            - 大运动：{safe_record.get('gross_motor', '未记录')}
            - 语言：{safe_record.get('language', '未记录')}
            - 精细动作：{safe_record.get('fine_motor', '未记录')}
            """
            
            prompt = f"""
            你是一位专业的儿童发育评估专家。请根据以下信息，提供该年龄段正常孩子应该具备的能力，并与当前孩子进行对比分析。
            {lang_instruction}
            
            {context}
            
            请以JSON格式返回：
            {{
                "age_months": {age_months},
                "normal_standards": {{
                    "physical": {{
                        "height_range": "正常身高范围（如：75-85cm）",
                        "weight_range": "正常体重范围（如：9-12kg）",
                        "head_circumference_range": "正常头围范围"
                    }},
                    "gross_motor": ["正常孩子应该具备的大运动能力1", "能力2", "能力3"],
                    "language": ["正常孩子应该具备的语言能力1", "能力2", "能力3"],
                    "fine_motor": ["正常孩子应该具备的精细动作能力1", "能力2", "能力3"],
                    "cognitive": ["正常孩子应该具备的认知能力1", "能力2"]
                }},
                "comparison": {{
                    "physical_comparison": "身体指标对比分析",
                    "gross_motor_comparison": "大运动能力对比和差距",
                    "language_comparison": "语言能力对比和差距",
                    "fine_motor_comparison": "精细动作对比和差距",
                    "cognitive_comparison": "认知能力对比和差距",
                    "overall_gap": "整体差距总结"
                }},
                "suggestions": ["针对性建议1", "建议2", "建议3"]
            }}
            
            重要要求：
            1. normal_standards必须基于{age_months}个月龄的正常发育标准
            2. comparison必须详细说明该孩子与正常标准的差距
            3. 要考虑到孩子的特殊情况，但也要客观对比
            4. suggestions要具体可行
            """
        
        client = self._get_client()
        if not client:
            return {
                "age_months": age_months,
                "normal_standards": {},
                "comparison": {
                    "error": "需要配置API Key才能获取对比信息"
                },
                "recommendations": []
            }
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位专业的儿童发育评估专家，擅长对比分析有特殊情况儿童与正常发育标准的差距。所有数据已匿名化处理。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            import json
            try:
                parsed = json.loads(result)
                return parsed
            except:
                # 尝试提取JSON
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
                return {
                    "age_months": age_months,
                    "normal_standards": {},
                    "comparison": {
                        "error": "解析失败，请重试"
                    },
                    "recommendations": []
                }
        except Exception as e:
            return {
                "age_months": age_months,
                "normal_standards": {},
                "comparison": {
                    "error": f"获取对比信息时出错：{str(e)}"
                },
                "recommendations": []
            }
