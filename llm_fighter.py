import asyncio
import re
import time

import pygame
from typing import Any
from audio_manager import audio_manager, SOUND_EFFECTS
from game_actions import VALID_ACTIONS  # 使用統一的動作集合
from bedrock_client import bedrock_client

MAX_HEALTH = 100
# 戰術分析呼叫間隔（毫秒）
MODEL_COOLDOWN = 1500
# 執行動作彈出間隔（毫秒）
ACTION_EXECUTION_COOLDOWN = 320
# 單一動作最小持續時間（毫秒）
MIN_ACTION_DURATION_MS = 140
class LLMFighter:
    def __init__(
        self,
        player,
        x,
        y,
        flip,
        data,
        sprite_sheet,
        animation_steps,
        model,
        system_prompt,
        llm_pipeline: Any,
    ):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0  # 0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.knockback_frames = 0
        self.knockback_vel_x = 0
        self.jump_dash_frames = 0
        self.jump_dash_dir = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.hit = False
        self.health = MAX_HEALTH
        self.alive = True
        self.model = model
        self.system_prompt = system_prompt
        self.llm_pipeline = llm_pipeline
        self.last_action = None
        self.action_queue = []
        self.last_model_call_time = None
        self.tactical_analysis = ""  # 最近一次模型的戰術分析
        self.last_action_exec_time = None
        self.last_action_name = None
        # 連續移動狀態，避免動作列表被 MOVE 佔滿
        self.continuous_move_mode = None  # "towards" | "away" | None
        self.continuous_move_until = 0

    # --- 距離與攻擊範圍判定工具 ---
    def get_distance_x(self, target) -> int:
        return abs(self.rect.centerx - target.rect.centerx)

    def get_effective_range_for_action(self, action: str) -> int:
        # 視覺上角色寬約 80，給定略大的有效距離避免頻繁揮空
        if action in ("ATTACK1", "DASH_ATTACK"):
            return 170
        if action in ("ATTACK2", "COUNTER_ATTACK"):
            return 160
        if action == "ATTACK3":
            return 150
        return 0

    def is_in_attack_range(self, target, action: str) -> bool:
        rng = self.get_effective_range_for_action(action)
        return self.get_distance_x(target) <= rng

    def load_images(self, sprite_sheet, animation_steps):
        """自動偵測來源表的格子大小，並統一縮放到遊戲設計尺寸。

        規則：
        - 以列數 rows 決定 tile_h = sheet_h // rows。
        - 以各列最大影格數 max_frames 近似估算 tile_w_candidate = sheet_w // max_frames。
        - 取 tile_w = min(tile_h, tile_w_candidate) 以維持方格並避免越界。
        - 每格切片後統一縮放到 out_px = self.size * self.image_scale（與原專案一致）。
        - 固定輸出尺寸，避免跑步/攻擊切幀位移抖動；同時容納不同來源圖放大倍率。
        """
        sheet_w = sprite_sheet.get_width()
        sheet_h = sprite_sheet.get_height()
        rows = max(1, len(animation_steps))
        tile_h = max(1, sheet_h // rows)
        try:
            max_frames = max(1, max(int(n) for n in animation_steps))
        except Exception:
            max_frames = 1
        tile_w_candidate = max(1, sheet_w // max_frames)
        tile_w = min(tile_h, tile_w_candidate)
        out_px = int(self.size * self.image_scale)

        animation_list = []
        for y, frames in enumerate(animation_steps):
            temp_img_list = []
            steps_in_row = max(1, int(frames))
            for x in range(steps_in_row):
                src_x = x * tile_w
                src_y = y * tile_h
                if src_x + tile_w > sheet_w or src_y + tile_h > sheet_h:
                    break
                sub = sprite_sheet.subsurface(src_x, src_y, tile_w, tile_h)
                scaled = pygame.transform.smoothscale(sub, (out_px, out_px))
                temp_img_list.append(scaled)
            animation_list.append(temp_img_list)
        return animation_list

    async def add_llm_actions_to_queue(self, full_system_prompt, target=None):
        """向模型請求戰術與動作，並更新佇列與戰術分析。"""
        # 判定是否使用 Bedrock
        is_bedrock = (
            isinstance(self.model, str)
            and ("amazon." in self.model or "anthropic." in self.model)
        )

        if is_bedrock and target is not None and getattr(bedrock_client, "available", False):
            # 透過 Bedrock 取得戰術分析與動作
            try:
                result = await bedrock_client.invoke_model(
                    self.model,
                    self.build_system_prompt_with_roles(target),
                    self.context_prompt(target) + self.pending_actions_context(),
                    self.player,
                )
                if result is not None:
                    actions, tactical, clear_queue = result
                    # 過濾有效動作（不再重複擴增 MOVE_*）
                    valid_moves = [a for a in actions if a in VALID_ACTIONS]
                    # 新戰術到來，一律刷新佇列（即使模型未標記 CLEAR_QUEUE）
                    self.action_queue = []
                    self.action_queue.extend(valid_moves)
                    self.tactical_analysis = tactical or ""
                    print(f"✅ Bedrock 取得 {len(valid_moves)} 個動作，戰術：{self.tactical_analysis}")
                    return valid_moves
            except Exception as e:
                print(f"❌ Bedrock 請求失敗，改用本地策略: {e}")

        # Fallback：HuggingFace 或 Mock pipeline
        prompt = f"{full_system_prompt}\nYour next moves are:"
        result = await asyncio.to_thread(
            self.llm_pipeline,
            prompt,
            max_new_tokens=50,
        )

        actions_text = result[0]["generated_text"][len(prompt) :]

        print(f"{self.model} response:")
        print(actions_text)

        # The response is a bullet point list of moves. Use regex
        matches = re.findall(r"- ([\w ]+)", actions_text)
        moves = ["".join(match) for match in matches]
        invalid_moves = []
        valid_moves = []

        # add valid moves to action queue（不擴增 MOVE_*）
        for move in moves:
            if move in VALID_ACTIONS:
                valid_moves.append(move)
            else:
                invalid_moves.append(move)

        # 新策略（fallback）也刷新佇列
        self.action_queue = []
        self.action_queue.extend(valid_moves)
        # 合成一段簡短戰術分析（以遊戲上下文推測）
        if target is not None:
            try:
                self.tactical_analysis = self.context_prompt(target)
            except Exception:
                self.tactical_analysis = "保持距離或主動進攻，尋找破綻。"
        else:
            self.tactical_analysis = "保持距離或主動進攻，尋找破綻。"

        return valid_moves

    def context_prompt(self, target) -> str:
        """
        Return a str of the context
        """

        # get distance from self.x and target.x
        distance = abs(self.rect.centerx - target.rect.centerx)
        # print(f"distance: {distance}")

        position_prompt = ""
        if distance > 300:
            position_prompt += (
                "You are very far from the opponent. Move closer to the opponent."
            )
            if target.rect.x > self.rect.x:
                position_prompt += "Your opponent is on the right."
            else:
                position_prompt += "Your opponent is on the left."

        else:
            position_prompt += "You are close to the opponent. You should attack."

        # 提供有效攻擊距離參考
        atk1 = self.get_effective_range_for_action("ATTACK1")
        atk2 = self.get_effective_range_for_action("ATTACK2")
        atk3 = self.get_effective_range_for_action("ATTACK3")
        # 風險預判：若你剛靠近或對手攻擊性高，建議跳躍或位移後再攻擊
        risk_hint = " Be aware of counterattacks when entering range; consider JUMP or JUMP_BEHIND then attack."
        position_prompt += f" Effective ranges (px): ATTACK1≈{atk1}, ATTACK2≈{atk2}, ATTACK3≈{atk3}. Current distance={distance}.{risk_hint}"

        # Create the last action prompt
        last_action_prompt = ""

        if self.last_action is not None:
            last_action_prompt += f"Your last action was {self.last_action}."

        if target.last_action is not None:
            last_action_prompt += f"Your last action was {target.last_action}."

        # Check who was more health
        score_prompt = ""
        if self.health > target.health:
            score_prompt += "You are winning. Keep attacking the opponent."
        elif self.health < target.health:
            score_prompt += (
                "You are losing. Continue to attack the opponent but don't get hit."
            )
        else:
            score_prompt += "You are tied. Keep attacking the opponent."

        # Assemble everything
        context = f"""{position_prompt}{last_action_prompt}
Your health is {self.health}/{MAX_HEALTH}. {score_prompt}
You can win by getting your opponent health to 0. To prevent your health from decreasing, don't get hit by the opponent.
Only attack when within effective range, otherwise MOVE_CLOSER first to avoid whiffing.
"""

        return context

    def get_game_state_prompt(self, target):

        full_system_prompt = f"""
You are playing a 2d Fighting game. {self.system_prompt}. Your goal is to beat the other opponent. You respond with a bullet point list of moves.
{self.context_prompt(target)}
The moves you can use are:
{VALID_ACTIONS}
----
Rules:
- You can chain moves logically (e.g., JUMP_BEHIND then ATTACK1) when close.
- Prefer moving closer before attacking if far.
- Only use moves from the list above.
Reply with a bullet point list of at least 6 moves. The format should be: `- <name of the move>` separated by a new line.
Example if the opponent is close:
- JUMP_BEHIND
- ATTACK1
- ATTACK2
Example if the opponent is far away:
- MOVE_CLOSER
- MOVE_CLOSER
- ATTACK1
"""

        # print(full_system_prompt)

        return full_system_prompt

    def pending_actions_context(self) -> str:
        """將目前剩餘動作傳遞給模型，幫助其決定是否清空或延續策略。"""
        remaining = ", ".join(self.action_queue[:8]) if self.action_queue else "(none)"
        return f"\nCurrent pending actions (not executed yet): {remaining}\nIf you decide to change strategy, include [CLEAR_QUEUE] to clear them."

    def build_system_prompt_with_roles(self, target) -> str:
        """將角色與對手屬性寫入 system prompt，強化帶入感並輔助策略擬定。"""
        # 角色數值（暫以血量為主要可用資訊；若有角色載入器可擴充）
        self_stats = f"HP {self.health}/100"
        target_stats = f"HP {target.health}/100"
        role_line = (
            "You are the fighter yourself. Think and act as the player character. "
            f"Your stats: {self_stats}. Opponent stats: {target_stats}. "
            "Plan tactics that fit your current state and the opponent's state."
        )
        return f"{self.system_prompt}\n{role_line}"

    def start_llm_request(self, full_system_prompt, target):
        asyncio.create_task(self.add_llm_actions_to_queue(full_system_prompt, target))

    async def move(self, screen_width, screen_height, target, round_over):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        # Check if time to call model again（戰術分析間隔 500ms）
        if self.last_model_call_time is None and round_over == False:
            # get game state
            full_system_prompt = self.get_game_state_prompt(target)
            self.last_model_call_time = pygame.time.get_ticks()
            # Add to queue
            self.start_llm_request(full_system_prompt, target)
        elif (
            pygame.time.get_ticks() - self.last_model_call_time > MODEL_COOLDOWN
            and round_over == False
        ):
            # get game state
            full_system_prompt = self.get_game_state_prompt(target)
            self.last_model_call_time = pygame.time.get_ticks()
            # Add to queue
            self.start_llm_request(full_system_prompt, target)

        # if round over clear actions
        if round_over == True:
            self.action_queue = []

        # can only perform other actions if not currently attacking/jumping/knockback
        if (
            self.alive == True
            and round_over == False
            and self.attacking == False
            and self.jump == False
            and self.knockback_frames <= 0
        ):

            # 動作執行節流（200ms/次）
            now = pygame.time.get_ticks()
            if self.last_action_exec_time is None:
                self.last_action_exec_time = now
            can_pop_action = (now - self.last_action_exec_time) >= ACTION_EXECUTION_COOLDOWN
            # 動作最小持續時間：若剛切換不久，暫不切換
            if self.last_action_name is not None and (now - self.last_action_exec_time) < MIN_ACTION_DURATION_MS:
                can_pop_action = False

            if len(self.action_queue) == 0 and self.continuous_move_mode is None:
                action = "NOOP"
            else:
                # 若處於連續移動模式，優先持續前進/後退
                if self.continuous_move_mode is not None and now <= self.continuous_move_until:
                    # 只有當無高優先度動作（攻擊/跳躍）時，才以連續移動覆蓋
                    next_action = self.action_queue[0] if len(self.action_queue) > 0 else None
                    if next_action in ("ATTACK1", "ATTACK2", "ATTACK3", "DASH_ATTACK", "COUNTER_ATTACK", "JUMP", "JUMP_BEHIND"):
                        action = self.action_queue.pop(0) if can_pop_action else "NOOP"
                        if action != "NOOP":
                            self.last_action_exec_time = now
                    else:
                        action = "MOVE_CLOSER" if self.continuous_move_mode == "towards" else "MOVE_AWAY"
                elif can_pop_action and len(self.action_queue) > 0:
                    action = self.action_queue.pop(0)
                    self.last_action_exec_time = now
                    self.last_action_name = action
                else:
                    action = "NOOP"

            # movement與攻擊映射
            if action == "MOVE_CLOSER":
                # 如果目標在右邊就向右，否則向左
                if target.rect.x > self.rect.x:
                    dx = SPEED
                    self.running = True
                else:
                    dx = -SPEED
                    self.running = True
                # 啟動連續靠近（延長至約 900ms），避免動作列表被 MOVE 佔滿同時能穩定移動
                if self.continuous_move_mode != "towards":
                    self.continuous_move_mode = "towards"
                self.continuous_move_until = now + 900
            if action == "MOVE_AWAY":
                # 遠離目標
                if target.rect.x > self.rect.x:
                    dx = -SPEED
                    self.running = True
                else:
                    dx = SPEED
                    self.running = True
                if self.continuous_move_mode != "away":
                    self.continuous_move_mode = "away"
                self.continuous_move_until = now + 600
            if action == "JUMP" and self.jump == False:
                self.vel_y = -34
                self.jump = True
            if action == "JUMP_BEHIND" and self.jump == False:
                # 跳至對手身後：加入水平短衝
                self.vel_y = -34
                self.jump = True
                self.jump_dash_frames = 16
                self.jump_dash_dir = 1 if target.rect.x > self.rect.x else -1
            if action in ("ATTACK1", "ATTACK2", "ATTACK3", "DASH_ATTACK", "COUNTER_ATTACK"):
                # 將不同攻擊映射到兩種攻擊型態
                if action in ("ATTACK1", "DASH_ATTACK"):
                    self.attack_type = 1
                elif action in ("ATTACK2", "COUNTER_ATTACK"):
                    self.attack_type = 2
                else:  # ATTACK3 採用類型1
                    self.attack_type = 1
                # 若不在有效距離，優先靠近避免揮空
                if not self.is_in_attack_range(target, action):
                    if target.rect.x > self.rect.x:
                        dx = SPEED
                    else:
                        dx = -SPEED
                    self.running = True
                    # 啟動短暫靠近
                    now = pygame.time.get_ticks()
                    self.continuous_move_mode = "towards"
                    self.continuous_move_until = now + 400
                else:
                    self.attack(target)

        # knockback（若存在）
        if self.knockback_frames > 0:
            dx += self.knockback_vel_x
            self.knockback_frames -= 1

        # 跳躍短衝（JUMP_BEHIND）
        if self.jump_dash_frames > 0:
            dx += self.jump_dash_dir * (SPEED + 4)
            self.jump_dash_frames -= 1


        # apply gravity（稍微增加滯空感）
        self.vel_y += GRAVITY * 0.9
        dy += self.vel_y

        # ensure player stays on screen，並在邊界時稍作反彈
        if self.rect.left + dx < 0:
            dx = -self.rect.left
            # 邊界反彈
            if self.knockback_vel_x < 0:
                self.knockback_vel_x = int(-self.knockback_vel_x * 0.5)
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
            if self.knockback_vel_x > 0:
                self.knockback_vel_x = int(-self.knockback_vel_x * 0.5)
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        # 角色面向規則：
        # - 預設/靠近/攻擊/跳躍時，面向對手
        # - 若當前動作為 MOVE_AWAY（遠離），鏡像翻轉背向對手
        moving_away_now = (
            (self.continuous_move_mode == "away" and pygame.time.get_ticks() <= self.continuous_move_until)
        )
        if moving_away_now:
            # 背向對手
            if target.rect.centerx > self.rect.centerx:
                self.flip = True
            else:
                self.flip = False
        else:
            # 面向對手
            if target.rect.centerx > self.rect.centerx:
                self.flip = False
            else:
                self.flip = True

        # 簡單碰撞處理：避免彼此重疊
        future_rect = self.rect.copy()
        future_rect.x += dx
        future_rect.y += dy
        if future_rect.colliderect(target.rect):
            overlap = (future_rect.right - target.rect.left) if future_rect.centerx < target.rect.centerx else (target.rect.right - future_rect.left)
            if abs(overlap) < 100:  # 小範圍修正，避免抖動
                dx += -overlap if future_rect.centerx < target.rect.centerx else overlap

        # 若靠近到一定距離，自動結束連續移動模式（避免黏走位）
        distance = abs(self.rect.centerx - target.rect.centerx)
        if distance < 140:
            self.continuous_move_mode = None
            self.continuous_move_until = 0

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # update player position
        self.rect.x += dx
        self.rect.y += dy

    # handle animation updates
    def update(self):
        # check what action the player is performing
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # 6:death
        elif self.hit == True:
            self.update_action(5)  # 5:hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)  # 3:attack1
            elif self.attack_type == 2:
                self.update_action(4)  # 4:attack2
        elif self.jump == True:
            self.update_action(2)  # 2:jump
        elif self.running == True:
            self.update_action(1)  # 1:run
        else:
            self.update_action(0)  # 0:idle

        animation_cooldown = 50
        # update image
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # check if the animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            # if the player is dead then end the animation
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                # check if an attack was executed
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                # check if damage was taken
                if self.action == 5:
                    # 受擊動畫結束，恢復行動
                    self.hit = False
                    # 允許快速銜接下一動作
                    self.last_action_exec_time = 0
                    # 中斷攻擊並給予冷卻
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            # execute attack
            self.attacking = True
            
            # 播放攻擊音效
            if self.attack_type == 1:
                audio_manager.play_sound(SOUND_EFFECTS["attack1_hit"], "attack1_hit")  # 第一種攻擊使用hit音效
            elif self.attack_type == 2:
                audio_manager.play_sound(SOUND_EFFECTS["attack2_skill"], "attack2_skill")  # 第二種攻擊使用skill音效
            
            # 稍微放大攻擊判定，減少揮空
            hitbox_w = int(2.2 * self.rect.width)
            attacking_rect = pygame.Rect(
                self.rect.centerx - (hitbox_w * self.flip),
                self.rect.y,
                hitbox_w,
                self.rect.height,
            )
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                # 標記受擊並中斷對方攻擊
                target.hit = True
                target.attacking = False
                target.attack_cooldown = 20
                
                # move target back on x axis based on oppside side they are facing
                if self.flip == True:
                    target.apply_knockback(direction=-1, strength=18, duration=14)
                else:
                    target.apply_knockback(direction=1, strength=18, duration=14)

    def apply_knockback(self, direction: int, strength: int = 10, duration: int = 8):
        """對角色施加擊退，direction: -1 左 / 1 右。"""
        self.knockback_vel_x = int(max(1, strength) * (1 if direction >= 0 else -1))
        self.knockback_frames = max(1, duration)
        # 被擊退時立即中斷攻擊並播放受擊狀態更久一點
        self.attacking = False
        self.hit = True


    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        # 與原版相同：以 left-top 為錨點，但我們的影格已底對齊於固定畫布
        surface.blit(
            img,
            (
                self.rect.x - (self.offset[0] * self.image_scale),
                self.rect.y - (self.offset[1] * self.image_scale),
            ),
        )
