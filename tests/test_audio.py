#!/usr/bin/env python3
"""
音效測試工具
測試所有音效和背景音樂是否正常播放
"""

import pygame
import time
from audio_manager import audio_manager, SOUND_EFFECTS, BACKGROUND_MUSIC

def main():
    print("🎵 音效測試工具")
    print("=" * 50)
    
    # 初始化 Pygame
    pygame.init()
    
    # 創建測試視窗
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("音效測試")
    
    # 測試背景音樂
    print("\n🎵 測試背景音樂...")
    print("1. 主選單背景音樂")
    audio_manager.play_music(BACKGROUND_MUSIC["menu"])
    time.sleep(3)
    
    print("2. 遊戲背景音樂")
    audio_manager.play_music(BACKGROUND_MUSIC["game"])
    time.sleep(3)
    
    # 測試音效
    print("\n🔊 測試音效...")
    for sound_name, filename in SOUND_EFFECTS.items():
        print(f"播放: {sound_name} ({filename})")
        audio_manager.play_sound(filename)
        time.sleep(1)
    
    # 測試音量控制
    print("\n🔊 測試音量控制...")
    print("降低背景音樂音量到 0.3")
    audio_manager.set_music_volume(0.3)
    time.sleep(2)
    
    print("降低音效音量到 0.5")
    audio_manager.set_sfx_volume(0.5)
    time.sleep(2)
    
    print("恢復音量到正常")
    audio_manager.set_music_volume(0.7)
    audio_manager.set_sfx_volume(0.8)
    
    # 測試開關功能
    print("\n🔇 測試音效開關...")
    print("關閉音效")
    audio_manager.toggle_sfx()
    time.sleep(1)
    
    print("播放音效（應該聽不到）")
    audio_manager.play_sound(SOUND_EFFECTS["attack1"])
    time.sleep(1)
    
    print("開啟音效")
    audio_manager.toggle_sfx()
    time.sleep(1)
    
    print("播放音效（應該聽得到）")
    audio_manager.play_sound(SOUND_EFFECTS["attack1"])
    time.sleep(1)
    
    # 測試背景音樂開關
    print("\n🎵 測試背景音樂開關...")
    print("關閉背景音樂")
    audio_manager.toggle_music()
    time.sleep(2)
    
    print("開啟背景音樂")
    audio_manager.toggle_music()
    time.sleep(2)
    
    # 顯示狀態
    print("\n📊 音效系統狀態:")
    status = audio_manager.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✅ 音效測試完成！")
    print("💡 提示：")
    print("  - 在程式中可以用 audio_manager.set_music_volume(0.5) 調整音量")
    print("  - 可以用 audio_manager.toggle_music() 開關背景音樂")
    print("  - 可以用 audio_manager.toggle_sfx() 開關音效")
    
    # 停止所有音效
    audio_manager.stop_music()
    pygame.quit()

if __name__ == "__main__":
    main()
