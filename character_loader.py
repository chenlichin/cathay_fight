#!/usr/bin/env python3
"""
角色配置載入器
Character Configuration Loader
"""

import csv
import os
from typing import Dict, List, Optional

class CharacterLoader:
    """角色配置載入器"""
    
    def __init__(self, config_dir: str = "assets"):
        self.config_dir = config_dir
        self.characters = {}
        self.skills = {}
        self.skill_type_mapping = {}
        self.action_display_mapping = {}
        self.load_characters()
        self.load_skills()
        self.build_mappings()
    
    def load_characters(self):
        """載入角色配置"""
        config_file = os.path.join(self.config_dir, "characters_config.csv")
        
        if not os.path.exists(config_file):
            print(f"⚠️  角色配置檔案不存在: {config_file}")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    char_id = int(row['id'])
                    self.characters[char_id] = {
                        'id': char_id,
                        'code': row['code'],
                        'display_name': row['display_name'],
                        'style': row['style'],
                        'description': row['description'],
                        'atk': int(row['atk']),
                        'def': int(row['def']),
                        'hp': int(row['hp']),
                        'icon_path': row['icon_path'],
                        'sprite_path': row['sprite_path'],
                        # 新增可選的預覽大圖欄位（向後相容）
                        'preview_path': row.get('preview_path', row.get('PreviewImage', row['icon_path']))
                    }
            
            print(f"✅ 載入 {len(self.characters)} 個角色")
            
        except Exception as e:
            print(f"❌ 載入角色配置失敗: {e}")
    
    def load_skills(self):
        """載入技能配置"""
        skills_file = os.path.join(self.config_dir, "character_skills.csv")
        
        if not os.path.exists(skills_file):
            print(f"⚠️  技能配置檔案不存在: {skills_file}")
            return
        
        try:
            with open(skills_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    char_id = int(row['character_id'])
                    skill_id = int(row['skill_id'])
                    
                    if char_id not in self.skills:
                        self.skills[char_id] = []
                    
                    self.skills[char_id].append({
                        'id': skill_id,
                        'name': row['skill_name'],
                        'type': row['skill_type'],
                        'damage': int(row['damage']),
                        'cooldown': int(row['cooldown']),
                        'description': row['description']
                    })
            
            print(f"✅ 載入 {sum(len(skills) for skills in self.skills.values())} 個技能")
            
        except Exception as e:
            print(f"❌ 載入技能配置失敗: {e}")
    
    def build_mappings(self):
        """建立技能映射和動作顯示名稱"""
        # 技能類型映射
        self.skill_type_mapping = {
            "ATTACK1": "attack1",
            "ATTACK2": "attack2", 
            "ATTACK3": "attack3",
            "DASH_ATTACK": "attack1",  # 使用 attack1 的傷害
            "COUNTER_ATTACK": "attack2"  # 使用 attack2 的傷害
        }
        
        # 動作顯示名稱映射
        self.action_display_mapping = {
            # 技能動作（從 CSV 動態讀取）
            "ATTACK1": None,  # 將在 get_action_display_name 中動態獲取
            "ATTACK2": None,
            "ATTACK3": None,
            "DASH_ATTACK": None,
            "COUNTER_ATTACK": None,
            
            # 非技能動作（保持英文）
            "MOVE_CLOSER": "MOVE_CLOSER",
            "MOVE_AWAY": "MOVE_AWAY",
            "JUMP": "JUMP",
            "JUMP_BEHIND": "JUMP_BEHIND",
            "MOVE_AND_JUMP": "MOVE_AND_JUMP",
            "FALL": "FALL"
        }
    
    def get_skill_by_type(self, char_id: int, skill_type: str) -> Optional[Dict]:
        """根據技能類型獲取技能資訊"""
        if char_id not in self.skills:
            return None
        
        for skill in self.skills[char_id]:
            if skill['type'] == skill_type:
                return skill
        return None
    
    def get_action_display_name(self, action: str, char_id: int = None) -> str:
        """獲取動作的顯示名稱"""
        # 如果是技能動作且有角色ID，從 CSV 讀取
        if action in ["ATTACK1", "ATTACK2", "ATTACK3", "DASH_ATTACK", "COUNTER_ATTACK"] and char_id:
            skill_type = self.skill_type_mapping.get(action)
            if skill_type:
                skill = self.get_skill_by_type(char_id, skill_type)
                if skill:
                    return skill['name']
        
        # 否則使用預設映射
        return self.action_display_mapping.get(action, action)
    
    def calculate_damage(self, char_id: int, action: str, target_def: int = 0, combo_count: int = 0) -> int:
        """計算傷害值（包含防禦力計算）"""
        # 獲取角色基礎攻擊力
        char = self.get_character(char_id)
        if not char:
            return 10  # 預設傷害
        
        base_atk = char['atk']
        
        # 獲取技能傷害
        skill_type = self.skill_type_mapping.get(action)
        skill_damage = 0
        if skill_type:
            skill = self.get_skill_by_type(char_id, skill_type)
            if skill:
                skill_damage = skill['damage']
        
        # 連擊加成（每連擊增加 5% 傷害）
        combo_bonus = int((base_atk + skill_damage) * 0.05 * combo_count)
        
        # 原始傷害 = 基礎攻擊力 + 技能傷害 + 連擊加成
        raw_damage = base_atk + skill_damage + combo_bonus
        
        # 防禦力直接減傷（簡化計算）
        # 防禦力 = 直接減傷值，但最多減傷 80%
        defense_reduction = min(target_def, raw_damage * 0.8)
        final_damage = max(1, raw_damage - defense_reduction)
        
        return int(final_damage)  # 確保最小傷害為 1
    
    def get_character(self, char_id: int) -> Optional[Dict]:
        """獲取角色資訊"""
        return self.characters.get(char_id)
    
    def get_character_skills(self, char_id: int) -> List[Dict]:
        """獲取角色技能"""
        return self.skills.get(char_id, [])
    
    def get_all_characters(self) -> Dict[int, Dict]:
        """獲取所有角色"""
        return self.characters.copy()
    
    def get_character_by_code(self, code: str) -> Optional[Dict]:
        """根據代號獲取角色"""
        for char in self.characters.values():
            if char['code'] == code:
                return char
        return None
    
    def get_characters_by_style(self, style: str) -> List[Dict]:
        """根據風格獲取角色"""
        return [char for char in self.characters.values() if char['style'] == style]
    
    def get_character_summary(self, char_id: int) -> Optional[Dict]:
        """獲取角色摘要資訊（包含技能）"""
        char = self.get_character(char_id)
        if not char:
            return None
        
        char_skills = self.get_character_skills(char_id)
        
        return {
            **char,
            'skills': char_skills,
            'total_stats': char['atk'] + char['def']
        }
    
    def validate_config(self) -> bool:
        """驗證配置完整性"""
        errors = []
        
        # 檢查角色配置
        for char_id, char in self.characters.items():
            # 檢查屬性範圍
            for attr in ['atk', 'def']:
                if not (1 <= char[attr] <= 100):
                    errors.append(f"角色 {char['code']} 的 {attr} 超出範圍: {char[attr]}")
            
            # 檢查HP範圍
            if not (100 <= char['hp'] <= 3000):
                errors.append(f"角色 {char['code']} 的 HP 超出範圍: {char['hp']}")
            
            # 檢查技能是否存在
            if char_id not in self.skills:
                errors.append(f"角色 {char['code']} 沒有技能配置")
        
        # 檢查技能配置
        for char_id in self.skills:
            if char_id not in self.characters:
                errors.append(f"技能配置中有未知的角色ID: {char_id}")
        
        if errors:
            print("❌ 配置驗證失敗:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("✅ 配置驗證通過")
        return True

# 全域角色載入器實例
character_loader = CharacterLoader()

# 測試函數
def test_character_loader():
    """測試角色載入器"""
    print("🧪 測試角色載入器...")
    
    # 獲取所有角色
    all_chars = character_loader.get_all_characters()
    print(f"載入的角色數量: {len(all_chars)}")
    
    # 獲取特定角色
    kate = character_loader.get_character_by_code("kate")
    if kate:
        print(f"凱特資訊: {kate['display_name']} - {kate['style']}")
        
        # 獲取技能
        skills = character_loader.get_character_skills(kate['id'])
        print(f"技能數量: {len(skills)}")
        
        # 測試動作顯示名稱
        print("\n動作顯示名稱測試:")
        for action in ["ATTACK1", "ATTACK2", "ATTACK3", "MOVE_CLOSER", "JUMP"]:
            display_name = character_loader.get_action_display_name(action, kate['id'])
            print(f"  {action} -> {display_name}")
        
        # 測試傷害計算
        print("\n傷害計算測試:")
        for action in ["ATTACK1", "ATTACK2", "ATTACK3"]:
            # 測試不同防禦力的傷害
            damage_no_def = character_loader.calculate_damage(kate['id'], action, 0)
            damage_low_def = character_loader.calculate_damage(kate['id'], action, 20)
            damage_high_def = character_loader.calculate_damage(kate['id'], action, 50)
            print(f"  {action} 傷害:")
            print(f"    無防禦: {damage_no_def}")
            print(f"    防禦20: {damage_low_def} (減傷20)")
            print(f"    防禦50: {damage_high_def} (減傷50)")
        
        # 獲取摘要
        summary = character_loader.get_character_summary(kate['id'])
        print(f"總屬性點數: {summary['total_stats']}")
    
    # 驗證配置
    character_loader.validate_config()

if __name__ == "__main__":
    test_character_loader()
