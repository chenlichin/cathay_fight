import asyncio
import re

import pygame
from typing import Any

VALID_ACTIONS = ["MOVE_CLOSER", "MOVE_AWAY", "HIGH_ATTACK", "LOW_ATTACK", "JUMP"]
MAX_HEALTH = 100
MODEL_COOLDOWN = 500
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

    def load_images(self, sprite_sheet, animation_steps):
        # extract images from spritesheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(
                    x * self.size, y * self.size, self.size, self.size
                )
                temp_img_list.append(
                    pygame.transform.scale(
                        temp_img,
                        (self.size * self.image_scale, self.size * self.image_scale),
                    )
                )
            animation_list.append(temp_img_list)
        return animation_list

    async def add_llm_actions_to_queue(self, full_system_prompt):

        prompt = f"{full_system_prompt}\nYour next moves are:"

        # Run the Hugging Face model in a separate thread
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

        # add valid moves to action queue
        for move in moves:
            if move in VALID_ACTIONS:
                valid_moves.append(move)
                # IF move left or right add 2 more moves
                if move == "MOVE_CLOSER" or move == "MOVE_AWAY":
                    valid_moves.append(move)
                    valid_moves.append(move)
                    valid_moves.append(move)
                    valid_moves.append(move)
            else:
                invalid_moves.append(move)

        self.action_queue.extend(valid_moves)

        return valid_moves

    def context_prompt(self, target) -> str:
        """
        Return a str of the context
        """

        # get distance from self.x and target.x
        distance = abs(self.rect.x - target.rect.x)
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
"""

        return context

    def get_game_state_prompt(self, target):

        full_system_prompt = f"""
You are playing a 2d Fighting game. {self.system_prompt}. Your goal is to beat the other opponent. You respond with a bullet point list of moves.
{self.context_prompt(target)}
The moves you can use are:
{VALID_ACTIONS}
----
Reply with a bullet point list of at least 6 moves. The format should be: `- <name of the move>` separated by a new line.
Example if the opponent is close:
- JUMP
- HIGH_ATTACK
- LOW_ATTACK
Example if the opponent is far away:
- MOVE_CLOSER
- MOVE_CLOSER
- LOW_ATTACK
"""

        # print(full_system_prompt)

        return full_system_prompt

    def start_llm_request(self, full_system_prompt):
        asyncio.create_task(self.add_llm_actions_to_queue(full_system_prompt))

    async def move(self, screen_width, screen_height, target, round_over):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        # Check if time to call model again
        if self.last_model_call_time is None and round_over == False:
            # get game state
            full_system_prompt = self.get_game_state_prompt(target)
            self.last_model_call_time = pygame.time.get_ticks()
            # Add to queue
            # await self.add_llm_actions_to_queue(full_system_prompt)
            self.start_llm_request(full_system_prompt)
        elif (
            pygame.time.get_ticks() - self.last_model_call_time > MODEL_COOLDOWN
            and round_over == False
        ):
            # get game state
            full_system_prompt = self.get_game_state_prompt(target)
            self.last_model_call_time = pygame.time.get_ticks()
            # Add to queue
            # await self.add_llm_actions_to_queue(full_system_prompt)
            self.start_llm_request(full_system_prompt)

        # if round over clear actions
        if round_over == True:
            self.action_queue = []

        # can only perform other actions if not currently attacking
        if self.attacking == False and self.alive == True and round_over == False:

            if len(self.action_queue) == 0:
                action = "NOOP"
            else:
                # print("action queue: ", self.action_queue)
                action = self.action_queue.pop(0)

            # movement
            if action == "MOVE_CLOSER":

                # if target is on the left move left
                if target.rect.x > self.rect.x:
                    dx = SPEED
                    self.running = True
                else:
                    dx = -SPEED
                    self.running = True
            if action == "MOVE_AWAY ":
                # if target is on the left move right
                if target.rect.x > self.rect.x:
                    dx = SPEED
                    self.running = True
                else:
                    dx = -SPEED
                    self.running = True
                # dx = SPEED
                # self.running = True
            # jump
            if action == "JUMP" and self.jump == False:
                self.vel_y = -30
                self.jump = True
            # attack
            if action == "HIGH_ATTACK" or action == "LOW_ATTACK":
                self.attack(target)
                # determine which attack type was used
                if action == "HIGH_ATTACK":
                    self.attack_type = 1
                if action == "LOW_ATTACK":
                    self.attack_type = 2

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure player stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        # ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

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
                    self.hit = False
                    # if the player was in the middle of an attack, then the attack is stopped
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            # execute attack
            self.attacking = True
            # self.attack_sound.play()
            attacking_rect = pygame.Rect(
                self.rect.centerx - (2 * self.rect.width * self.flip),
                self.rect.y,
                2 * self.rect.width,
                self.rect.height,
            )
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True
                # move target back on x axis based on oppside side they are facing
                if self.flip == True:
                    target.rect.x -= 150
                else:
                    target.rect.x += 150

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(
            img,
            (
                self.rect.x - (self.offset[0] * self.image_scale),
                self.rect.y - (self.offset[1] * self.image_scale),
            ),
        )
