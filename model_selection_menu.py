#!/usr/bin/env python3
"""
模型選擇選單
讓玩家選擇 AWS Bedrock 模型
"""

import pygame
from font_manager import font_manager
from audio_manager import audio_manager, SOUND_EFFECTS
from model_config import get_aws_models

class ModelSelectionMenu:
    """模型選擇選單"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 選擇狀態
        self.selected_model = 0
        self.current_player = 1
        self.player1_model = None
        self.player2_model = None
        
        # 載入可用模型（來自 model_config）
        self.models = get_aws_models()
        self.model_list = list(self.models.keys())
        
        # 載入字體
        self.title_font = font_manager.get_font("your_custom_font.ttf", size=48)
        self.model_font = font_manager.get_font("your_custom_font.ttf", size=24)
        self.info_font = font_manager.get_font("your_custom_font.ttf", size=20)
        self.desc_font = font_manager.get_font("your_custom_font.ttf", size=16)
        
        # 檢查字體是否成功載入，如果失敗則使用系統字體
        self._ensure_fonts_loaded()
        
        # 顏色
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 100, 255)
        self.GREEN = (0, 255, 0)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.DARK_BLUE = (20, 20, 60)
        # 淺色玩家顏色
        self.LIGHT_BLUE = (40, 148, 255)  # #2894FF
        self.LIGHT_RED = (255, 117, 117)  # #FF7575
        
        # 模型卡片設定
        self.card_width = 300
        self.card_height = 150
        self.card_spacing = 30
        self.cards_per_row = 2
        
        # 載入背景圖片
        try:
            self.bg_image = pygame.image.load("assets/images/background/character_background.png").convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (screen_width, screen_height))
        except:
            print("⚠️ 無法載入模型選擇背景圖片")
            self.bg_image = None
        
        # 計算佈局
        self.calculate_layout()
    
    def draw_text_with_outline(self, surface, text, font, color, outline_color, x, y):
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
    
    def _ensure_fonts_loaded(self):
        """確保所有字體都已正確載入"""
        # 檢查字體是否成功載入，如果失敗則使用系統字體
        if not self.title_font:
            print("⚠️  無法載入標題字體，使用系統字體")
            try:
                self.title_font = pygame.font.SysFont("microsoftyahei", 48)
            except:
                self.title_font = pygame.font.Font(None, 48)
        
        if not self.model_font:
            print("⚠️  無法載入模型字體，使用系統字體")
            try:
                self.model_font = pygame.font.SysFont("microsoftyahei", 24)
            except:
                self.model_font = pygame.font.Font(None, 24)
        
        if not self.info_font:
            print("⚠️  無法載入資訊字體，使用系統字體")
            try:
                self.info_font = pygame.font.SysFont("microsoftyahei", 20)
            except:
                self.info_font = pygame.font.Font(None, 20)
        
        if not self.desc_font:
            print("⚠️  無法載入描述字體，使用系統字體")
            try:
                self.desc_font = pygame.font.SysFont("microsoftyahei", 16)
            except:
                self.desc_font = pygame.font.Font(None, 16)
        
        print("✅ 字體載入完成")
    
    def calculate_layout(self):
        """計算佈局位置"""
        total_cards = len(self.model_list)
        rows = (total_cards + self.cards_per_row - 1) // self.cards_per_row
        
        # 計算總寬度和高度
        total_width = self.cards_per_row * self.card_width + (self.cards_per_row - 1) * self.card_spacing
        total_height = rows * self.card_height + (rows - 1) * self.card_spacing
        
        # 起始位置（置中）
        start_x = (self.screen_width - total_width) // 2
        start_y = 200
        
        # 計算每個卡片的位置
        self.card_positions = []
        for i, model_id in enumerate(self.model_list):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            x = start_x + col * (self.card_width + self.card_spacing)
            y = start_y + row * (self.card_height + self.card_spacing)
            self.card_positions.append((x, y))
    
    def handle_input(self, event):
        """處理輸入事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                # 向左選擇
                self.selected_model = (self.selected_model - 1) % len(self.model_list)
                audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
            
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                # 向右選擇
                self.selected_model = (self.selected_model + 1) % len(self.model_list)
                audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
            
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                # 向上選擇（跳過行）
                self.selected_model = (self.selected_model - self.cards_per_row) % len(self.model_list)
                audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
            
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                # 向下選擇（跳過行）
                self.selected_model = (self.selected_model + self.cards_per_row) % len(self.model_list)
                audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # 確認選擇
                if self.current_player == 1:
                    self.player1_model = self.model_list[self.selected_model]
                    self.current_player = 2
                    # 選擇不同的模型
                    next_model = (self.selected_model + 1) % len(self.model_list)
                    self.selected_model = next_model
                    audio_manager.play_sound(SOUND_EFFECTS["option_confirmed"])
                else:
                    self.player2_model = self.model_list[self.selected_model]
                    audio_manager.play_sound(SOUND_EFFECTS["option_confirmed"])
                    return "START_GAME"
            
            elif event.key == pygame.K_ESCAPE:
                return "CHARACTER_SELECT"
        
        return None
    
    def get_selections(self):
        """獲取玩家選擇"""
        return {
            "player1_model": self.player1_model,
            "player2_model": self.player2_model
        }
    
    def draw_model_cards(self, surface):
        """繪製模型卡片"""
        for i, (model_id, pos) in enumerate(zip(self.model_list, self.card_positions)):
            x, y = pos
            model_info = self.models[model_id]
            
            # 選擇狀態
            is_selected = (i == self.selected_model)
            is_player1_selected = (i == self.player1_model and self.current_player == 2)
            is_player2_selected = (i == self.player2_model and self.current_player == 1)
            
            # 邊框顏色
            if is_selected:
                border_color = self.YELLOW
                border_width = 4
            elif is_player1_selected:
                border_color = self.BLUE
                border_width = 3
            elif is_player2_selected:
                border_color = self.RED
                border_width = 3
            else:
                border_color = self.GRAY
                border_width = 2
            
            # 繪製卡片背景
            pygame.draw.rect(surface, self.DARK_BLUE, (x, y, self.card_width, self.card_height))
            pygame.draw.rect(surface, border_color, (x, y, self.card_width, self.card_height), border_width)
            
            # 繪製模型名稱
            try:
                name_surface = self.model_font.render(model_info["name"], True, self.WHITE)
                name_rect = name_surface.get_rect(center=(x + self.card_width//2, y + 30))
                surface.blit(name_surface, name_rect)
            except Exception as e:
                print(f"⚠️  無法渲染模型名稱: {e}")
                # 使用備用文字
                fallback_surface = pygame.font.Font(None, 24).render(model_info["name"], True, self.WHITE)
                fallback_rect = fallback_surface.get_rect(center=(x + self.card_width//2, y + 30))
                surface.blit(fallback_surface, fallback_rect)
            
            # 繪製強度等級（若無則顯示速度）
            try:
                power_level = model_info.get("power_level") or model_info.get("speed", "")
                power_surface = self.info_font.render(str(power_level), True, self.YELLOW)
                power_rect = power_surface.get_rect(center=(x + self.card_width//2, y + 60))
                surface.blit(power_surface, power_rect)
            except Exception as e:
                print(f"⚠️  無法渲染強度等級: {e}")
                # 使用備用文字
                fallback_surface = pygame.font.Font(None, 20).render(str(model_info.get("power_level", model_info.get("speed", ""))), True, self.YELLOW)
                fallback_rect = fallback_surface.get_rect(center=(x + self.card_width//2, y + 60))
                surface.blit(fallback_surface, fallback_rect)
            
            # 繪製描述
            try:
                desc_surface = self.desc_font.render(model_info["description"], True, self.WHITE)
                desc_rect = desc_surface.get_rect(center=(x + self.card_width//2, y + 90))
                surface.blit(desc_surface, desc_rect)
            except Exception as e:
                print(f"⚠️  無法渲染描述: {e}")
                # 使用備用文字
                fallback_surface = pygame.font.Font(None, 16).render(model_info["description"], True, self.WHITE)
                fallback_rect = fallback_surface.get_rect(center=(x + self.card_width//2, y + 90))
                surface.blit(fallback_surface, fallback_rect)
            
            # 繪製策略
            try:
                strategy_text = f"策略: {model_info.get('strategy', '-') }"
                strategy_surface = self.desc_font.render(strategy_text, True, self.GREEN)
                strategy_rect = strategy_surface.get_rect(center=(x + self.card_width//2, y + 115))
                surface.blit(strategy_surface, strategy_rect)
            except Exception as e:
                print(f"⚠️  無法渲染策略: {e}")
                # 使用備用文字
                strategy_text = f"策略: {model_info['strategy']}"
                fallback_surface = pygame.font.Font(None, 16).render(strategy_text, True, self.GREEN)
                fallback_rect = fallback_surface.get_rect(center=(x + self.card_width//2, y + 115))
                surface.blit(fallback_surface, fallback_rect)
    
    def draw_player_status(self, surface):
        """繪製玩家狀態"""
        # 玩家1狀態 - 顯示當前選擇的模型
        p1_color = self.LIGHT_BLUE if self.current_player == 1 else self.GRAY
        if self.current_player == 1:
            # 當前正在選擇，顯示游標指向的模型
            current_model = self.models[self.model_list[self.selected_model]]
            p1_text = f"Player 1: {current_model['name']} (選擇中)"
        else:
            # 已選擇完成，顯示確認的模型
            if self.player1_model:
                selected_model = self.models[self.player1_model]
                p1_text = f"Player 1: {selected_model['name']} (已確認)"
            else:
                p1_text = "Player 1: 未選擇"
        
        # 使用帶框線的文字繪製玩家1狀態
        try:
            self.draw_text_with_outline(surface, p1_text, self.info_font, p1_color, self.BLACK, 50, 50)
        except Exception as e:
            print(f"⚠️  無法渲染玩家1狀態: {e}")
            fallback_surface = pygame.font.Font(None, 20).render(p1_text, True, p1_color)
            surface.blit(fallback_surface, (50, 50))
        
        # 玩家2狀態 - 顯示當前選擇的模型
        p2_color = self.LIGHT_RED if self.current_player == 2 else self.GRAY
        if self.current_player == 2:
            # 當前正在選擇，顯示游標指向的模型
            current_model = self.models[self.model_list[self.selected_model]]
            p2_text = f"Player 2: {current_model['name']} (選擇中)"
        else:
            # 已選擇完成，顯示確認的模型
            if self.player2_model:
                selected_model = self.models[self.player2_model]
                p2_text = f"Player 2: {selected_model['name']} (已確認)"
            else:
                p2_text = "Player 2: 未選擇"
        
        # 使用帶框線的文字繪製玩家2狀態
        try:
            self.draw_text_with_outline(surface, p2_text, self.info_font, p2_color, self.BLACK, 50, 80)
        except Exception as e:
            print(f"⚠️  無法渲染玩家2狀態: {e}")
            fallback_surface = pygame.font.Font(None, 20).render(p2_text, True, p2_color)
            surface.blit(fallback_surface, (50, 80))
        
        # 當前選擇提示
        if self.current_player == 1:
            current_text = "Player 1 請選擇 AI 模型"
        else:
            current_text = "Player 2 請選擇 AI 模型"
        
        # 使用帶框線的文字繪製當前選擇提示
        try:
            self.draw_text_with_outline(surface, current_text, self.model_font, self.YELLOW, self.BLACK,
                                       (self.screen_width - self.model_font.size(current_text)[0]) // 2, 100)
        except Exception as e:
            print(f"⚠️  無法渲染當前選擇提示: {e}")
            fallback_surface = pygame.font.Font(None, 24).render(current_text, True, self.YELLOW)
            fallback_rect = fallback_surface.get_rect(center=(self.screen_width//2, 100))
            surface.blit(fallback_surface, fallback_rect)
    
    def draw_instructions(self, surface):
        """繪製操作說明"""
        instructions = [
            "← → 或 A/D: 選擇模型",
            "↑ ↓ 或 W/S: 選擇模型",
            "Enter/Space: 確認選擇",
            "ESC: 返回角色選擇"
        ]
        
        for i, instruction in enumerate(instructions):
            try:
                inst_surface = self.desc_font.render(instruction, True, self.WHITE)
                inst_x = self.screen_width - 250
                inst_y = self.screen_height - 120 + i * 25
                surface.blit(inst_surface, (inst_x, inst_y))
            except Exception as e:
                print(f"⚠️  無法渲染說明文字 {i}: {e}")
                fallback_surface = pygame.font.Font(None, 16).render(instruction, True, self.WHITE)
                inst_x = self.screen_width - 250
                inst_y = self.screen_height - 120 + i * 25
                surface.blit(fallback_surface, (inst_x, inst_y))
    
    def draw(self, surface):
        """繪製選單"""
        # 繪製背景
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(self.BLACK)
        
        # 繪製標題
        title_text = "AI 模型選擇"
        try:
            title_surface = self.title_font.render(title_text, True, self.YELLOW)
            title_rect = title_surface.get_rect(center=(self.screen_width//2, 50))
            surface.blit(title_surface, title_rect)
        except Exception as e:
            print(f"⚠️  無法渲染標題: {e}")
            fallback_surface = pygame.font.Font(None, 48).render(title_text, True, self.YELLOW)
            fallback_rect = fallback_surface.get_rect(center=(self.screen_width//2, 50))
            surface.blit(fallback_surface, fallback_rect)
        
        # 繪製模型卡片
        self.draw_model_cards(surface)
        
        # 繪製玩家狀態
        self.draw_player_status(surface)
        
        # 繪製操作說明
        self.draw_instructions(surface)
