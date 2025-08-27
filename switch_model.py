#!/usr/bin/env python3
"""
模型切換工具
讓您可以輕鬆切換不同的 LLM 模型
"""

import sys
import os
from model_config import AVAILABLE_MODELS, list_available_models

def main():
    print("🤖 LLM 模型切換工具")
    print("=" * 50)
    
    # 顯示可用模型
    list_available_models()
    
    # 讀取當前設定
    try:
        with open("model_config.py", "r", encoding="utf-8") as f:
            content = f.read()
            for line in content.split("\n"):
                if line.strip().startswith("DEFAULT_MODEL ="):
                    current_model = line.split("=")[1].strip().strip('"\'')
                    print(f"🔧 當前預設模型: {current_model}")
                    break
    except:
        print("❌ 無法讀取當前模型設定")
        return
    
    # 讓使用者選擇模型
    print("\n請選擇要使用的模型：")
    print("0. 保持當前模型")
    
    models = list(AVAILABLE_MODELS.keys())
    for i, model_id in enumerate(models, 1):
        info = AVAILABLE_MODELS[model_id]
        print(f"{i}. {model_id} ({info['name']}) - {info['size']}")
    
    try:
        choice = input("\n請輸入選項編號 (0-{}): ".format(len(models)))
        choice = int(choice)
        
        if choice == 0:
            print("✅ 保持當前模型設定")
            return
        
        if 1 <= choice <= len(models):
            selected_model = models[choice - 1]
            print(f"✅ 選擇模型: {selected_model}")
            
            # 更新設定檔案
            update_model_config(selected_model)
            print(f"✅ 已更新預設模型為: {selected_model}")
            print("💡 重新啟動遊戲以使用新模型")
        else:
            print("❌ 無效的選項")
            
    except ValueError:
        print("❌ 請輸入有效的數字")
    except KeyboardInterrupt:
        print("\n👋 取消操作")

def update_model_config(new_model):
    """更新模型配置檔案"""
    try:
        with open("model_config.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 替換預設模型
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("DEFAULT_MODEL ="):
                lines[i] = f'DEFAULT_MODEL = "{new_model}"'
                break
        
        # 寫回檔案
        with open("model_config.py", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
    except Exception as e:
        print(f"❌ 更新設定檔案失敗: {e}")

if __name__ == "__main__":
    main() 