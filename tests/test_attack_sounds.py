#!/usr/bin/env python3
"""
攻擊音效測試工具
測試攻擊音效是否正常播放
"""

import pygame
import time
from audio_manager import audio_manager, SOUND_EFFECTS

def test_attack_sounds():
    """測試攻擊音效播放"""
    print("⚔️ 測試攻擊音效播放...")
    
    # 初始化 Pygame
    pygame.init()
    
    try:
        # 測試第一種攻擊音效
        print("播放第一種攻擊音效 (HIGH_ATTACK)...")
        audio_manager.play_sound(SOUND_EFFECTS["attack1_hit"])
        time.sleep(1)
        
        # 測試第二種攻擊音效
        print("播放第二種攻擊音效 (LOW_ATTACK)...")
        audio_manager.play_sound(SOUND_EFFECTS["attack2_skill"])
        time.sleep(1)
        
        # 測試快速連續播放
        print("測試快速連續播放...")
        for i in range(3):
            print(f"  第 {i+1} 次攻擊音效...")
            audio_manager.play_sound(SOUND_EFFECTS["attack1_hit"])
            time.sleep(0.3)
        
        print("✅ 攻擊音效測試完成")
        
    except Exception as e:
        print(f"❌ 攻擊音效測試失敗: {e}")
    
    finally:
        pygame.quit()

def test_audio_status():
    """測試音效系統狀態"""
    print("\n📊 測試音效系統狀態...")
    
    try:
        status = audio_manager.get_status()
        print(f"音效系統狀態:")
        print(f"  - 音效開關: {status['sfx_enabled']}")
        print(f"  - 音樂開關: {status['music_enabled']}")
        print(f"  - 音效音量: {status['sfx_volume']}")
        print(f"  - 音樂音量: {status['music_volume']}")
        print(f"  - 快取音效數量: {status['sound_cache_count']}")
        
        print("✅ 音效系統狀態檢查完成")
        
    except Exception as e:
        print(f"❌ 狀態檢查失敗: {e}")

def test_sound_files():
    """測試音效檔案是否存在"""
    print("\n📁 測試音效檔案...")
    
    try:
        import os
        
        # 檢查攻擊音效檔案
        attack1_file = "assets/music/" + SOUND_EFFECTS["attack1_hit"]
        attack2_file = "assets/music/" + SOUND_EFFECTS["attack2_skill"]
        
        if os.path.exists(attack1_file):
            print(f"✅ {SOUND_EFFECTS['attack1_hit']} 檔案存在")
        else:
            print(f"❌ {SOUND_EFFECTS['attack1_hit']} 檔案不存在")
            
        if os.path.exists(attack2_file):
            print(f"✅ {SOUND_EFFECTS['attack2_skill']} 檔案存在")
        else:
            print(f"❌ {SOUND_EFFECTS['attack2_skill']} 檔案不存在")
        
        print("✅ 音效檔案檢查完成")
        
    except Exception as e:
        print(f"❌ 音效檔案檢查失敗: {e}")

def main():
    print("🧪 攻擊音效測試工具")
    print("=" * 50)
    
    try:
        # 測試音效系統狀態
        test_audio_status()
        
        # 測試音效檔案
        test_sound_files()
        
        # 測試攻擊音效播放
        test_attack_sounds()
        
        print("\n🎉 所有測試完成！")
        print("💡 如果攻擊音效正常播放，說明音效系統工作正常")
        print("💡 如果沒有音效，請檢查：")
        print("  1. 音效檔案是否存在")
        print("  2. 音效檔案是否損壞")
        print("  3. 系統音量設定")
        print("  4. 音效系統是否初始化成功")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()
