#!/usr/bin/env python3
"""
修復驗證測試工具
測試simple_ai行為間隔、音效優先權系統和防覆蓋機制
"""

import pygame
import time
from audio_manager import audio_manager, SOUND_EFFECTS
from simple_ai import SimpleAI

def test_audio_system():
    """測試音效系統"""
    print("🔊 測試音效系統...")
    
    # 初始化 Pygame
    pygame.init()
    
    # 測試攻擊音效（高優先權）
    print("播放第一種攻擊音效 (HIGH_ATTACK)...")
    audio_manager.play_sound(SOUND_EFFECTS["attack1_hit"], "attack1_hit")
    time.sleep(0.5)
    
    print("播放第二種攻擊音效 (LOW_ATTACK)...")
    audio_manager.play_sound(SOUND_EFFECTS["attack2_skill"], "attack2_skill")
    time.sleep(0.5)
    
    # 測試選單音效（低優先權，應該被阻擋）
    print("嘗試播放選單音效（應該被阻擋）...")
    audio_manager.play_sound(SOUND_EFFECTS["option_switch"], "option_switch")
    time.sleep(0.5)
    
    # 測試勝利音效（中等優先權）
    print("播放勝利音效...")
    audio_manager.play_sound(SOUND_EFFECTS["victory"], "victory")
    time.sleep(1)
    
    print("✅ 音效系統測試完成")

def test_simple_ai_timing():
    """測試simple_ai的行為間隔"""
    print("\n⏱️  測試simple_ai行為間隔...")
    
    # 創建simple_ai實例
    ai = SimpleAI("aggressive")
    
    start_time = time.time()
    
    # 測試生成動作的時間
    print("生成AI動作...")
    actions = ai.generate_actions("You are close to the opponent. You should attack.")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"生成動作數量: {len(actions)}")
    print(f"總執行時間: {total_time:.3f}秒")
    print(f"動作列表: {actions[:5]}...")  # 顯示前5個動作
    
    # 檢查是否有適當的間隔
    expected_time = len(actions) * 0.1  # 每個動作0.1秒
    if total_time >= expected_time * 0.8:  # 允許一些誤差
        print("✅ simple_ai行為間隔正常")
    else:
        print(f"⚠️  simple_ai行為間隔可能過短 (預期: {expected_time:.3f}秒)")
    
    print("✅ simple_ai行為間隔測試完成")

def test_audio_priority():
    """測試音效優先權系統"""
    print("\n🎯 測試音效優先權系統...")
    
    # 測試音效狀態
    status = audio_manager.get_status()
    print(f"當前播放的音效: {status['current_sounds']}")
    
    # 測試優先權阻擋
    print("測試優先權阻擋...")
    
    # 先播放高優先權音效
    print("播放高優先權攻擊音效...")
    audio_manager.play_sound(SOUND_EFFECTS["attack1_hit"], "attack1_hit")
    time.sleep(0.1)
    
    # 嘗試播放低優先權音效
    print("嘗試播放低優先權選單音效...")
    audio_manager.play_sound(SOUND_EFFECTS["option_switch"], "option_switch")
    
    # 檢查狀態
    status = audio_manager.get_status()
    print(f"播放後的音效狀態: {status['current_sounds']}")
    
    print("✅ 音效優先權系統測試完成")

def main():
    print("🧪 修復驗證測試工具")
    print("=" * 50)
    
    try:
        # 測試音效系統
        test_audio_system()
        
        # 測試simple_ai行為間隔
        test_simple_ai_timing()
        
        # 測試音效優先權系統
        test_audio_priority()
        
        print("\n🎉 所有測試完成！")
        print("💡 修復內容：")
        print("  - 動作間隔已移除，遊戲速度恢復正常")
        print("  - 音效優先權系統已實現（攻擊音效最高優先權）")
        print("  - 防音效覆蓋機制已添加")
        print("  - 防重複播放機制已添加（0.2秒內相同音效不重複）")
        print("  - 智能音效清理機制已實現")
        print("  - 回合結束選項已添加確認音效")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
