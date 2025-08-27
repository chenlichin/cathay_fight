#!/usr/bin/env python3
"""
簡單音效測試工具
測試音效系統是否正常工作
"""

import pygame
import time
from audio_manager import audio_manager, SOUND_EFFECTS

def test_basic_audio():
    """測試基本音效播放"""
    print("🔊 測試基本音效播放...")
    
    # 初始化 Pygame
    pygame.init()
    
    try:
        # 測試攻擊音效
        print("播放第一種攻擊音效...")
        audio_manager.play_sound(SOUND_EFFECTS["attack1_hit"])
        time.sleep(1)
        
        print("播放第二種攻擊音效...")
        audio_manager.play_sound(SOUND_EFFECTS["attack2_skill"])
        time.sleep(1)
        
        # 測試選單音效
        print("播放選項切換音效...")
        audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
        time.sleep(1)
        
        print("播放選項確認音效...")
        audio_manager.play_sound(SOUND_EFFECTS["option_confirmed"])
        time.sleep(1)
        
        # 測試勝利音效
        print("播放勝利音效...")
        audio_manager.play_sound(SOUND_EFFECTS["victory"])
        time.sleep(2)
        
        print("✅ 基本音效測試完成")
        
    except Exception as e:
        print(f"❌ 音效測試失敗: {e}")
    
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

def main():
    print("🧪 簡單音效測試工具")
    print("=" * 50)
    
    try:
        # 測試音效系統狀態
        test_audio_status()
        
        # 測試基本音效播放
        test_basic_audio()
        
        print("\n🎉 所有測試完成！")
        print("💡 如果音效正常播放，說明音效系統工作正常")
        print("💡 如果沒有音效，請檢查：")
        print("  1. 音效檔案是否存在")
        print("  2. 音效檔案是否損壞")
        print("  3. 系統音量設定")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()
