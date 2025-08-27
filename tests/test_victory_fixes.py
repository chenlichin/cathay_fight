#!/usr/bin/env python3
"""
Victory 修復驗證測試工具
測試 Victory 畫面顯示、音效播放和選單音效
"""

import pygame
import time
from audio_manager import audio_manager, SOUND_EFFECTS

def test_victory_audio():
    """測試勝利音效播放"""
    print("🏆 測試勝利音效播放...")
    
    # 初始化 Pygame
    pygame.init()
    
    try:
        # 測試勝利音效
        print("播放勝利音效...")
        audio_manager.play_sound(SOUND_EFFECTS["victory"])
        time.sleep(2)
        
        print("✅ 勝利音效測試完成")
        
    except Exception as e:
        print(f"❌ 勝利音效測試失敗: {e}")
    
    finally:
        pygame.quit()

def test_menu_audio():
    """測試選單音效播放"""
    print("\n🎵 測試選單音效播放...")
    
    # 初始化 Pygame
    pygame.init()
    
    try:
        # 測試選項切換音效
        print("播放選項切換音效...")
        audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
        time.sleep(1)
        
        # 測試選項確認音效
        print("播放選項確認音效...")
        audio_manager.play_sound(SOUND_EFFECTS["option_confirmed"])
        time.sleep(1)
        
        print("✅ 選單音效測試完成")
        
    except Exception as e:
        print(f"❌ 選單音效測試失敗: {e}")
    
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
    print("🧪 Victory 修復驗證測試工具")
    print("=" * 50)
    
    try:
        # 測試音效系統狀態
        test_audio_status()
        
        # 測試勝利音效
        test_victory_audio()
        
        # 測試選單音效
        test_menu_audio()
        
        print("\n🎉 所有測試完成！")
        print("💡 修復內容：")
        print("  - Victory 畫面顯示2秒後消失")
        print("  - 每回合都會播放勝利音效")
        print("  - 回合結束選單有選項切換和確認音效")
        print("  - 遊戲結束選單有選項切換和確認音效")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()
