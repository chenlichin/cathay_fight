#!/usr/bin/env python3
"""
選單音效測試工具
測試選項切換和確認音效是否正常播放
"""

import pygame
import time
from audio_manager import audio_manager, SOUND_EFFECTS
from menu import GameMenu, CharacterSelectMenu

def main():
    print("🎵 選單音效測試工具")
    print("=" * 50)
    
    # 初始化 Pygame
    pygame.init()
    
    # 創建測試視窗
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("選單音效測試")
    
    # 創建選單實例
    main_menu = GameMenu(1200, 800)
    character_menu = CharacterSelectMenu(1200, 800)
    
    # 測試主選單音效
    print("\n🎮 測試主選單音效...")
    print("使用 ↑↓ 或 W/S 切換選項，按 Enter 或 Space 確認")
    print("按 ESC 退出測試")
    
    clock = pygame.time.Clock()
    running = True
    current_menu = "main"  # main, character
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    # 切換選單
                    if current_menu == "main":
                        current_menu = "character"
                        print("切換到角色選擇選單")
                    else:
                        current_menu = "main"
                        print("切換到主選單")
                
                # 處理選單輸入
                if current_menu == "main":
                    result = main_menu.handle_input(event)
                    if result == "CHARACTER_SELECT":
                        print("主選單：選擇進入角色選擇")
                        current_menu = "character"
                    elif result == "QUIT":
                        running = False
                else:
                    result = character_menu.handle_input(event)
                    if result == "START_GAME":
                        print("角色選擇：開始遊戲")
                        current_menu = "main"
                    elif result == "MAIN_MENU":
                        print("角色選擇：返回主選單")
                        current_menu = "main"
        
        # 繪製選單
        if current_menu == "main":
            main_menu.draw(screen)
        else:
            character_menu.draw(screen)
        
        # 顯示當前選單狀態
        font = pygame.font.Font(None, 36)
        status_text = f"當前選單: {'主選單' if current_menu == 'main' else '角色選擇'}"
        status_surface = font.render(status_text, True, (255, 255, 255))
        screen.blit(status_surface, (10, 10))
        
        help_text = "TAB: 切換選單 | ESC: 退出測試"
        help_surface = font.render(help_text, True, (200, 200, 200))
        screen.blit(help_surface, (10, 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    print("\n✅ 選單音效測試完成！")
    print("💡 測試結果：")
    print("  - 選項切換音效 (option_switch)")
    print("  - 選項確認音效 (option_confirmed)")
    print("  - 背景音樂自動切換")
    
    pygame.quit()

if __name__ == "__main__":
    main()
