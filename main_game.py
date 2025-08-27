import asyncio
import pygame

from font_manager import font_manager
from audio_manager import audio_manager, SOUND_EFFECTS, BACKGROUND_MUSIC
from menu import GameMenu, CharacterSelectMenu
from model_selection_menu import ModelSelectionMenu
from character_loader import character_loader
from llm_fighter import LLMFighter
from simple_ai import MockLLMPipeline
from model_config import get_model_info


async def main():
    pygame.init()

    # Window settings
    GAME_WIDTH = 800
    GAME_HEIGHT = 500
    BORDER_LEFT = 180
    BORDER_RIGHT = 180
    BORDER_TOP = 40
    BORDER_BOTTOM = 120
    SCREEN_WIDTH = GAME_WIDTH + BORDER_LEFT + BORDER_RIGHT
    SCREEN_HEIGHT = GAME_HEIGHT + BORDER_TOP + BORDER_BOTTOM

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("黃巧君 Fight ! - AI 格鬥遊戲")
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

    clock = pygame.time.Clock()
    FPS = 60

    # Colors
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 100, 255)

    # Menus
    main_menu = GameMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
    char_menu = CharacterSelectMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
    model_menu = ModelSelectionMenu(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Audio
    audio_manager.play_music(BACKGROUND_MUSIC["menu"])

    # Game state
    game_state = "MAIN_MENU"  # MAIN_MENU, CHARACTER_SELECT, MODEL_SELECT, GAME, GAME_OVER

    # Fonts
    count_font = font_manager.get_font("your_custom_font.ttf", size=80)
    score_font = font_manager.get_font("your_custom_font.ttf", size=30)
    game_over_font = font_manager.get_font("your_custom_font.ttf", size=60)
    option_font = font_manager.get_font("your_custom_font.ttf", size=40)
    action_font = font_manager.get_font("your_custom_font.ttf", size=18)
    small_font = font_manager.get_font("your_custom_font.ttf", size=16)

    # Load art
    try:
        bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()
    except Exception:
        bg_image = None
    try:
        victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()
    except Exception:
        victory_img = None

    # Fighters & round state
    fighter_1 = None
    fighter_2 = None
    score = [0, 0]
    round_over = False
    victory_sound_played = False
    intro_count = 3
    last_count_update = pygame.time.get_ticks()
    timer = 99
    round_over_time = 0
    game_over_selected = 0
    game_over_options = ["Again", "Back to Menu"]
    # 轉場排程
    pending_transition = None  # dict: {to, delay_ms, kind}
    post_fade_action = None    # 在淡入完成後執行的延後動作（避免提前觸發音效/互動）
    # 共用的過場淡入/淡出
    def fade_out(duration_ms=1000, draw_cb=None):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        start = pygame.time.get_ticks()
        while True:
            elapsed = pygame.time.get_ticks() - start
            t = min(1.0, elapsed / duration_ms)
            # 先繪製目前畫面，再覆蓋漸黑圖層
            if draw_cb is not None:
                draw_cb()
            overlay.set_alpha(int(255 * t))
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            pygame.display.update()
            if t >= 1.0:
                break

    def fade_in(duration_ms=1000, draw_cb=None):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        start = pygame.time.get_ticks()
        while True:
            elapsed = pygame.time.get_ticks() - start
            t = min(1.0, elapsed / duration_ms)
            # 先繪製目標畫面，再覆蓋由黑轉透明圖層
            if draw_cb is not None:
                draw_cb()
            overlay.set_alpha(int(255 * (1.0 - t)))
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            pygame.display.update()
            if t >= 1.0:
                break
    # 回合總結/下一回合提示
    p1_prompt_extra = ""
    p2_prompt_extra = ""
    last_round_p1_hp = 0
    last_round_p2_hp = 0
    last_round_winner = None  # 1, 2, or None

    # Animation constants (use warrior defaults for compatibility)
    WARRIOR_DATA = [162, 4, [72, 56]]
    WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]

    def draw_text(surface, text, font, color, x, y):
        img = font.render(text, True, color)
        surface.blit(img, (x, y))

    def draw_text_with_outline(surface, text, font, color, outline_color, x, y):
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    outline_surface = font.render(text, True, outline_color)
                    surface.blit(outline_surface, (x + dx, y + dy))
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def draw_bg(surface):
        surface.fill((0, 0, 0))
        if bg_image:
            # letterbox center
            bg_scaled = pygame.transform.scale(bg_image, (GAME_WIDTH, GAME_HEIGHT))
            surface.blit(bg_scaled, (0, 0))

    def draw_health_bar(surface, health, x, y, width):
        ratio = max(0, min(1, health / 100))
        pygame.draw.rect(surface, WHITE, (x - 2, y - 2, width + 4, 34))
        pygame.draw.rect(surface, RED, (x, y, width, 30))
        pygame.draw.rect(surface, YELLOW, (x, y, int(width * ratio), 30))

    def draw_timer(surface, timer_value, y):
        t = max(0, int(timer_value))
        text = f"{t}"
        img = count_font.render(text, True, RED)
        centered_x = (GAME_WIDTH - img.get_width()) // 2
        surface.blit(img, (centered_x, y))
        return img.get_width()

    def draw_actions(surface, fighter, x, title_text):
        if fighter is None:
            return
        PADDING_X = 15
        PADDING_Y = 20
        LINE_HEIGHT = 22
        # 精確計算可用側欄寬度，避免覆蓋戰鬥區域
        if x < BORDER_LEFT:  # 左側欄
            sidebar_width = max(0, BORDER_LEFT - x)
        elif x >= BORDER_LEFT + GAME_WIDTH:  # 右側欄
            sidebar_width = max(0, BORDER_LEFT + GAME_WIDTH + BORDER_RIGHT - x)
        else:
            sidebar_width = 0
        if sidebar_width <= 0:
            return

        # 區塊：標題（Player）
        y_offset = BORDER_TOP + PADDING_Y
        player_surface = action_font.render("Player", True, WHITE)
        player_x = x + (sidebar_width - player_surface.get_width()) // 2
        draw_text(surface, "Player", action_font, WHITE, player_x, y_offset)
        y_offset += LINE_HEIGHT + 6

        # 區塊：中文角色名（位於 Player 下方），超過6字自動換行
        def wrap_cn_lines(txt: str, limit: int = 6):
            return [txt[i:i+limit] for i in range(0, len(txt), limit)] if txt else [""]
        name_lines = wrap_cn_lines(title_text, 6)
        for nm in name_lines:
            line_surface = small_font.render(nm, True, WHITE)
            nx = x + (sidebar_width - line_surface.get_width()) // 2
            surface.blit(line_surface, (nx, y_offset))
            y_offset += LINE_HEIGHT

        # 區塊：模型名（處理邊界斷詞）
        model_name = str(getattr(fighter, 'model', 'model'))
        # 模型名斷詞（安全省略）
        def ellipsis(text, font, max_width):
            if font.size(text)[0] <= max_width:
                return text
            while text and font.size(text + "…")[0] > max_width:
                text = text[:-1]
            return text + "…" if text else "…"
        model_shown = ellipsis(model_name, small_font, sidebar_width - PADDING_X * 2)
        model_line = small_font.render(model_shown, True, YELLOW)
        mx = x + (sidebar_width - model_line.get_width()) // 2
        surface.blit(model_line, (mx, y_offset))
        y_offset += LINE_HEIGHT + 8

        # Helper: 截斷單行為可視範圍
        def ellipsis(text, font, max_width):
            if font.size(text)[0] <= max_width:
                return text
            # 逐步縮短並加上省略號
            while text and font.size(text + "…")[0] > max_width:
                text = text[:-1]
            return text + "…" if text else "…"

        # Helper: 文字換行（支援無空格語言）
        def wrap_text(text, font, max_width, max_lines):
            lines = []
            if not text:
                return lines
            # 先以空白切分
            tokens = text.split()
            if len(tokens) <= 1:
                # 無空白情境，依字元切，中文每10字一行
                current = ""
                char_count = 0
                for ch in text:
                    if char_count < 10 and font.size((current + ch).strip())[0] <= max_width:
                        current += ch
                        char_count += 1
                    else:
                        lines.append(current.strip())
                        current = ch
                        char_count = 1
                        if len(lines) >= max_lines:
                            break
                if len(lines) < max_lines and current:
                    lines.append(current.strip())
                return lines[:max_lines]
            # 有空白，單詞換行
            line = ""
            for token in tokens:
                candidate = (line + " " + token).strip()
                if font.size(candidate)[0] <= max_width:
                    line = candidate
                else:
                    if line:
                        lines.append(line)
                    else:
                        # 單詞超長，強制截斷
                        token = ellipsis(token, font, max_width)
                        lines.append(token)
                    line = token if font.size(token)[0] <= max_width else ""
                if len(lines) >= max_lines:
                    break
            if len(lines) < max_lines and line:
                lines.append(line)
            return lines[:max_lines]

        # 區塊：動作列表（固定顯示最多 6 個，固定高度）
        list_title = small_font.render("動作列表", True, WHITE)
        list_x = x + (sidebar_width - list_title.get_width()) // 2
        surface.blit(list_title, (list_x, y_offset))
        y_offset += LINE_HEIGHT
        max_actions = 6
        actions_shown = 0
        if hasattr(fighter, 'action_queue') and fighter.action_queue:
            for i, action in enumerate(fighter.action_queue[:max_actions]):
                action_text = action.replace('_', ' ')
                # 保證單行不溢出
                action_text = ellipsis(action_text, small_font, sidebar_width - PADDING_X * 2 - 8)
                color = YELLOW if i == 0 else WHITE
                surface.blit(small_font.render(f"• {action_text}", True, color), (x + PADDING_X, y_offset))
                y_offset += LINE_HEIGHT
                actions_shown += 1
        # 補滿固定高度
        for _ in range(max_actions - actions_shown):
            y_offset += LINE_HEIGHT

        # 區塊：戰術分析（固定高度，多行截斷）
        y_offset += 6
        tac_title = small_font.render("戰術分析", True, WHITE)
        tac_x = x + (sidebar_width - tac_title.get_width()) // 2
        # 固定區塊背景避免殘影/位移
        TACTIC_LINES = 6  # 顯示更多行，減少被截斷
        TACTIC_HEIGHT = LINE_HEIGHT * (TACTIC_LINES + 2)
        # 畫背景框（在側欄內縮進，避免貼齊邊緣造成視覺溢出）
        inset = 8
        bg_rect = pygame.Rect(x + inset, y_offset - 2, max(0, sidebar_width - inset * 2), TACTIC_HEIGHT)
        pygame.draw.rect(surface, (10, 10, 30), bg_rect)
        surface.blit(tac_title, (tac_x, y_offset))
        y_offset += LINE_HEIGHT
        analysis = getattr(fighter, 'tactical_analysis', '') or ''
        if not analysis:
            thinking = "思考中..."
            thinking = ellipsis(thinking, small_font, max(0, sidebar_width - PADDING_X * 2))
            surface.blit(small_font.render(thinking, True, YELLOW), (x + PADDING_X, y_offset))
            # 佔位其餘行
            for _ in range(TACTIC_LINES - 1):
                y_offset += LINE_HEIGHT
        else:
            max_width = max(0, sidebar_width - PADDING_X * 2)
            lines = wrap_text(analysis, small_font, max_width, TACTIC_LINES)
            # 若超過，對最後一行加省略
            if len(lines) == TACTIC_LINES:
                lines[-1] = ellipsis(lines[-1], small_font, max_width)
            for ln in lines:
                surface.blit(small_font.render(ln, True, YELLOW), (x + PADDING_X, y_offset))
                y_offset += LINE_HEIGHT
            # 不足補滿固定高度
            for _ in range(TACTIC_LINES - len(lines)):
                y_offset += LINE_HEIGHT

    def draw_game_over_screen(surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        title = "Game Over"
        go_w, _ = game_over_font.size(title)
        go_x = (SCREEN_WIDTH - go_w) // 2
        go_y = SCREEN_HEIGHT // 3
        draw_text_with_outline(surface, title, game_over_font, RED, BLACK, go_x, go_y)
        winner_text = "Player 1 獲勝!" if score[0] > score[1] else ("Player 2 獲勝!" if score[1] > score[0] else "平手!")
        w_w, _ = option_font.size(winner_text)
        w_x = (SCREEN_WIDTH - w_w) // 2
        w_y = go_y + 100
        draw_text_with_outline(surface, winner_text, option_font, YELLOW, BLACK, w_x, w_y)
        menu_start_y = w_y + 100
        for i, option in enumerate(game_over_options):
            opt_w, _ = option_font.size(option)
            ox = (SCREEN_WIDTH - opt_w) // 2
            oy = menu_start_y + i * 60
            blink_state = (pygame.time.get_ticks() // 500) % 2
            color = WHITE if (i == game_over_selected and blink_state) else (YELLOW if i == game_over_selected else WHITE)
            draw_text_with_outline(surface, option, option_font, color, BLACK, ox, oy)

    def create_fighters(selections, model_selections):
        nonlocal fighter_1, fighter_2
        # Determine spritesheet and constants based on selected character
        def build_fighter(player_num, left_side, char_index, model_id):
            # 查詢角色
            char_ids = sorted(character_loader.characters.keys())
            if char_index < 0 or char_index >= len(char_ids):
                char_index = 0
            cid = char_ids[char_index]
            char_info = character_loader.get_character(cid)
            sprite_path = char_info['sprite_path']
            try:
                sheet = pygame.image.load(sprite_path).convert_alpha()
            except Exception:
                # 後備使用 Kate 的圖
                sheet = pygame.image.load("assets/images/characters/kate/sprites/warrior.png").convert_alpha()
            data = WARRIOR_DATA
            steps = WARRIOR_ANIMATION_STEPS
            start_margin_x = 50
            rect_w, rect_h = 80, 180
            ground_offset = 110
            start_y = GAME_HEIGHT - ground_offset - rect_h
            x = start_margin_x if left_side else GAME_WIDTH - start_margin_x - rect_w
            # 決定策略（若是 AWS 模型，根據其策略；否則預設）
            strategy = "balanced"
            model_info = get_model_info(model_id) if model_id else None
            if model_info and 'strategy' in model_info:
                strategy = model_info['strategy']
            mock_strategy = "defensive" if strategy == "defensive" else ("aggressive" if strategy == "aggressive" else "balanced")
            llm = MockLLMPipeline(mock_strategy)
            extra = p1_prompt_extra if player_num == 1 else p2_prompt_extra
            fighter = LLMFighter(
                player_num,
                x,
            start_y,
                not left_side,
                data,
                sheet,
                steps,
                model_id or "simple",
                f"You are a {strategy} player. {extra}",
                llm,
            )
            # 設定角色 ID，供側欄顯示中文名稱
            try:
                setattr(fighter, 'character_id', cid)
            except Exception:
                pass
            return fighter

        fighter_1 = build_fighter(1, True, selections["player1_character"], model_selections.get("player1_model"))
        fighter_2 = build_fighter(2, False, selections["player2_character"], model_selections.get("player2_model"))

    # game loop
    run = True
    selections = None
    model_selections = None
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if game_state == "MAIN_MENU":
                result = main_menu.handle_input(event)
                if result == "CHARACTER_SELECT":
                    pending_transition = {"to": "CHARACTER_SELECT", "delay_ms": 0, "kind": "simple"}
                elif result == "QUIT":
                    run = False
            
            elif game_state == "CHARACTER_SELECT":
                result = char_menu.handle_input(event)
                if result == "MODEL_SELECT":
                    pending_transition = {"to": "MODEL_SELECT", "delay_ms": 750, "kind": "char_to_model"}
                elif result == "MAIN_MENU":
                    pending_transition = {"to": "MAIN_MENU", "delay_ms": 0, "kind": "simple"}

            elif game_state == "MODEL_SELECT":
                result = model_menu.handle_input(event)
                if result == "START_GAME":
                    pending_transition = {"to": "GAME", "delay_ms": 300, "kind": "model_to_game"}
                elif result == "CHARACTER_SELECT":
                    pending_transition = {"to": "CHARACTER_SELECT", "delay_ms": 0, "kind": "reset_char"}

        # 若有排程轉場，統一在此執行，避免層級/時序錯誤
        if pending_transition is not None:
            delay_ms = pending_transition.get("delay_ms", 0)
            to_state = pending_transition.get("to")
            kind = pending_transition.get("kind")
            # 先確保目前畫面已完整繪製一次（避免殘影），再進入保留/延遲
            if game_state == "MAIN_MENU":
                main_menu.draw(screen)
            elif game_state == "CHARACTER_SELECT":
                char_menu.draw(screen)
            elif game_state == "MODEL_SELECT":
                model_menu.draw(screen)
            elif game_state == "GAME":
                screen.fill((0, 0, 0))
                screen.blit(game_surface, (BORDER_LEFT, BORDER_TOP))
            pygame.display.update()
            if delay_ms > 0:
                pygame.time.delay(delay_ms)
            # 動畫持續 2000ms，淡出/淡入之間不再額外等待
            # 在淡出與淡入時，每一幀都回呼繪製函式，避免閃爍
            def draw_current():
                if game_state == "MAIN_MENU":
                    main_menu.draw(screen)
                elif game_state == "CHARACTER_SELECT":
                    char_menu.draw(screen)
                elif game_state == "MODEL_SELECT":
                    model_menu.draw(screen)
                elif game_state == "GAME":
                    screen.fill((0, 0, 0))
                    screen.blit(game_surface, (BORDER_LEFT, BORDER_TOP))
            fade_out(1000, draw_cb=draw_current)

            # 執行狀態切換與初始化
            if kind == "char_to_model":
                selections = char_menu.get_selections()
                model_menu = ModelSelectionMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
                game_state = "MODEL_SELECT"
                # 預繪目標畫面
                model_menu.draw(screen)
            elif kind == "model_to_game":
                model_selections = model_menu.get_selections()
                if not model_selections.get("player1_model") and model_menu.model_list:
                    model_selections["player1_model"] = model_menu.model_list[0]
                if not model_selections.get("player2_model") and model_menu.model_list:
                    model_selections["player2_model"] = model_menu.model_list[-1]
                create_fighters(selections, model_selections)
                # 重置回合狀態
                score = [0, 0]
                round_over = False
                victory_sound_played = False
                intro_count = 3
                last_count_update = pygame.time.get_ticks()
                timer = 99
                game_state = "GAME"
                # 預繪一幀遊戲背景以供淡入
                draw_bg(game_surface)
                screen.fill((0, 0, 0))
                screen.blit(game_surface, (BORDER_LEFT, BORDER_TOP))
                # 淡入完成後再觸發音效與重設倒數基準，避免動畫期間啟動
                post_fade_action = "start_game_audio"
            elif kind == "reset_char":
                # 從模型選擇返回角色選擇時重置狀態
                char_menu = CharacterSelectMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
                game_state = "CHARACTER_SELECT"
                char_menu.draw(screen)
            elif kind == "simple":
                game_state = to_state
                if to_state == "CHARACTER_SELECT":
                    char_menu.draw(screen)
                elif to_state == "MAIN_MENU":
                    main_menu.draw(screen)
                elif to_state == "MODEL_SELECT":
                    model_menu.draw(screen)

            def draw_target():
                if game_state == "MAIN_MENU":
                    main_menu.draw(screen)
                elif game_state == "CHARACTER_SELECT":
                    char_menu.draw(screen)
                elif game_state == "MODEL_SELECT":
                    model_menu.draw(screen)
                elif game_state == "GAME":
                    screen.fill((0, 0, 0))
                    screen.blit(game_surface, (BORDER_LEFT, BORDER_TOP))
            fade_in(1000, draw_cb=draw_target)

            # 淡入完成後延後動作（只在需要時觸發）
            if post_fade_action == "start_game_audio":
                audio_manager.play_sound(SOUND_EFFECTS["game_start"])
                audio_manager.play_music(BACKGROUND_MUSIC["game"])
                # 將倒數時間基準重設為此刻，確保淡入前的時間不會吃到倒數
                last_count_update = pygame.time.get_ticks()
                post_fade_action = None

            pending_transition = None
            continue

        elif game_state == "GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        game_over_selected = (game_over_selected - 1) % len(game_over_options)
                        audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game_over_selected = (game_over_selected + 1) % len(game_over_options)
                        audio_manager.play_sound(SOUND_EFFECTS["option_switch"])
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        audio_manager.play_sound(SOUND_EFFECTS["option_confirmed"])
                        if game_over_selected == 0:
                            # Again -> go character select
                            audio_manager.play_music(BACKGROUND_MUSIC["menu"])  # back to menu BGM before new game
                            char_menu = CharacterSelectMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
                            game_state = "CHARACTER_SELECT"
                        else:
                            audio_manager.play_music(BACKGROUND_MUSIC["menu"])  # switch back to menu BGM
                            game_state = "MAIN_MENU"

        # Render by state
        if game_state == "MAIN_MENU":
            main_menu.update()
            main_menu.draw(screen)
        
        elif game_state == "CHARACTER_SELECT":
            char_menu.draw(screen)

        elif game_state == "MODEL_SELECT":
            model_menu.draw(screen)
        
        elif game_state == "GAME":
            # draw background
            draw_bg(game_surface)

            # center timer and compute gap
            timer_width = draw_timer(game_surface, timer, 10)
            gap = int(timer_width * 1.4)
            side_total_width = (GAME_WIDTH - gap) // 2
            padding_x = 20
            bar_width = max(200, side_total_width - padding_x * 2)

            # left and right hp bars
            left_hp_x = padding_x
            draw_health_bar(game_surface, fighter_1.health, left_hp_x, 20, bar_width)
            right_hp_x = GAME_WIDTH - padding_x - bar_width
            draw_health_bar(game_surface, fighter_2.health, right_hp_x, 20, bar_width)

            # scores 與玩家標題（不再顯示狀態文字以避免重疊）
            p1_text = f"Player1 | 勝場數：{score[0]}"
            draw_text(game_surface, p1_text, score_font, RED, left_hp_x, 60)
            p2_text = f"Player2 | 勝場數：{score[1]}"
            p2_w, _ = score_font.size(p2_text)
            draw_text(game_surface, p2_text, score_font, RED, right_hp_x + bar_width - p2_w, 60)

            # intro count or run
            if intro_count <= 0:
                await fighter_1.move(GAME_WIDTH, GAME_HEIGHT, fighter_2, round_over)
                await fighter_2.move(GAME_WIDTH, GAME_HEIGHT, fighter_1, round_over)
            else:
                draw_text(game_surface, str(intro_count), count_font, RED, GAME_WIDTH // 2 - 20, GAME_HEIGHT // 3)
                if (pygame.time.get_ticks() - last_count_update) >= 1000:
                    intro_count -= 1
                    last_count_update = pygame.time.get_ticks()

            # update fighters & draw
            fighter_1.update()
            fighter_2.update()
            fighter_1.draw(game_surface)
            fighter_2.draw(game_surface)

            # check defeat
            if not round_over:
                if not fighter_1.alive:
                    score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
                elif not fighter_2.alive:
                    score[0] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()

                if timer == 0 and not round_over:
                    if fighter_1.health > fighter_2.health:
                        score[0] += 1
                    elif fighter_2.health > fighter_1.health:
                        score[1] += 1
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
            else:
                if victory_img:
                    v_w = victory_img.get_width()
                    v_h = victory_img.get_height()
                    v_x = (GAME_WIDTH - v_w) // 2
                    v_y = (GAME_HEIGHT - v_h) // 2
                    game_surface.blit(victory_img, (v_x, v_y))
                    if not victory_sound_played:
                        audio_manager.play_sound(SOUND_EFFECTS["victory"])
                        victory_sound_played = True
                if pygame.time.get_ticks() - round_over_time > 2000:
                    # check match over (best of 3)
                    if score[0] >= 2 or score[1] >= 2:
                        game_state = "GAME_OVER"
                    else:
                        # next round wait prompt
                        waiting = True
                        info_font = font_manager.get_font("your_custom_font.ttf", size=36)
                        # 紀錄上一回合結果供總結
                        last_round_p1_hp = fighter_1.health
                        last_round_p2_hp = fighter_2.health
                        if score[0] > score[1]:
                            last_round_winner = 1
                        elif score[1] > score[0]:
                            last_round_winner = 2
                        else:
                            last_round_winner = None
                        while waiting:
                            screen.fill((0, 0, 0))
                            screen.blit(game_surface, (BORDER_LEFT, BORDER_TOP))
                            msg = "Next Round - Press Enter"
                            w, _ = info_font.size(msg)
                            x = (SCREEN_WIDTH - w) // 2
                            y = SCREEN_HEIGHT // 2
                            draw_text_with_outline(screen, msg, info_font, YELLOW, BLACK, x, y)
                            pygame.display.update()
                            for ev in pygame.event.get():
                                if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                                    audio_manager.play_sound(SOUND_EFFECTS["option_confirmed"])
                                    waiting = False
                                if ev.type == pygame.QUIT:
                                    waiting = False
                                    run = False
                                    break
                        if run:
                            # 生成回合總結文字並注入下一回合 prompt
                            if last_round_winner == 1:
                                p1_prompt_extra = (
                                    f"上一回合你獲勝。你的剩餘HP {last_round_p1_hp}，對手HP {last_round_p2_hp}。"
                                    "維持優勢：距離足夠時果斷攻擊；若對手逼近，考慮 JUMP_BEHIND 後反擊。"
                                )
                                p2_prompt_extra = (
                                    f"上一回合你落敗。你的剩餘HP {last_round_p2_hp}，對手HP {last_round_p1_hp}。"
                                    "調整策略：進入有效距離再出手，避免揮空；常被貼身時多用 MOVE_AWAY 或 JUMP_BEHIND。"
                                )
                            elif last_round_winner == 2:
                                p2_prompt_extra = (
                                    f"上一回合你獲勝。你的剩餘HP {last_round_p2_hp}，對手HP {last_round_p1_hp}。"
                                    "維持優勢：距離足夠時果斷攻擊；若對手逼近，考慮 JUMP_BEHIND 後反擊。"
                                )
                                p1_prompt_extra = (
                                    f"上一回合你落敗。你的剩餘HP {last_round_p1_hp}，對手HP {last_round_p2_hp}。"
                                    "調整策略：進入有效距離再出手，避免揮空；常被貼身時多用 MOVE_AWAY 或 JUMP_BEHIND。"
                                )
                            else:
                                p1_prompt_extra = (
                                    f"上一回合平手。你的HP {last_round_p1_hp}，對手HP {last_round_p2_hp}。"
                                    "優化命中率：先判斷距離再出手，避免揮空。"
                                )
                                p2_prompt_extra = (
                                    f"上一回合平手。你的HP {last_round_p2_hp}，對手HP {last_round_p1_hp}。"
                                    "優化命中率：先判斷距離再出手，避免揮空。"
                                )
                            round_over = False
                            intro_count = 3
                            last_count_update = pygame.time.get_ticks()
                            timer = 99
                            victory_sound_played = False
                            # 重新建立新回合戰士，避免上一回合死亡狀態殘留
                            if selections is not None and model_selections is not None:
                                create_fighters(selections, model_selections)

            # timer countdown
            if intro_count <= 0 and not round_over:
                if (pygame.time.get_ticks() - last_count_update) >= 1000:
                    timer -= 1
                    last_count_update = pygame.time.get_ticks()

            # compose to screen
            screen.fill((0, 0, 0))
            screen.blit(game_surface, (BORDER_LEFT, BORDER_TOP))
            # 側欄顯示角色名稱與模型（移除 HP/狀態文字）
            # 角色名稱由角色載入器取得
            p1_name = "Player 1"
            p2_name = "Player 2"
            try:
                if hasattr(fighter_1, 'character_id'):
                    char1 = character_loader.get_character(getattr(fighter_1, 'character_id'))
                    if char1:
                        p1_name = char1.get('display_name') or p1_name
                if hasattr(fighter_2, 'character_id'):
                    char2 = character_loader.get_character(getattr(fighter_2, 'character_id'))
                    if char2:
                        p2_name = char2.get('display_name') or p2_name
            except Exception:
                pass
            # 名稱換行：每 6 個中文字自動換行（簡化處理：每 6 字切一行）
            def wrap_cn(name: str, limit: int = 6):
                return [name[i:i+limit] for i in range(0, len(name), limit)] if name else [""]
            # 將多行名稱組合顯示（傳給 draw_actions 的 title 仍保留第一行；其餘行在內部渲染下方）
            draw_actions(screen, fighter_1, 10, p1_name)
            draw_actions(screen, fighter_2, BORDER_LEFT + GAME_WIDTH + 10, p2_name)
        
        elif game_state == "GAME_OVER":
            screen.fill((0, 0, 0))
            screen.blit(game_surface, (BORDER_LEFT, BORDER_TOP))
            draw_actions(screen, fighter_1, 10, "Player 1")
            draw_actions(screen, fighter_2, BORDER_LEFT + GAME_WIDTH + 10, "Player 2")
            draw_game_over_screen(screen)

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    print("啟動 黃巧君 Fight ! 遊戲")
    asyncio.run(main())


