#!/usr/bin/env python3
"""
測試新的玩家顏色
Test new player colors
"""

import pygame
import sys

def test_player_colors():
    """測試新的玩家顏色效果"""
    print("=== 測試新的玩家顏色效果 ===")
    
    # 初始化 Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # 顏色定義
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    # 新的淺色玩家顏色
    LIGHT_BLUE = (40, 148, 255)  # #2894FF
    LIGHT_RED = (255, 117, 117)  # #FF7575
    # 舊的顏色（對比用）
    OLD_BLUE = (0, 100, 255)
    OLD_RED = (255, 0, 0)
    
    # 載入字體
    try:
        font = pygame.font.Font("assets/fonts/turok.ttf", 24)
        print("✅ 成功載入自定義字體")
    except:
        font = pygame.font.Font(None, 24)
        print("⚠️ 使用系統字體")
    
    def draw_text_with_outline(surface, text, font, color, outline_color, x, y):
        """繪製帶外框的文字"""
        # Draw outline
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    outline_surface = font.render(text, True, outline_color)
                    surface.blit(outline_surface, (x + dx, y + dy))
        
        # Draw main text
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))
    
    def draw_text_normal(surface, text, font, color, x, y):
        """繪製普通文字（對比用）"""
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))
    
    # 測試文字
    test_texts = [
        "Player 1: 戰士 (選擇中)",
        "Player 2: 法師 (已確認)",
        "Player 1 請選擇角色"
    ]
    
    print(f"測試文字: {len(test_texts)} 個")
    for i, text in enumerate(test_texts):
        print(f"  {i+1}. {text}")
    
    print(f"\n顏色對比:")
    print(f"  舊藍色: RGB{OLD_BLUE}")
    print(f"  新藍色: RGB{LIGHT_BLUE} (#2894FF)")
    print(f"  舊紅色: RGB{OLD_RED}")
    print(f"  新紅色: RGB{LIGHT_RED} (#FF7575)")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清空螢幕
        screen.fill((50, 50, 50))
        
        # 繪製測試文字
        y_offset = 50
        
        # 1. 舊顏色（對比）
        draw_text_normal(screen, "舊顏色（對比）:", font, WHITE, 50, y_offset)
        y_offset += 40
        
        draw_text_with_outline(screen, test_texts[0], font, OLD_BLUE, BLACK, 50, y_offset)
        y_offset += 30
        draw_text_with_outline(screen, test_texts[1], font, OLD_RED, BLACK, 50, y_offset)
        y_offset += 30
        draw_text_with_outline(screen, test_texts[2], font, GRAY, BLACK, 50, y_offset)
        y_offset += 50
        
        # 2. 新顏色（改進後）
        draw_text_normal(screen, "新顏色（改進後）:", font, WHITE, 50, y_offset)
        y_offset += 40
        
        draw_text_with_outline(screen, test_texts[0], font, LIGHT_BLUE, BLACK, 50, y_offset)
        y_offset += 30
        draw_text_with_outline(screen, test_texts[1], font, LIGHT_RED, BLACK, 50, y_offset)
        y_offset += 30
        draw_text_with_outline(screen, test_texts[2], font, GRAY, BLACK, 50, y_offset)
        y_offset += 50
        
        # 3. 顏色資訊
        draw_text_normal(screen, "顏色資訊:", font, WHITE, 50, y_offset)
        y_offset += 30
        
        draw_text_normal(screen, f"Player 1 新顏色: RGB{LIGHT_BLUE} (#2894FF)", font, LIGHT_BLUE, 50, y_offset)
        y_offset += 25
        draw_text_normal(screen, f"Player 2 新顏色: RGB{LIGHT_RED} (#FF7575)", font, LIGHT_RED, 50, y_offset)
        y_offset += 25
        
        # 4. 不同背景測試
        draw_text_normal(screen, "不同背景測試:", font, WHITE, 50, y_offset)
        y_offset += 30
        
        # 深色背景
        pygame.draw.rect(screen, (20, 20, 60), (50, y_offset, 300, 30))
        draw_text_with_outline(screen, "深色背景測試", font, LIGHT_BLUE, BLACK, 60, y_offset + 5)
        y_offset += 40
        
        # 淺色背景
        pygame.draw.rect(screen, (200, 200, 200), (50, y_offset, 300, 30))
        draw_text_with_outline(screen, "淺色背景測試", font, LIGHT_RED, BLACK, 60, y_offset + 5)
        
        # 更新顯示
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ 玩家顏色測試完成")

def test_color_contrast():
    """測試顏色對比度"""
    print("\n=== 測試顏色對比度 ===")
    
    # 新顏色
    LIGHT_BLUE = (40, 148, 255)  # #2894FF
    LIGHT_RED = (255, 117, 117)  # #FF7575
    
    # 舊顏色
    OLD_BLUE = (0, 100, 255)
    OLD_RED = (255, 0, 0)
    
    # 測試背景
    backgrounds = [
        ("深色背景", (20, 20, 60)),
        ("淺色背景", (200, 200, 200)),
        ("黑色背景", (0, 0, 0)),
        ("白色背景", (255, 255, 255)),
    ]
    
    print("顏色對比度分析:")
    for bg_name, bg_color in backgrounds:
        print(f"\n{bg_name} ({bg_color}):")
        
        # 計算對比度
        def calc_contrast(color1, color2):
            return abs(color1[0] - color2[0]) + abs(color1[1] - color2[1]) + abs(color1[2] - color2[2])
        
        # 新顏色對比度
        new_blue_contrast = calc_contrast(LIGHT_BLUE, bg_color)
        new_red_contrast = calc_contrast(LIGHT_RED, bg_color)
        
        # 舊顏色對比度
        old_blue_contrast = calc_contrast(OLD_BLUE, bg_color)
        old_red_contrast = calc_contrast(OLD_RED, bg_color)
        
        print(f"  新藍色: {new_blue_contrast} (舊: {old_blue_contrast})")
        print(f"  新紅色: {new_red_contrast} (舊: {old_red_contrast})")
        
        # 評估可讀性
        def assess_readability(contrast):
            if contrast > 300:
                return "✅ 優秀"
            elif contrast > 200:
                return "✅ 良好"
            elif contrast > 100:
                return "⚠️ 一般"
            else:
                return "❌ 較差"
        
        print(f"  新藍色可讀性: {assess_readability(new_blue_contrast)}")
        print(f"  新紅色可讀性: {assess_readability(new_red_contrast)}")
    
    return True

def main():
    """主測試函數"""
    print("🎮 測試新的玩家顏色")
    print("=" * 50)
    
    # 測試顏色對比度
    contrast_success = test_color_contrast()
    
    # 測試視覺效果
    print("\n=== 視覺效果測試 ===")
    print("啟動視覺測試視窗...")
    print("按 ESC 鍵退出測試")
    
    try:
        test_player_colors()
        visual_success = True
    except Exception as e:
        print(f"❌ 視覺測試失敗: {e}")
        visual_success = False
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    print(f"  顏色對比度分析: {'✅ 成功' if contrast_success else '❌ 失敗'}")
    print(f"  視覺效果測試: {'✅ 成功' if visual_success else '❌ 失敗'}")
    
    all_success = contrast_success and visual_success
    print(f"\n總體結果: {'🎉 全部通過' if all_success else '⚠️ 部分失敗'}")

if __name__ == "__main__":
    main()
