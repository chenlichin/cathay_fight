import pygame
import os
import time
from typing import Dict, Optional

class AudioManager:
    """簡化版音效管理系統"""
    
    def __init__(self):
        # 音量設定 (0.0 - 1.0)
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
        # 開關設定
        self.music_enabled = True
        self.sfx_enabled = True
        
        # 音效檔案路徑
        self.music_path = "assets/music/"
        
        # 音效快取
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}
        
        # 當前播放的背景音樂
        self.current_music: Optional[str] = None
        
        # 初始化音效系統
        self._init_audio()
    
    def _init_audio(self):
        """初始化音效系統"""
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("✅ 音效系統初始化成功")
        except Exception as e:
            print(f"❌ 音效系統初始化失敗: {e}")
            self.music_enabled = False
            self.sfx_enabled = False
    
    def load_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        """載入音效檔案"""
        if not self.sfx_enabled:
            return None
            
        try:
            filepath = os.path.join(self.music_path, filename)
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.sfx_volume)
                return sound
            else:
                print(f"⚠️  音效檔案不存在: {filepath}")
                return None
        except Exception as e:
            print(f"❌ 載入音效失敗 {filename}: {e}")
            return None
    
    def play_sound(self, filename: str, sound_name: str = None):
        """播放音效（簡化版）"""
        if not self.sfx_enabled:
            return
            
        # 檢查快取
        if filename not in self.sound_cache:
            sound = self.load_sound(filename)
            if sound:
                self.sound_cache[filename] = sound
        
        # 播放音效
        if filename in self.sound_cache:
            try:
                self.sound_cache[filename].play()
                print(f"🔊 播放音效: {filename}")
            except Exception as e:
                print(f"❌ 播放音效失敗 {filename}: {e}")
    
    def play_music(self, filename: str, loop: bool = True):
        """播放背景音樂"""
        if not self.music_enabled:
            return
            
        try:
            filepath = os.path.join(self.music_path, filename)
            if os.path.exists(filepath):
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)
                # 設定循環播放
                loop_count = -1 if loop else 0
                pygame.mixer.music.play(loop_count)
                self.current_music = filename
                print(f"🎵 播放背景音樂: {filename}")
            else:
                print(f"⚠️  音樂檔案不存在: {filepath}")
        except Exception as e:
            print(f"❌ 播放背景音樂失敗 {filename}: {e}")
    
    def stop_music(self):
        """停止背景音樂"""
        try:
            pygame.mixer.music.stop()
            self.current_music = None
            print("🔇 停止背景音樂")
        except Exception as e:
            print(f"❌ 停止背景音樂失敗: {e}")
    
    def pause_music(self):
        """暫停背景音樂"""
        try:
            pygame.mixer.music.pause()
            print("⏸️  暫停背景音樂")
        except Exception as e:
            print(f"❌ 暫停背景音樂失敗: {e}")
    
    def unpause_music(self):
        """恢復背景音樂"""
        try:
            pygame.mixer.music.unpause()
            print("▶️  恢復背景音樂")
        except Exception as e:
            print(f"❌ 恢復背景音樂失敗: {e}")
    
    def set_music_volume(self, volume: float):
        """設定背景音樂音量 (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        print(f"🔊 背景音樂音量: {self.music_volume:.1f}")
    
    def set_sfx_volume(self, volume: float):
        """設定音效音量 (0.0 - 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        # 更新所有快取音效的音量
        for sound in self.sound_cache.values():
            sound.set_volume(self.sfx_volume)
        print(f"🔊 音效音量: {self.sfx_volume:.1f}")
    
    def toggle_music(self):
        """切換背景音樂開關"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        print(f"🎵 背景音樂: {'開啟' if self.music_enabled else '關閉'}")
    
    def toggle_sfx(self):
        """切換音效開關"""
        self.sfx_enabled = not self.sfx_enabled
        print(f"🔊 音效: {'開啟' if self.sfx_enabled else '關閉'}")
    
    def get_status(self) -> Dict[str, any]:
        """獲取音效系統狀態"""
        return {
            "music_enabled": self.music_enabled,
            "sfx_enabled": self.sfx_enabled,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "current_music": self.current_music,
            "sound_cache_count": len(self.sound_cache)
        }

# 全域音效管理器實例
audio_manager = AudioManager()

# 音效檔案對應表
SOUND_EFFECTS = {
    "menu_select": "option_switch.mp3",     # 使用現有的選項切換音效
    "attack1_hit": "attack1_hit.mp3",      # 第一種攻擊音效（HIGH_ATTACK）
    "attack2_skill": "attack2_skill.mp3",  # 第二種攻擊音效（LOW_ATTACK）
    "victory": "victory.mp3",
    "game_start": "game_start_fight.mp3",
    "option_switch": "option_switch.mp3",   # 選項切換音效
    "option_confirmed": "option_confirmed.mp3"  # 選項確認音效
}

# 背景音樂檔案
BACKGROUND_MUSIC = {
    "menu": "background_menu.mp3",
    "game": "background_main.mp3"
}
