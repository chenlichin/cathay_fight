#!/usr/bin/env python3
"""
角色選擇選單測試工具
測試選項切換和模型選擇功能是否正常
"""

import pygame
from menu import CharacterSelectMenu
from audio_manager import audio_manager

def main():
    print("🎮 角色選擇選單測試工具")
    print("=" * 50)
    
    # 初始化 Pygame
    pygame.init()
    
    # 創建測試視窗
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("角色選擇測試")
    
    # 創建角色選擇選單
    character_menu = CharacterSelectMenu(1200, 800)
    
    print("\n🎯 測試說明：")
    print("1. 使用 ←→ 或 A/D 切換角色/模型")
    print("2. 使用 ↑↓ 或 W/S 切換選擇類型（角色/模型）")
    print("3. 按 Enter/Space 確認選擇")
    print("4. 按 ESC 返回主選單")
    print("5. 按 Q 退出測試")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                
                # 處理選單輸入
                result = character_menu.handle_input(event)
                if result == "START_GAME":
                    print("✅ 遊戲開始！")
                    # 顯示選擇結果
                    selections = character_menu.get_selections()
                    print(f"Player 1: 角色 {selections['player1_character']}, 模型 {selections['player1_model']}")
                    print(f"Player 2: 角色 {selections['player2_character']}, 模型 {selections['player2_model']}")
                    # 重置選單
                    character_menu = CharacterSelectMenu(1200, 800)
                elif result == "MAIN_MENU":
                    print("🔙 返回主選單")
                    # 重置選單
                    character_menu = CharacterSelectMenu(1200, 800)
        
        # 繪製選單
        character_menu.draw(screen)
        
        # 顯示當前狀態
        font = pygame.font.Font(None, 36)
        status_text = f"當前玩家: Player {character_menu.current_player}"
        status_surface = font.render(status_text, True, (255, 255, 255))
        screen.blit(status_surface, (10, 10))
        
        mode_text = f"選擇模式: {'角色' if character_menu.selection_mode == 'CHARACTER' else '模型'}"
        mode_surface = font.render(mode_text, True, (255, 255, 255))
        screen.blit(mode_surface, (10, 40))
        
        help_text = "Q: 退出測試"
        help_surface = font.render(help_text, True, (200, 200, 200))
        screen.blit(help_surface, (10, 70))
        
        pygame.display.flip()
        clock.tick(60)
    
    print("\n✅ 角色選擇測試完成！")
    pygame.quit()

if __name__ == "__main__":
    main()
