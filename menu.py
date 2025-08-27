import pygame
import sys
import os
from font_manager import font_manager
from audio_manager import audio_manager, SOUND_EFFECTS
from character_loader import character_loader

class GameMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_state = "MAIN_MENU"  # MAIN_MENU, CHARACTER_SELECT, GAME
        self.selected_option = 0
        self.menu_options = ["Game Start" , "Exit"]
        self.blink_timer = 0
        self.blink_speed = 500  # milliseconds
        
        # Load fonts using font manager
        # 您可以在這裡指定客製化字體檔案名稱，例如：
        # self.title_font = font_manager.get_font("your_custom_font.ttf", 80)
        # 如果不指定字體檔案名稱，會使用系統字體
        
        self.title_font = font_manager.get_font("your_custom_font.ttf",size=80)
        self.menu_font = font_manager.get_font("your_custom_font.ttf",size=40)
        self.subtitle_font = font_manager.get_font("your_custom_font.ttf",size=30)
        
        # Load background
        try:
            self.bg_image = pygame.image.load("assets/images/title_background.png").convert_alpha()
            # 確保背景圖片完全覆蓋螢幕，避免邊緣問題
            self.bg_image = pygame.transform.scale(self.bg_image, (screen_width, screen_height))
            # 創建一個稍大的表面來避免邊緣問題
            temp_surface = pygame.Surface((screen_width + 8, screen_height + 8))
            temp_surface.fill((50, 0, 0))  # 用背景色填充
            temp_surface.blit(self.bg_image, (4, 4))  # 在中心繪製
            self.bg_image = temp_surface
        except:
            # Fallback to solid color if image not found
            self.bg_image = pygame.Surface((screen_width, screen_height))
            self.bg_image.fill((50, 0, 0))
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.ORANGE = (255, 165, 0)
        self.BLACK = (0, 0, 0)
        
    def handle_input(self, event):
        """處理輸入事件"""
        if self.current_state == "MAIN_MENU":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    # 播放選項切換音效
                    audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    # 播放選項切換音效
                    audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # 播放選項確認音效
                    audio_manager.play_sound(SOUND_EFFECTS["option_confirmed"])
                    return self.execute_menu_option()
        return None
    
    def execute_menu_option(self):
        """執行選中的選單選項"""
        if self.selected_option == 0:  # 進入遊戲
            return "CHARACTER_SELECT"
        elif self.selected_option == 1:  # 結束遊戲
            return "QUIT"
        return None
    
    def update(self):
        """更新選單狀態"""
        self.blink_timer += pygame.time.get_ticks() % 1000
    
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
    
    def draw(self, surface):
        """繪製選單"""
        if self.current_state == "MAIN_MENU":
            # 先完全填充螢幕，確保沒有縫隙
            surface.fill((50, 0, 0))
            # Draw background - 確保完全覆蓋，避免邊緣問題
            surface.blit(self.bg_image, (-4, -4))  # 稍微偏移以覆蓋邊緣
            
            # Draw title
            title_text = ""
            title_surface = self.title_font.render(title_text, True, self.YELLOW)
            title_rect = title_surface.get_rect()
            title_x = (self.screen_width - title_rect.width) // 2
            title_y = self.screen_height // 4
            
            self.draw_text_with_outline(surface, title_text, self.title_font, 
                                      self.YELLOW, self.BLACK, title_x, title_y)
            
            # Draw menu options
            menu_start_y = self.screen_height // 2 + 50
            for i, option in enumerate(self.menu_options):
                # Calculate position
                option_surface = self.menu_font.render(option, True, self.WHITE)
                option_rect = option_surface.get_rect()
                option_x = (self.screen_width - option_rect.width) // 2
                option_y = menu_start_y + i * 80
                
                # Determine color and effects
                if i == self.selected_option:
                    # Blinking effect for selected option
                    blink_state = (pygame.time.get_ticks() // self.blink_speed) % 2
                    if blink_state:
                        color = self.WHITE
                    else:
                        color = self.ORANGE
                    
                    # Draw selection indicator
                    indicator = "► "
                    indicator_surface = self.menu_font.render(indicator, True, color)
                    indicator_rect = indicator_surface.get_rect()
                    indicator_x = option_x - indicator_rect.width - 10
                    self.draw_text_with_outline(surface, indicator, self.menu_font,
                                              color, self.BLACK, indicator_x, option_y)
                else:
                    color = self.WHITE
                
                # Draw menu option
                self.draw_text_with_outline(surface, option, self.menu_font,
                                          color, self.BLACK, option_x, option_y)
            
            # Draw instructions
            instruction_text = "使用 ↑↓ 或 W/S 選擇，按 Enter 或 Space 確認"
            instruction_surface = self.subtitle_font.render(instruction_text, True, self.WHITE)
            instruction_rect = instruction_surface.get_rect()
            instruction_x = (self.screen_width - instruction_rect.width) // 2
            instruction_y = self.screen_height - 100
            
            self.draw_text_with_outline(surface, instruction_text, self.subtitle_font,
                                      self.WHITE, self.BLACK, instruction_x, instruction_y)


class CharacterSelectMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_state = "CHARACTER_SELECT"
        
        # 角色資料（從 CSV 載入，最多顯示 6 個）
        all_chars = character_loader.get_all_characters()
        self.sorted_ids = sorted(all_chars.keys())[:6]
        self.characters = [all_chars[cid] for cid in self.sorted_ids]

        # 玩家狀態
        self.current_player = 1
        self.focus_index = 0
        self.player1_character = 0
        self.player2_character = 1 if len(self.characters) > 1 else 0
        self.player1_locked = False
        self.player2_locked = False

        # 字型
        self.title_font = font_manager.get_font("your_custom_font.ttf", size=60)
        self.player_font = font_manager.get_font("your_custom_font.ttf", size=32)
        self.player_font_small = font_manager.get_font("your_custom_font.ttf", size=int(32 * 0.7))
        self.name_font = font_manager.get_font("your_custom_font.ttf", size=24)
        self.name_font_small = font_manager.get_font("your_custom_font.ttf", size=int(24 * 0.7))
        self.desc_font = font_manager.get_font("your_custom_font.ttf", size=20)
        
        # 顏色
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 100, 255)
        self.GREEN = (0, 255, 0)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        
        # 背景
        try:
            self.bg_image = pygame.image.load("assets/images/background/character_background.png").convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (screen_width, screen_height))
        except Exception:
            self.bg_image = None

        # 圖示快取（彩色與灰階），維持 2:3 比例顯示
        self.card_img_w = 160
        self.card_img_h = 240
        self.card_pad = 10
        self.icons_color = []
        self.icons_gray = []
        for char in self.characters:
            icon_path = char.get("icon_path")
            try:
                icon = pygame.image.load(icon_path).convert_alpha()
                icon = pygame.transform.smoothscale(icon, (self.card_img_w, self.card_img_h))
            except Exception:
                icon = pygame.Surface((self.card_img_w, self.card_img_h), pygame.SRCALPHA)
                icon.fill((128, 128, 128, 255))
            self.icons_color.append(icon)
            # 生成灰階版本
            gray = self._to_grayscale(icon)
            self.icons_gray.append(gray)

        # 佈局（改為 Carousel），卡片大小以圖片+文字為主
        name_h = self.name_font_small.get_height()
        self.card_w = self.card_img_w + self.card_pad * 2
        self.card_h = self.card_pad + self.card_img_h + 6 + name_h + self.card_pad
        # Carousel 參數
        self.carousel_visible = 5  # 中央1 + 左右各2
        self.center_scale = 1.0  # 中央不放大
        self.side_scale = 0.6
        # 預留左右 20% 邊界（未來放大圖），並以中間 60% 區域進行 Carousel 排列
        self.side_margin_ratio = 0.2
        self.left_margin = int(self.screen_width * self.side_margin_ratio)
        self.right_margin = self.screen_width - self.left_margin
        self.content_width = self.right_margin - self.left_margin  # 約 60% 寬
        self.carousel_center_x = self.left_margin + self.content_width // 2
        # 計算間距：確保最遠兩側（±2）不超出內容區，並稍微緊湊（*0.9）
        side_w = int(self.card_img_w * self.side_scale)
        max_spacing = max(10, int(((self.content_width - side_w) / 4)))
        self.carousel_spacing = max(10, int(max_spacing * 0.9))
        # 讓 Carousel 避開標題：標題高 + 80 像素間距，並在剩餘區域垂直置中
        self.title_top_offset = self.title_font.get_height() + 80
        self.bottom_margin = 160  # 保留底部資訊空間
        avail_h = max(0, self.screen_height - self.title_top_offset - self.bottom_margin)
        self.carousel_y = self.title_top_offset + max(0, (avail_h - int(self.card_img_h * self.center_scale)) // 2)
        # 邊緣漸層覆蓋快取
        self._overlay_cache = {}
        self._faded_cache = {}
        # 預覽大圖（灰階與彩色）
        self.preview_color = {}
        self.preview_gray = {}
        # 動畫
        self.animating = False
        self.anim_dir = 0  # -1 左, +1 右
        self.anim_start = 0
        self.anim_duration = 300
        self.slide_offset = 0.0  # 由 0 補間到 -dir

    def _to_grayscale(self, surface: pygame.Surface) -> pygame.Surface:
        # 轉灰階但保留原始 alpha（透明區維持透明）
        src = surface.copy().convert_alpha()
        w, h = src.get_width(), src.get_height()
        try:
            src.lock()
            for y in range(h):
                for x in range(w):
                    r, g, b, a = src.get_at((x, y))
                    if a == 0:
                        continue
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                    src.set_at((x, y), (gray, gray, gray, a))
        finally:
            try:
                src.unlock()
            except Exception:
                pass
        return src

    def _get_side_overlay(self, w: int, h: int) -> pygame.Surface:
        key = (w, h)
        if key in self._overlay_cache:
            return self._overlay_cache[key]
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        max_alpha = 100
        for x in range(w):
            # 左右漸層：中心透明，邊緣較深
            dist = abs(x - w / 2) / (w / 2)
            a = int(max_alpha * dist)
            pygame.draw.line(overlay, (0, 0, 0, a), (x, 0), (x, h))
        self._overlay_cache[key] = overlay
        return overlay

    def _get_faded_image(self, idx: int, draw_w: int, draw_h: int, alpha_base: int, dir_left: bool) -> pygame.Surface:
        key = (idx, draw_w, draw_h, alpha_base, dir_left)
        if key in self._faded_cache:
            return self._faded_cache[key]
        # 取得縮放後圖片
        base = pygame.transform.smoothscale(self.icons_gray[idx], (draw_w, draw_h)).convert_alpha()
        # 以中央為最大不透明度 alpha_base；並依卡片方向設定橫向漸層：
        # 左側卡片：左→右 (0→alpha_base)；右側卡片：右→左 (0→alpha_base)
        try:
            base.lock()
            w, h = base.get_width(), base.get_height()
            for x in range(w):
                u = x / (w - 1) if w > 1 else 1.0
                if dir_left:
                    a_line = int(alpha_base * u)
                else:
                    a_line = int(alpha_base * (1.0 - u))
                for y in range(h):
                    r, g, b, _ = base.get_at((x, y))
                    base.set_at((x, y), (r, g, b, a_line))
            base.unlock()
        except Exception:
            pass
        self._faded_cache[key] = base
        return base

    def _get_preview(self, idx: int, gray: bool) -> pygame.Surface:
        char = self.characters[idx]
        key = (idx, gray)
        cache = self.preview_gray if gray else self.preview_color
        if key in cache:
            return cache[key]
        path = char.get('preview_path') or char.get('icon_path')
        try:
            img = pygame.image.load(path).convert_alpha()
        except Exception:
            # fallback: 使用 icon
            img = pygame.image.load(char.get('icon_path')).convert_alpha()
        # 調整至側邊預留區域（20% 邊界內），並放大 1.3 倍
        base_w = int(self.left_margin * 0.9)
        target_w = int(base_w * 1.3)
        scale = target_w / img.get_width()
        target_h = int(img.get_height() * scale)
        img = pygame.transform.smoothscale(img, (target_w, target_h))
        if gray:
            img = self._to_grayscale(img)
        cache[key] = img
        return img

    def draw_text_with_outline(self, surface, text, font, color, outline_color, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    outline_surface = font.render(text, True, outline_color)
                    surface.blit(outline_surface, (x + dx, y + dy))
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def _index_to_pos(self, idx):
        col = idx % 3
        row = idx // 3
        x = self.grid_start_x + col * (self.card_w + self.card_spacing_x)
        y = self.grid_start_y + row * (self.card_h + self.card_spacing_y)
        return x, y
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                if not self.animating:
                    self.animating = True
                    self.anim_dir = -1
                    self.anim_start = pygame.time.get_ticks()
                    self.slide_offset = 0.0
                audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if not self.animating:
                    self.animating = True
                    self.anim_dir = 1
                    self.anim_start = pygame.time.get_ticks()
                    self.slide_offset = 0.0
                audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.focus_index = (self.focus_index - 3) % len(self.characters)
                audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.focus_index = (self.focus_index + 3) % len(self.characters)
                audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.current_player == 1:
                    self.player1_character = self.focus_index
                    self.player1_locked = True
                    self.current_player = 2
                    if self.player2_character == self.player1_character:
                        self.focus_index = (self.focus_index + 1) % len(self.characters)
                    audio_manager.play_sound(SOUND_EFFECTS["option_confirmed"])
                else:
                    self.player2_character = self.focus_index
                    self.player2_locked = True
                    audio_manager.play_sound(SOUND_EFFECTS["option_confirmed"])
                    return "MODEL_SELECT"
            elif event.key == pygame.K_ESCAPE:
                # 取消當前選角：回到主選單時重設狀態
                self.current_player = 1
                self.focus_index = 0
                self.player1_locked = False
                self.player2_locked = False
                self.player1_character = 0
                self.player2_character = 1 if len(self.characters) > 1 else 0
                return "MAIN_MENU"
        return None
    
    def get_selections(self):
        return {
            "player1_character": self.player1_character,
            "player2_character": self.player2_character,
        }

    def draw(self, surface):
        # 背景（先底色，若有背景圖再覆蓋）
        surface.fill((20, 20, 40))
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        
        # 標題
        title_text = "角色選擇"
        title_surface = self.title_font.render(title_text, True, self.YELLOW)
        title_rect = title_surface.get_rect()
        title_x = (self.screen_width - title_rect.width) // 2
        self.draw_text_with_outline(surface, title_text, self.title_font, self.YELLOW, self.BLACK, title_x, 30)

        # 左上角狀態已由預覽大圖取代（移除即時提示）

        # 取消左下角屬性（改置中顯示於中央卡片下方）

        # Carousel 繪製
        now = pygame.time.get_ticks()
        if self.animating:
            t = min(1.0, (now - self.anim_start) / self.anim_duration)
            # ease in-out
            ease = t * t * (3 - 2 * t)
            self.slide_offset = -self.anim_dir * ease
            if t >= 1.0:
                self.animating = False
                # 完成一次滑動：更新焦點並重置偏移
                self.focus_index = (self.focus_index + self.anim_dir) % len(self.characters)
                self.slide_offset = 0.0

        visible_range = [-2, -1, 0, 1, 2]
        for rel in visible_range:
            idx = (self.focus_index + rel) % len(self.characters)
            # 判斷縮放：中央 1.5x，其餘 0.6x（在過渡中以 slide_offset 判定中心）
            pos_eval = rel + self.slide_offset
            is_center = abs(pos_eval) < 0.5
            scale = self.center_scale if is_center else self.side_scale
            draw_w = int(self.card_img_w * scale)
            draw_h = int(self.card_img_h * scale)
            # 位置：均勻水平排列，居中
            cx = self.carousel_center_x + int((rel + self.slide_offset) * self.carousel_spacing)
            x = cx - draw_w // 2
            y = self.carousel_y + (self.card_img_h - draw_h) // 2

            # 彩色/灰階：被任一玩家選定或是中心（正在選）→ 彩色
            is_locked_p1 = self.player1_locked and idx == self.player1_character
            is_locked_p2 = self.player2_locked and idx == self.player2_character
            colored = is_center or is_locked_p1 or is_locked_p2
            img_src = self.icons_color[idx] if colored else self.icons_gray[idx]
            if is_center:
                img = pygame.transform.smoothscale(img_src, (draw_w, draw_h))
                surface.blit(img, (x, y))
                # 名稱與屬性固定在視覺中心，不隨動畫位移
                fixed_cx = self.carousel_center_x
                fixed_y_top = self.carousel_y
                name = self.characters[idx]['display_name']
                name_surface = self.name_font_small.render(name, True, self.WHITE)
                name_rect = name_surface.get_rect(center=(fixed_cx, fixed_y_top + int(self.card_img_h * self.center_scale) + 8 + name_surface.get_height() // 2))
                surface.blit(name_surface, name_rect)
                # 屬性條（類似格鬥遊戲資訊視窗）
                atk = self.characters[idx]['atk']
                defense = self.characters[idx]['def']
                hp = self.characters[idx]['hp']
                stats_text = f"ATK {atk}   DEF {defense}   HP {hp}"
                stats_surface = self.desc_font.render(stats_text, True, self.WHITE)
                stats_rect = stats_surface.get_rect(center=(fixed_cx, name_rect.bottom + 20))
                # 背板
                pad_x, pad_y = 10, 6
                bg_w = stats_rect.width + pad_x * 2
                bg_h = stats_rect.height + pad_y * 2
                bg_x = stats_rect.centerx - bg_w // 2
                bg_y = stats_rect.centery - bg_h // 2
                pygame.draw.rect(surface, (0, 0, 0), (bg_x, bg_y, bg_w, bg_h))
                pygame.draw.rect(surface, self.YELLOW, (bg_x, bg_y, bg_w, bg_h), 2)
                surface.blit(stats_surface, stats_rect)
                # 焦點高亮（中央 item）
                blink = (pygame.time.get_ticks() // 300) % 2
                col = self.YELLOW if blink else self.WHITE
                pygame.draw.rect(surface, col, (x - 6, y - 6, draw_w + 12, draw_h + 12), 3)
            else:
                # 兩側採用灰階 + 半透明 + 邊緣漸層透明，中央為最大不透明度，距離中心愈遠愈透明
                dist_from_center = min(2.0, abs(pos_eval)) / 2.0  # 0..1
                alpha_base = int(200 * (1.0 - 0.7 * dist_from_center))  # 中央~200，最遠~60
                faded = self._get_faded_image(idx, draw_w, draw_h, alpha_base, dir_left=(rel < 0))
                surface.blit(faded, (x, y))

        # 提示（置中下方一行式）
        tip_text = "WASD/方向鍵: 移動 | Enter/Space: 確認 | ESC: 返回主選單"
        tip_surface = self.desc_font.render(tip_text, True, self.WHITE)
        tip_x = (self.screen_width - tip_surface.get_width()) // 2
        tip_y = self.screen_height - tip_surface.get_height() - 30
        surface.blit(tip_surface, (tip_x, tip_y))

                # 左右預覽大圖：
        # 左側：若 P1 正在選或已鎖定，顯示（未鎖定灰階，鎖定彩色，並在 P2 階段保持顯示）
        if self.current_player == 1 or self.player1_locked:
            if self.player1_locked:
                idx_left = self.player1_character
                gray_left = False
            else:
                idx_left = self.focus_index
                gray_left = True
            preview_left = self._get_preview(idx_left, gray=gray_left)
            px_left = int(self.left_margin * 0.02)
            # 預覽往上移 3 行（含留白）高度，讓下方資訊框更寬鬆
            line_h = self.player_font_small.get_height()
            shift_y = line_h * 3 + 20
            py_left = max(0, (self.screen_height - preview_left.get_height()) // 2 - shift_y)
            surface.blit(preview_left, (px_left, py_left))
            # 預覽下方多行標籤：第一行固定 Player 1，角色名每 10 字一行，總行數最多 3 行
            left_title = "Player 1"
            left_name = self.characters[idx_left]['display_name'] if idx_left < len(self.characters) else '未選擇'
            def chunk_by_n(txt, n):
                return [txt[i:i+n] for i in range(0, len(txt), n)] if txt else [""]
            name_lines = chunk_by_n(left_name, 10)
            # 限制總行數最多 3 行（含標題），故名稱最多 2 行
            name_lines = name_lines[: max(0, 3 - 1)]
            left_lines = [left_title] + name_lines
            # 固定框寬為 11 個中文字的寬度
            fixed_w = self.player_font_small.size("漢" * 11)[0]
            line_surfaces = [self.player_font_small.render(ln, True, self.WHITE) for ln in left_lines]
            block_h = sum(s.get_height() for s in line_surfaces) + (len(line_surfaces)-1)*4
            lx_left = px_left + (preview_left.get_width() - fixed_w) // 2
            ly_left = py_left + preview_left.get_height() + 12
            pygame.draw.rect(surface, (0,0,0), (lx_left - 12, ly_left - 10, fixed_w + 24, block_h + 20))
            pygame.draw.rect(surface, self.BLUE, (lx_left - 12, ly_left - 10, fixed_w + 24, block_h + 20), 2)
            cy = ly_left
            for s in line_surfaces:
                # 每行文字在固定寬度內水平置中
                sx = lx_left + (fixed_w - s.get_width()) // 2
                surface.blit(s, (sx, cy))
                cy += s.get_height() + 4

        # 右側：若 P2 正在選或已鎖定，顯示（同理保持顯示）
        if self.current_player == 2 or self.player2_locked:
            if self.player2_locked:
                idx_right = self.player2_character
                gray_right = False
            else:
                idx_right = self.focus_index
                gray_right = True
            preview_right = self._get_preview(idx_right, gray=gray_right)
            px_right = self.right_margin + int(self.left_margin * 0.98) - preview_right.get_width()
            # 同樣往上移 3 行高度
            line_h = self.player_font_small.get_height()
            shift_y = line_h * 3 + 20
            py_right = max(0, (self.screen_height - preview_right.get_height()) // 2 - shift_y)
            surface.blit(preview_right, (px_right, py_right))
            # 預覽下方多行標籤：第一行固定 Player 2，角色名每 10 字一行，總行數最多 3 行
            right_title = "Player 2"
            right_name = self.characters[idx_right]['display_name'] if idx_right < len(self.characters) else '未選擇'
            def chunk_by_n2(txt, n):
                return [txt[i:i+n] for i in range(0, len(txt), n)] if txt else [""]
            r_name_lines = chunk_by_n2(right_name, 10)
            r_name_lines = r_name_lines[: max(0, 3 - 1)]
            right_lines = [right_title] + r_name_lines
            fixed_w_r = self.player_font_small.size("漢" * 11)[0]
            r_surfaces = [self.player_font_small.render(ln, True, self.WHITE) for ln in right_lines]
            r_block_h = sum(s.get_height() for s in r_surfaces) + (len(r_surfaces)-1)*4
            lx_right = px_right + (preview_right.get_width() - fixed_w_r) // 2
            ly_right = py_right + preview_right.get_height() + 12
            pygame.draw.rect(surface, (0,0,0), (lx_right - 12, ly_right - 10, fixed_w_r + 24, r_block_h + 20))
            pygame.draw.rect(surface, self.RED, (lx_right - 12, ly_right - 10, fixed_w_r + 24, r_block_h + 20), 2)
            cy = ly_right
            for s in r_surfaces:
                sx = lx_right + (fixed_w_r - s.get_width()) // 2
                surface.blit(s, (sx, cy))
                cy += s.get_height() + 4

