import pygame
import os

class FontManager:
    """字體管理器，處理客製化字體載入"""
    
    def __init__(self):
        self.fonts_cache = {}
        self.font_path = "assets/fonts/"
        
    def load_custom_font(self, font_name, size):
        """載入客製化字體"""
        # 檢查快取
        cache_key = f"{font_name}_{size}"
        if cache_key in self.fonts_cache:
            return self.fonts_cache[cache_key]
        
        # 嘗試載入客製化字體檔案
        font_file_path = os.path.join(self.font_path, font_name)
        if os.path.exists(font_file_path):
            try:
                font = pygame.font.Font(font_file_path, size)
                self.fonts_cache[cache_key] = font
                print(f"成功載入客製化字體: {font_name}")
                return font
            except Exception as e:
                print(f"載入客製化字體失敗: {font_name}, 錯誤: {e}")
        
        # 如果客製化字體載入失敗，使用系統字體
        return self.get_system_font(size)
    
    def get_system_font(self, size):
        """獲取系統字體（支援中文）"""
        try:
            # 優先使用微軟雅黑，對中文支援最好
            chinese_fonts = ["microsoftyahei", "simhei", "simsun", "kaiti", "arial"]
            for font_name in chinese_fonts:
                try:
                    font = pygame.font.SysFont(font_name, size)
                    # 測試字體是否能正常渲染中文
                    test_surface = font.render("測試", True, (255, 255, 255))
                    if test_surface.get_width() > 0:
                        print(f"✅ 成功載入系統字體: {font_name}")
                        return font
                except Exception as e:
                    print(f"⚠️  字體 {font_name} 載入失敗: {e}")
                    continue
            
            # 如果都失敗，使用預設字體
            print("⚠️  所有系統字體載入失敗，使用預設字體")
            return pygame.font.Font(None, size)
        except Exception as e:
            print(f"❌ 字體管理器錯誤: {e}")
            # 如果 pygame.font 還沒初始化，返回 None
            return None
    
    def get_font(self, font_name=None, size=32):
        """獲取字體（優先使用客製化字體）"""
        if font_name:
            return self.load_custom_font(font_name, size)
        else:
            return self.get_system_font(size)

# 全域字體管理器實例
font_manager = FontManager() 