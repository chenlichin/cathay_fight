#!/usr/bin/env python3
"""
AWS Bedrock 整合模組
提供與 Amazon Bedrock 服務的整合功能
"""

import os
import json
import asyncio
import boto3
from typing import List, Optional, Dict, Any
from game_actions import VALID_ACTIONS

# 嘗試載入 .env 檔案
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 已載入 .env 檔案")
except ImportError:
    print("⚠️  python-dotenv 未安裝，無法載入 .env 檔案")

class BedrockClient:
    """AWS Bedrock 客戶端"""
    
    def __init__(self):
        self.clients = {}  # 不同 region 的客戶端快取
        self.models = {
            "amazon.nova-micro-v1:0": {
                "name": "Amazon Nova Micro",
                "power_level": "強度: 2/5",
                "description": "輕量級模型，快速回應",
                "strategy": "aggressive",
                "region": "us-east-1"
            },
            "amazon.nova-lite-v1:0": {
                "name": "Amazon Nova Lite",
                "power_level": "強度: 3/5",
                "description": "平衡型模型，攻防兼備",
                "strategy": "balanced",
                "region": "us-east-1"
            },
            "amazon.nova-pro-v1:0": {
                "name": "Amazon Nova Pro",
                "power_level": "強度: 4/5",
                "description": "高級模型，智能策略",
                "strategy": "defensive",
                "region": "us-east-1"
            },
            "anthropic.claude-3-haiku-20240307-v1:0": {
                "name": "Claude 3 Haiku", 
                "power_level": "強度: 5/5",
                "description": "最強模型，全能型策略",
                "strategy": "balanced",
                "region": "us-east-1"
            }
        }
        
        # 檢查環境變數
        self.check_aws_credentials()
    
    def check_aws_credentials(self):
        """檢查 AWS 認證"""
        required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"⚠️  缺少 AWS 環境變數: {', '.join(missing_vars)}")
            print("💡 請設定環境變數後重新啟動遊戲")
            self.available = False
        else:
            print("✅ AWS 認證檢查通過")
            self.available = True
    
    def get_client(self, region: str):
        """獲取指定 region 的 Bedrock 客戶端"""
        if region not in self.clients:
            try:
                self.clients[region] = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=region
                )
                print(f"✅ 已連接到 AWS Bedrock ({region})")
            except Exception as e:
                print(f"❌ 無法連接到 AWS Bedrock ({region}): {e}")
                return None
        return self.clients[region]
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """獲取可用的模型列表"""
        return self.models
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """獲取特定模型的資訊"""
        return self.models.get(model_id)
    
    async def invoke_model(self, model_id: str, system_prompt: str, context_prompt: str, player: int) -> Optional[tuple[List[str], str, bool]]:
        """
        呼叫 Bedrock 模型
        
        Args:
            model_id: 模型 ID
            system_prompt: 系統提示詞
            context_prompt: 遊戲上下文提示詞
            player: 玩家編號
            
        Returns:
            (動作列表, 戰術分析, 是否清空佇列) 或 None（如果失敗）
        """
        if not self.available:
            print("❌ AWS Bedrock 不可用")
            return None
        
        model_info = self.get_model_info(model_id)
        if not model_info:
            print(f"❌ 未知模型: {model_id}")
            return None
        
        region = model_info["region"]
        client = self.get_client(region)
        if not client:
            return None
        
        try:
            # 構建完整的提示詞，要求戰術分析
            full_prompt = f"""{system_prompt}

{context_prompt}

請分析當前戰況並提供戰術建議，然後生成動作序列。

戰術分析格式：
[戰術分析] 簡短描述你的戰術思路和策略

動作序列格式：
[動作] 動作1
[動作] 動作2
[動作] 動作3
[動作] 動作4
[動作] 動作5
[動作] 動作6

可用的動作：MOVE_CLOSER, MOVE_AWAY, ATTACK1, ATTACK2, ATTACK3, JUMP, JUMP_BEHIND, MOVE_AND_JUMP, DASH_ATTACK, COUNTER_ATTACK, FALL

請確保戰術分析簡潔明瞭，動作序列準確。"""
            
            # 構建 Bedrock 請求
            if "claude" in model_id:
                # Claude 模型使用 messages 格式
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 100,
                    "messages": [
                        {
                            "role": "user",
                            "content": full_prompt
                        }
                    ]
                }
            elif "amazon.nova" in model_id:
                # Amazon Nova 模型使用正確的 content 陣列格式
                request_body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": full_prompt}]
                        }
                    ]
                }
            else:
                # 其他模型的通用格式
                request_body = {
                    "prompt": full_prompt,
                    "max_tokens": 100,
                    "temperature": 0.7
                }
            
            # 非同步呼叫 Bedrock
            response = await asyncio.to_thread(
                client.invoke_model,
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            # 解析回應
            response_body = json.loads(response.get('body').read())
            
            if "claude" in model_id:
                # Claude 模型回應格式
                content = response_body.get("content", [])
                if content and len(content) > 0:
                    response_text = content[0].get("text", "")
                else:
                    response_text = ""
            elif "amazon.nova" in model_id:
                # Amazon Nova 模型回應格式
                output = response_body.get("output", {})
                message = output.get("message", {})
                content = message.get("content", [])
                if content and len(content) > 0:
                    response_text = content[0].get("text", "")
                else:
                    response_text = ""
            else:
                # 其他模型回應格式
                response_text = response_body.get("completion", "")
            
            print(f"🤖 {model_info['name']} 回應:")
            print(response_text)
            
            # 解析動作和戰術分析
            actions, tactical_analysis, clear_queue = self.parse_actions(response_text)
            if actions:
                print(f"✅ 成功解析 {len(actions)} 個動作")
                print(f"🎯 戰術分析: {tactical_analysis}")
                return actions, tactical_analysis, clear_queue
            else:
                print("❌ 無法解析動作，使用預設動作")
                default_actions = self.get_default_actions(model_info["strategy"])
                return default_actions, f"使用預設{model_info['strategy']}策略", False
                
        except Exception as e:
            print(f"❌ Bedrock API 呼叫失敗: {e}")
            return None
    
    async def invoke_tactical_analysis(self, model_id: str, tactical_prompt: str, player: int) -> Optional[str]:
        """
        專門用於戰術分析的 API 呼叫
        
        Args:
            model_id: 模型 ID
            tactical_prompt: 戰術分析提示詞
            player: 玩家編號
            
        Returns:
            戰術分析文字或 None（如果失敗）
        """
        if not self.available:
            print("❌ AWS Bedrock 不可用")
            return None
        
        model_info = self.get_model_info(model_id)
        if not model_info:
            print(f"❌ 未知模型: {model_id}")
            return None
        
        region = model_info["region"]
        client = self.get_client(region)
        if not client:
            return None
        
        try:
            # 構建 Bedrock 請求
            if "claude" in model_id:
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 150,
                    "messages": [
                        {
                            "role": "user",
                            "content": tactical_prompt
                        }
                    ]
                }
            elif "amazon.nova" in model_id:
                request_body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": tactical_prompt}]
                        }
                    ]
                }
            else:
                request_body = {
                    "prompt": tactical_prompt,
                    "max_tokens": 150,
                    "temperature": 0.7
                }
            
            # 非同步呼叫 Bedrock
            response = await asyncio.to_thread(
                client.invoke_model,
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            # 解析回應
            response_body = json.loads(response.get('body').read())
            
            if "claude" in model_id:
                content = response_body.get("content", [])
                if content and len(content) > 0:
                    response_text = content[0].get("text", "")
                else:
                    response_text = ""
            elif "amazon.nova" in model_id:
                output = response_body.get("output", {})
                message = output.get("message", {})
                content = message.get("content", [])
                if content and len(content) > 0:
                    response_text = content[0].get("text", "")
                else:
                    response_text = ""
            else:
                response_text = response_body.get("completion", "")
            
            print(f"🎯 {model_info['name']} 戰術分析:")
            print(response_text)
            
            # 解析戰術分析
            tactical_analysis = self.parse_tactical_analysis(response_text)
            if tactical_analysis:
                print(f"✅ 成功解析戰術分析: {tactical_analysis}")
                return tactical_analysis
            else:
                print("❌ 無法解析戰術分析，使用預設")
                return f"使用預設{model_info['strategy']}策略"
                
        except Exception as e:
            print(f"❌ 戰術分析 API 呼叫失敗: {e}")
            return None
    
    def parse_tactical_analysis(self, response_text: str) -> Optional[str]:
        """解析戰術分析"""
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if "[戰術分析]" in line:
                tactical_analysis = line.replace("[戰術分析]", "").strip()
                return tactical_analysis
        
        # 如果沒有找到標記，嘗試提取戰術相關內容
        for line in lines:
            if any(keyword in line.lower() for keyword in ["戰術", "策略", "分析", "思路", "計劃", "策略"]):
                return line.strip()
        
        return None
    
    def parse_actions(self, response_text: str) -> tuple[List[str], str, bool]:
        """解析模型回應中的動作、戰術分析與是否清空佇列指令"""
        valid_actions = VALID_ACTIONS
        actions = []
        tactical_analysis = ""
        clear_queue = False
        
        # 按行分割並清理
        lines = response_text.strip().split('\n')
        print(f"🔍 解析回應，共 {len(lines)} 行")
        
        for line in lines:
            line = line.strip()
            
            # 檢查戰術分析
            if "[戰術分析]" in line:
                tactical_analysis = line.replace("[戰術分析]", "").strip()
                print(f"📝 找到戰術分析: {tactical_analysis}")
                continue
                
            # 檢查清空指令
            if "[CLEAR_QUEUE]" in line or "[清空]" in line or "[清空佇列]" in line:
                clear_queue = True
                print("🧹 指令: 清空佇列")
                continue

            # 檢查動作
            action = None
            if "[動作]" in line:
                action = line.replace("[動作]", "").strip().upper()
            elif line.startswith("-") or line.startswith("•") or line.startswith("*"):
                # 允許無標記的子彈條列
                action = line[1:].strip().upper()
            if action is not None:
                # 移除可能的編號和符號
                action = action.replace('-', '').replace('•', '').replace('*', '')
                action = action.strip()
                
                print(f"🎯 解析動作: '{action}' (原始: '{line}')")
                
                if action in valid_actions:
                    actions.append(action)
                    print(f"✅ 動作有效: {action}")
                else:
                    print(f"❌ 動作無效: {action} (不在 {valid_actions} 中)")
        
        # 如果沒有找到戰術分析標記，嘗試從回應中提取
        if not tactical_analysis:
            print("🔍 未找到戰術分析標記，嘗試提取...")
            # 尋找可能的戰術描述
            for line in lines:
                if any(keyword in line.lower() for keyword in ["戰術", "策略", "分析", "思路", "計劃"]):
                    tactical_analysis = line.strip()
                    print(f"📝 提取到戰術分析: {tactical_analysis}")
                    break
        
        print(f"📊 解析結果: {len(actions)} 個動作, 戰術分析: {tactical_analysis}, 清空佇列: {clear_queue}")
        return actions[:8], tactical_analysis, clear_queue  # 最多8個動作
    
    def get_default_actions(self, strategy: str) -> List[str]:
        """根據策略獲取預設動作"""
        if strategy == "defensive":
            return ["MOVE_AWAY", "JUMP", "ATTACK1", "MOVE_AWAY", "JUMP", "ATTACK2"]
        elif strategy == "aggressive":
            return ["MOVE_CLOSER", "ATTACK1", "ATTACK2", "MOVE_CLOSER", "ATTACK1", "JUMP"]
        else:  # balanced
            return ["MOVE_CLOSER", "ATTACK1", "JUMP", "ATTACK2", "MOVE_AWAY", "ATTACK1"]

# 全域實例
bedrock_client = BedrockClient()
