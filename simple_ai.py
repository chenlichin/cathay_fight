import random
import time
from game_actions import VALID_ACTIONS

class SimpleAI:
    """簡化的 AI 模擬器，用於替代 Hugging Face 模型"""
    
    def __init__(self, strategy="defensive"):
        self.strategy = strategy
        self.last_call_time = 0
        
    def generate_actions(self, game_context):
        """根據策略生成動作列表"""
        # 模擬思考時間
        
        actions = []
        
        if self.strategy == "defensive":
            # 防禦型策略：更多移動和迴避
            action_pool = [action for action in VALID_ACTIONS if action in ["MOVE_AWAY", "JUMP", "JUMP_BEHIND", "MOVE_AND_JUMP", "ATTACK1", "ATTACK2", "COUNTER_ATTACK"]]
        else:
            # 攻擊型策略：更多攻擊動作
            action_pool = [action for action in VALID_ACTIONS if action in ["ATTACK1", "ATTACK2", "ATTACK3", "MOVE_CLOSER", "JUMP", "JUMP_BEHIND", "MOVE_AND_JUMP", "DASH_ATTACK"]]
        
        # 根據遊戲狀態調整策略
        if "far" in game_context.lower():
            # 距離遠時多移動
            actions.extend([action for action in VALID_ACTIONS if action == "MOVE_CLOSER"] * 4)
        elif "close" in game_context.lower():
            # 距離近時多攻擊
            actions.extend([action for action in VALID_ACTIONS if action in ["ATTACK1", "ATTACK2", "ATTACK3"]] * 2)
        
        # 隨機選擇 6-8 個動作
        num_actions = random.randint(6, 8)
        for _ in range(num_actions):
            actions.append(random.choice(action_pool))
        
        return actions

class MockLLMPipeline:
    """模擬 LLM Pipeline"""
    
    def __init__(self, strategy="defensive"):
        self.ai = SimpleAI(strategy)
    
    def __call__(self, prompt, max_new_tokens=50):
        """模擬 LLM 調用"""
        # 從 prompt 中提取遊戲狀態
        game_context = prompt
        
        # 生成動作
        actions = self.ai.generate_actions(game_context)
        
        # 格式化輸出，模擬 LLM 的回應格式
        response_text = "\n".join([f"- {action}" for action in actions])
        
        return [{"generated_text": prompt + response_text}]

