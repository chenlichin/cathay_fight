import asyncio
import pygame
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# from fighter import Fighter
from llm_fighter import LLMFighter


async def main():

    pygame.init()

    # create game window
    GAME_WIDTH = 1000
    GAME_HEIGHT = 600
    BORDER_LEFT = 200
    BORDER_RIGHT = 200
    BORDER_TOP = 50
    BORDER_BOTTOM = 150
    SCREEN_WIDTH = GAME_WIDTH + BORDER_LEFT + BORDER_RIGHT
    SCREEN_HEIGHT = GAME_HEIGHT + BORDER_TOP + BORDER_BOTTOM

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Model Brawl League")
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

    # set framerate
    clock = pygame.time.Clock()
    FPS = 60

    # define colours
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)

    # define game variables
    intro_count = 3
    last_count_update = pygame.time.get_ticks()
    score = [0, 0]  # player scores. [P1, P2]
    round_over = False
    ROUND_OVER_COOLDOWN = 2000

    # define fighter variables
    WARRIOR_SIZE = 162
    WARRIOR_SCALE = 4
    WARRIOR_OFFSET = [72, 56]
    WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
    WIZARD_SIZE = 250
    WIZARD_SCALE = 3
    WIZARD_OFFSET = [112, 107]
    WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

    # load background image
    bg_image = pygame.image.load(
        "assets/images/background/background.jpg"
    ).convert_alpha()

    # load spritesheets
    warrior_sheet = pygame.image.load(
        "assets/images/warrior/Sprites/warrior.png"
    ).convert_alpha()
    wizard_sheet = pygame.image.load(
        "assets/images/wizard/Sprites/wizard.png"
    ).convert_alpha()

    # load vicory image
    victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()

    # define number of steps in each animation
    WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
    WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

    # define font
    count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
    score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

    # function for drawing text
    def draw_text(surface, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        surface.blit(img, (x, y))

    # function for drawing background
    def draw_bg(surface):
        scaled_bg = pygame.transform.scale(bg_image, (GAME_WIDTH, GAME_HEIGHT))
        surface.blit(scaled_bg, (0, 0))

    # function for drawing fighter health bars
    def draw_health_bar(surface, health, x, y):
        ratio = health / 100
        pygame.draw.rect(surface, WHITE, (x - 2, y - 2, 404, 34))
        pygame.draw.rect(surface, RED, (x, y, 400, 30))
        pygame.draw.rect(surface, YELLOW, (x, y, 400 * ratio, 30))

    def draw_timer(surface, timer, x, y):

        if timer <= 0:
            timer = 0

        draw_text(surface, f"{timer}", count_font, RED, x, y)

    action_font = pygame.font.Font("assets/fonts/turok.ttf", 20)

    def draw_actions(surface, fighter, x):
        draw_text(surface, "Moves:", action_font, WHITE, x, BORDER_TOP)
        if fighter.action_queue:
            for i, action in enumerate(fighter.action_queue[:5]):
                draw_text(
                    surface,
                    f"- {action}",
                    action_font,
                    WHITE,
                    x,
                    BORDER_TOP + 25 + i * 20,
                )
        else:
            draw_text(surface, "No actions", action_font, WHITE, x, BORDER_TOP + 25)

    # Load Hugging Face model
    MODEL_NAME = "bigscience/bloom-560m"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    hf_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    llm = pipeline("text-generation", model=hf_model, tokenizer=tokenizer)

    model_1 = MODEL_NAME
    system_prompt_1 = "You are a very defensive player"
    display_name_1 = model_1

    model_2 = MODEL_NAME
    system_prompt_2 = "You are a very aggressive player"
    display_name_2 = model_2

    fighter_1 = LLMFighter(
        1,
        200,
        310,
        False,
        WARRIOR_DATA,
        warrior_sheet,
        WARRIOR_ANIMATION_STEPS,
        model_1,
        system_prompt_1,
        llm,
    )

    fighter_2 = LLMFighter(
        2,
        700,
        310,
        True,
        WIZARD_DATA,
        wizard_sheet,
        WIZARD_ANIMATION_STEPS,
        model_2,
        system_prompt_2,
        llm,
    )

    # game loop
    run = True
    timer = 99
    while run:

        clock.tick(FPS)

        # draw background
        draw_bg(game_surface)

        # show player stats
        draw_health_bar(game_surface, fighter_1.health, 20, 20)
        draw_health_bar(game_surface, fighter_2.health, 580, 20)
        draw_text(
            game_surface,
            f"P1: {display_name_1} " + str(score[0]),
            score_font,
            RED,
            20,
            60,
        )
        draw_text(
            game_surface,
            f"P2: {display_name_2} " + str(score[1]),
            score_font,
            RED,
            580,
            60,
        )
        draw_timer(game_surface, timer, 460, 10)

        # update countdown
        if intro_count <= 0:
            # move fighters
            await fighter_1.move(GAME_WIDTH, GAME_HEIGHT, fighter_2, round_over)
            await fighter_2.move(GAME_WIDTH, GAME_HEIGHT, fighter_1, round_over)
        else:
            # display count timer
            draw_text(
                game_surface,
                str(intro_count),
                count_font,
                RED,
                GAME_WIDTH / 2,
                GAME_HEIGHT / 3,
            )
            # update count timer
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        # update fighters
        fighter_1.update()
        fighter_2.update()

        # draw fighters
        fighter_1.draw(game_surface)
        fighter_2.draw(game_surface)

        # check for player defeat
        if round_over == False:
            if fighter_1.alive == False:
                score[1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif fighter_2.alive == False:
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()

            if timer == 0:
                if fighter_1.health > fighter_2.health:
                    score[0] += 1
                elif fighter_2.health > fighter_1.health:
                    score[1] += 1
                else:
                    print("tie")
                    # no winner
                round_over = True
                round_over_time = pygame.time.get_ticks()

        else:
            # display victory image
            game_surface.blit(victory_img, (360, 150))
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                intro_count = 3
                timer = 99
                fighter_1 = LLMFighter(
                    1,
                    200,
                    310,
                    False,
                    WARRIOR_DATA,
                    warrior_sheet,
                    WARRIOR_ANIMATION_STEPS,
                    model_1,
                    system_prompt_1,
                    llm,
                )

                fighter_2 = LLMFighter(
                    2,
                    700,
                    310,
                    True,
                    WIZARD_DATA,
                    wizard_sheet,
                    WIZARD_ANIMATION_STEPS,
                    model_2,
                    system_prompt_2,
                    llm,
                )

        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # count down timer for every 1 second of real time
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            timer -= 1
            last_count_update = pygame.time.get_ticks()

        # draw game surface onto screen and add borders
        screen.fill((0, 0, 0))
        screen.blit(game_surface, (BORDER_LEFT, BORDER_TOP))
        draw_actions(screen, fighter_1, 10)
        draw_actions(screen, fighter_2, SCREEN_WIDTH - BORDER_RIGHT + 10)

        # update display
        pygame.display.update()
        await asyncio.sleep(0)

    # exit pygame
    pygame.quit()


# This is the program entry point:
print("start game")
asyncio.run(main())
