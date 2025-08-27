#!/usr/bin/env python3
"""
遊戲動作定義
統一管理所有可用的遊戲動作
"""

# 所有可用的遊戲動作（對應實際的圖片檔案）
VALID_ACTIONS = [
    "MOVE_CLOSER",    # 向目標移動 (Run.png)
    "MOVE_AWAY",      # 遠離目標 (Run.png)
    "ATTACK1",        # 攻擊1 (Attack1.png)
    "ATTACK2",        # 攻擊2 (Attack2.png)
    "ATTACK3",        # 攻擊3 (Attack3.png)
    "JUMP",           # 跳躍 (Jump.png)
    "JUMP_BEHIND",    # 迴避跳躍 (Jump.png)
    "MOVE_AND_JUMP",  # 移動+跳躍 (Run.png + Jump.png)
    "DASH_ATTACK",    # 衝刺攻擊 (Run.png + Attack1.png)
    "COUNTER_ATTACK", # 反擊 (Attack2.png)
    "FALL"            # 跌倒 (Fall.png)
]

# 動作類型分類
MOVEMENT_ACTIONS = ["MOVE_CLOSER", "MOVE_AWAY", "JUMP", "JUMP_BEHIND", "MOVE_AND_JUMP", "FALL"]
ATTACK_ACTIONS = ["ATTACK1", "ATTACK2", "ATTACK3", "DASH_ATTACK", "COUNTER_ATTACK"]
COMPOUND_ACTIONS = ["MOVE_AND_JUMP", "DASH_ATTACK", "COUNTER_ATTACK"]

# 動作描述
ACTION_DESCRIPTIONS = {
    "MOVE_CLOSER": "向對手移動",
    "MOVE_AWAY": "遠離對手",
    "ATTACK1": "攻擊1（高攻擊）",
    "ATTACK2": "攻擊2（中攻擊）",
    "ATTACK3": "攻擊3（低攻擊）",
    "JUMP": "跳躍",
    "JUMP_BEHIND": "迴避跳躍",
    "MOVE_AND_JUMP": "移動+跳躍",
    "DASH_ATTACK": "衝刺攻擊",
    "COUNTER_ATTACK": "反擊",
    "FALL": "跌倒"
}

# 動作對應的動畫索引（對應 WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 7, 9]）
# 注意：由於精靈表限制，ATTACK3 和 FALL 使用現有動畫
ACTION_ANIMATION_INDEX = {
    "MOVE_CLOSER": 1,  # 1:run (Run.png)
    "MOVE_AWAY": 1,    # 1:run (Run.png)
    "JUMP": 2,         # 2:jump (Jump.png)
    "JUMP_BEHIND": 2,  # 2:jump (Jump.png)
    "MOVE_AND_JUMP": 2, # 2:jump (Jump.png) - 複合動作使用跳躍動畫
    "ATTACK1": 3,      # 3:attack1 (Attack1.png)
    "ATTACK2": 4,      # 4:attack2 (Attack2.png)
    "ATTACK3": 3,      # 3:attack1 (使用 Attack1 動畫)
    "DASH_ATTACK": 3,  # 3:attack1 (Attack1.png) - 複合動作使用攻擊動畫
    "COUNTER_ATTACK": 4, # 4:attack2 (Attack2.png) - 複合動作使用攻擊2動畫
    "FALL": 2          # 2:jump (使用 Jump 動畫)
}

def is_valid_action(action):
    """檢查動作是否有效"""
    return action in VALID_ACTIONS

def get_action_description(action):
    """獲取動作描述"""
    return ACTION_DESCRIPTIONS.get(action, "未知動作")

def get_animation_index(action):
    """獲取動作對應的動畫索引"""
    return ACTION_ANIMATION_INDEX.get(action, 0)  # 預設為 idle (0)

def get_movement_actions():
    """獲取移動類動作"""
    return MOVEMENT_ACTIONS.copy()

def get_attack_actions():
    """獲取攻擊類動作"""
    return ATTACK_ACTIONS.copy()
