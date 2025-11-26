import pygame, sys, random
from pygame.math import Vector2
from pathlib import Path

# ---------------------- Helper / Asset Utilities ---------------------- #
ASSET_DIR = Path("Graphics")
SOUND_DIR = Path("Sound")
FONT_DIR = Path("Font")


def load_image_or_fallback(paths, size=None):
    """
    Try multiple filenames in order; if none exist, produce a simple surface fallback.
    `paths` is a list of Path or str candidates.
    """
    for p in paths:
        p = Path(p)
        if p.exists():
            try:
                img = pygame.image.load(str(p)).convert_alpha()
                if size is not None:
                    img = pygame.transform.smoothscale(img, size)
                return img
            except Exception:
                pass
    # fallback: colored rect with text (small)
    surf = pygame.Surface(size if size else (40, 40), pygame.SRCALPHA)
    surf.fill((180, 180, 180, 255))
    return surf


def load_sound_or_none(path):
    p = Path(path)
    if p.exists():
        try:
            return pygame.mixer.Sound(str(p))
        except Exception:
            return None
    return None


# ---------------------- Game Classes ---------------------- #
class SNAKE:
    def __init__(self, skin_index=1):
        self.skin = skin_index
        self.reset_graphics()
        self.reset()

    def reset(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)
        self.new_block = False

    def reset_graphics(self):
        # Load images; try skin2 then default if not found
        s = self.skin
        size = (cell_size, cell_size)

        def candidates(name):
            if s == 2:
                return [ASSET_DIR / f"skin2_{name}.png", ASSET_DIR / f"{name}.png"]
            else:
                return [ASSET_DIR / f"{name}.png", ASSET_DIR / f"skin2_{name}.png"]

        # head
        self.head_up = load_image_or_fallback(candidates("head_up"), size)
        self.head_down = load_image_or_fallback(candidates("head_down"), size)
        self.head_right = load_image_or_fallback(candidates("head_right"), size)
        self.head_left = load_image_or_fallback(candidates("head_left"), size)

        # tail
        self.tail_up = load_image_or_fallback(candidates("tail_up"), size)
        self.tail_down = load_image_or_fallback(candidates("tail_down"), size)
        self.tail_right = load_image_or_fallback(candidates("tail_right"), size)
        self.tail_left = load_image_or_fallback(candidates("tail_left"), size)

        # body
        self.body_vertical = load_image_or_fallback(candidates("body_vertical"), size)
        self.body_horizontal = load_image_or_fallback(candidates("body_horizontal"), size)

        self.body_tr = load_image_or_fallback(candidates("body_tr"), size)
        self.body_tl = load_image_or_fallback(candidates("body_tl"), size)
        self.body_br = load_image_or_fallback(candidates("body_br"), size)
        self.body_bl = load_image_or_fallback(candidates("body_bl"), size)

        # sounds
        self.crunch_sound = load_sound_or_none(SOUND_DIR / "crunch.wav")

    def draw_snake(self):
        self.update_head_graphics()
        self.update_tail_graphics()

        for index, block in enumerate(self.body):
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)

            if index == 0:
                screen.blit(self.head, block_rect)
            elif index == len(self.body) - 1:
                screen.blit(self.tail, block_rect)
            else:
                previous_block = self.body[index + 1] - block
                next_block = self.body[index - 1] - block
                # vertical
                if previous_block.x == next_block.x:
                    screen.blit(self.body_vertical, block_rect)
                elif previous_block.y == next_block.y:
                    screen.blit(self.body_horizontal, block_rect)
                else:
                    # corners
                    if (previous_block.x == -1 and next_block.y == -1) or (previous_block.y == -1 and next_block.x == -1):
                        screen.blit(self.body_tl, block_rect)
                    elif (previous_block.x == -1 and next_block.y == 1) or (previous_block.y == 1 and next_block.x == -1):
                        screen.blit(self.body_bl, block_rect)
                    elif (previous_block.x == 1 and next_block.y == -1) or (previous_block.y == -1 and next_block.x == 1):
                        screen.blit(self.body_tr, block_rect)
                    elif (previous_block.x == 1 and next_block.y == 1) or (previous_block.y == 1 and next_block.x == 1):
                        screen.blit(self.body_br, block_rect)

    def update_head_graphics(self):
        # Determine head graphic by relation of second segment to head
        if len(self.body) > 1:
            head_relation = self.body[1] - self.body[0]
            if head_relation == Vector2(1, 0):
                self.head = self.head_left
            elif head_relation == Vector2(-1, 0):
                self.head = self.head_right
            elif head_relation == Vector2(0, 1):
                self.head = self.head_up
            elif head_relation == Vector2(0, -1):
                self.head = self.head_down
        else:
            self.head = self.head_right

    def update_tail_graphics(self):
        if len(self.body) > 1:
            tail_relation = self.body[-2] - self.body[-1]
            if tail_relation == Vector2(1, 0):
                self.tail = self.tail_left
            elif tail_relation == Vector2(-1, 0):
                self.tail = self.tail_right
            elif tail_relation == Vector2(0, 1):
                self.tail = self.tail_up
            elif tail_relation == Vector2(0, -1):
                self.tail = self.tail_down
        else:
            self.tail = self.tail_left

    def move_snake(self):
        # If direction is zero, don't move
        if self.direction == Vector2(0, 0):
            return
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self):
        self.new_block = True

    def play_crunch_sound(self):
        if self.crunch_sound:
            self.crunch_sound.play()


class FRUIT:
    def __init__(self, skin_index=1):
        self.skin = skin_index
        self.randomize()

    def draw_fruit(self):
        fruit_rect = pygame.Rect(int(self.pos.x * cell_size), int(self.pos.y * cell_size), cell_size, cell_size)
        if apple_image:
            screen.blit(apple_image, fruit_rect)
        else:
            pygame.draw.rect(screen, (200, 30, 30), fruit_rect)

    def randomize(self):
        # ensure fruit spawns within grid
        self.x = random.randint(0, cell_number - 1)
        self.y = random.randint(0, cell_number - 1)
        self.pos = Vector2(self.x, self.y)


class MAIN:
    def __init__(self):
        self.snake = SNAKE(skin_index=current_skin)
        self.fruit = FRUIT(skin_index=current_skin)
        self.read_high_score()
        self.direction_changed = False
        self.state = "MAIN_MENU"  # MAIN_MENU, PLAYING, PAUSED, GAME_OVER
        self.menu_index = 0
        self.difficulty_index = 1  # 0: Easy, 1: Normal, 2: Hard
        self.skin_index = current_skin
        self.last_score = 0

    def read_high_score(self):
        try:
            with open("highscore.txt", "r") as file:
                self.high_score = int(file.read())
        except:
            self.high_score = 0

    def write_high_score(self):
        with open("highscore.txt", "w") as file:
            file.write(str(self.high_score))

    def start_game(self):
        self.snake = SNAKE(skin_index=self.skin_index)
        self.fruit = FRUIT(skin_index=self.skin_index)
        self.direction_changed = False
        self.snake.reset()
        self.fruit.randomize()
        self.state = "PLAYING"
        # Immediately set a safe direction to the right to avoid stuck state
        self.snake.direction = Vector2(1, 0)
        # Reset timer according to difficulty
        self.apply_difficulty_timer()

    def apply_difficulty_timer(self):
        # Difficulty determines game update speed (ms)
        if self.difficulty_index == 0:  # Easy
            interval = 200
        elif self.difficulty_index == 1:  # Normal
            interval = 150
        else:  # Hard
            interval = 100
        pygame.time.set_timer(SCREEN_UPDATE, interval)

    def update(self):
        # Called on SCREEN_UPDATE timer
        self.direction_changed = False
        if self.state == "PLAYING":
            self.snake.move_snake()
            self.check_collision()
            self.check_fail()

    def draw_elements(self):
        self.draw_grass()
        if self.state in ("PLAYING", "PAUSED", "GAME_OVER"):
            self.fruit.draw_fruit()
            self.snake.draw_snake()
            self.draw_score()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()

        # ensure fruit is not on snake
        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()

    def check_fail(self):
        # border collision
        head = self.snake.body[0]
        if not 0 <= head.x < cell_number or not 0 <= head.y < cell_number:
            self.game_over()
        # self collision
        for block in self.snake.body[1:]:
            if block == head:
                self.game_over()

    def game_over(self):
        self.last_score = len(self.snake.body) - 3
        if self.last_score > self.high_score:
            self.high_score = self.last_score
            self.write_high_score()
        self.state = "GAME_OVER"

    def draw_grass(self):
        grass_color = (167, 209, 61)
        for row in range(cell_number):
            for col in range(cell_number):
                if (row + col) % 2 == 0:
                    grass_rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                    pygame.draw.rect(screen, grass_color, grass_rect)

    def draw_score(self):
        score = len(self.snake.body) - 3
        # update highscore while playing
        if score > self.high_score:
            self.high_score = score
            self.write_high_score()

        # Current score (bottom-right)
        score_text = str(score)
        score_surface = game_font.render(score_text, True, (56, 74, 12))
        score_x = int(cell_size * cell_number - 60)
        score_y = int(cell_size * cell_number - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        apple_rect = apple_image.get_rect(midright=(score_rect.left, score_rect.centery)) if apple_image else pygame.Rect(score_rect.left - 36, score_rect.top, 32, 32)
        bg_rect = pygame.Rect(apple_rect.left, apple_rect.top, (apple_rect.width if apple_image else 32) + score_rect.width + 6, apple_rect.height)

        pygame.draw.rect(screen, (167, 209, 61), bg_rect)
        screen.blit(score_surface, score_rect)
        if apple_image:
            screen.blit(apple_image, apple_rect)
        pygame.draw.rect(screen, (56, 74, 12), bg_rect, 2)

        # High Score (top-left)
        high_score_text = f"High Score: {self.high_score}"
        high_score_surface = game_font.render(high_score_text, True, (56, 74, 12))
        high_score_rect = high_score_surface.get_rect(topleft=(10, 10))
        screen.blit(high_score_surface, high_score_rect)

    # ---------- Menus & overlays ---------- #
    def draw_main_menu(self):
        title = title_font.render("HUNGRY PYTHON", True, (50, 50, 50))
        title_rect = title.get_rect(center=(screen_size_x // 2, 230))
        screen.blit(title, title_rect)

        menu_items = ["Start Game", f"Difficulty: {['Easy','Normal','Hard'][self.difficulty_index]}", "Quit"]
        for i, item in enumerate(menu_items):
            color = (10, 80, 10) if i == self.menu_index else (50, 50, 50)
            surf = menu_font.render(item, True, color)
            rect = surf.get_rect(center=(screen_size_x // 2, 310 + i * 50))
            screen.blit(surf, rect)



    def draw_pause(self):
        overlay = pygame.Surface((screen_size_x, screen_size_y), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        pause_text = title_font.render("PAUSED", True, (255, 255, 255))
        rect = pause_text.get_rect(center=(screen_size_x // 2, screen_size_y // 2 - 20))
        screen.blit(pause_text, rect)
        info = small_font.render("Press P to resume or M for menu", True, (230, 230, 230))
        screen.blit(info, info.get_rect(center=(screen_size_x // 2, screen_size_y // 2 + 30)))

    def draw_game_over(self):
        overlay = pygame.Surface((screen_size_x, screen_size_y), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        go_text = title_font.render("GAME OVER", True, (255, 200, 80))
        screen.blit(go_text, go_text.get_rect(center=(screen_size_x // 2, 200)))
        score_text = menu_font.render(f"Score: {self.last_score}", True, (255, 255, 255))
        screen.blit(score_text, score_text.get_rect(center=(screen_size_x // 2, 280)))
        hs_text = menu_font.render(f"High Score: {self.high_score}", True, (200, 200, 200))
        screen.blit(hs_text, hs_text.get_rect(center=(screen_size_x // 2, 320)))

        # options
        opt1 = small_font.render("Press ENTER to play again", True, (220, 220, 220))
        opt2 = small_font.render("Press M to return to menu", True, (220, 220, 220))
        screen.blit(opt1, opt1.get_rect(center=(screen_size_x // 2, 470)))
        screen.blit(opt2, opt2.get_rect(center=(screen_size_x // 2, 510)))


# ---------------------- Pygame Setup ---------------------- #
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

cell_size = 40
cell_number = 20
screen_size_x = cell_number * cell_size
screen_size_y = cell_number * cell_size

screen = pygame.display.set_mode((screen_size_x, screen_size_y))
pygame.display.set_caption("Snake - Upgraded")
clock = pygame.time.Clock()

# Fonts
game_font = pygame.font.Font(str(FONT_DIR / "PoetsenOne-Regular.ttf") if (FONT_DIR / "PoetsenOne-Regular.ttf").exists() else None, 25)
menu_font = pygame.font.Font(str(FONT_DIR / "PoetsenOne-Regular.ttf") if (FONT_DIR / "PoetsenOne-Regular.ttf").exists() else None, 32)
title_font = pygame.font.Font(str(FONT_DIR / "PoetsenOne-Regular.ttf") if (FONT_DIR / "PoetsenOne-Regular.ttf").exists() else None, 64)
small_font = pygame.font.Font(str(FONT_DIR / "PoetsenOne-Regular.ttf") if (FONT_DIR / "PoetsenOne-Regular.ttf").exists() else None, 18)

# Load apple image (try skin2 then default)
apple_image = load_image_or_fallback([ASSET_DIR / "apple.png", ASSET_DIR / "skin2_apple.png"], (cell_size, cell_size))

# Sounds
menu_select_sound = load_sound_or_none(SOUND_DIR / "menu_select.wav")
# (crunch sound is loaded per snake instance)

# Timer event
SCREEN_UPDATE = pygame.USEREVENT

# Default skin and difficulty
current_skin = 1
default_interval = 150
pygame.time.set_timer(SCREEN_UPDATE, default_interval)

# Create main game manager
main_game = MAIN()

# ---------------------- Main Game Loop ---------------------- #
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Timer-driven update
        if event.type == SCREEN_UPDATE:
            main_game.update()

        # Key handling: menus, playing, pause
        if event.type == pygame.KEYDOWN:
            # Global keys
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # --- MAIN MENU controls ---
            if main_game.state == "MAIN_MENU":
                if event.key == pygame.K_DOWN:
                    main_game.menu_index = (main_game.menu_index + 1) % 4
                    if menu_select_sound: menu_select_sound.play()
                elif event.key == pygame.K_UP:
                    main_game.menu_index = (main_game.menu_index - 1) % 4
                    if menu_select_sound: menu_select_sound.play()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    sel = main_game.menu_index
                    if sel == 0:  # Start Game
                        if menu_select_sound: menu_select_sound.play()
                        main_game.start_game()
                    elif sel == 1:  # Difficulty
                        main_game.difficulty_index = (main_game.difficulty_index + 1) % 3
                        main_game.apply_difficulty_timer()
                        if menu_select_sound: menu_select_sound.play()
                    elif sel == 2:  # Skin
                        main_game.skin_index = 2 if main_game.skin_index == 1 else 1
                        if menu_select_sound: menu_select_sound.play()
                    elif sel == 3:  # Quit
                        pygame.quit()
                        sys.exit()
                # Allow left/right to change options inline
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    if main_game.menu_index == 1:  # Difficulty
                        if event.key == pygame.K_RIGHT:
                            main_game.difficulty_index = (main_game.difficulty_index + 1) % 3
                        else:
                            main_game.difficulty_index = (main_game.difficulty_index - 1) % 3
                        main_game.apply_difficulty_timer()
                        if menu_select_sound: menu_select_sound.play()
                    elif main_game.menu_index == 2:  # Skin
                        main_game.skin_index = 2 if main_game.skin_index == 1 else 1
                        if menu_select_sound: menu_select_sound.play()

            # --- PLAYING controls ---
            elif main_game.state == "PLAYING":
                # Prevent more than one direction change per update/frame
                if not main_game.direction_changed:
                    current_x = main_game.snake.direction.x
                    current_y = main_game.snake.direction.y

                    if event.key == pygame.K_UP and current_y != 1:
                        main_game.snake.direction = Vector2(0, -1)
                        main_game.direction_changed = True
                    elif event.key == pygame.K_RIGHT and current_x != -1:
                        main_game.snake.direction = Vector2(1, 0)
                        main_game.direction_changed = True
                    elif event.key == pygame.K_DOWN and current_y != -1:
                        main_game.snake.direction = Vector2(0, 1)
                        main_game.direction_changed = True
                    elif event.key == pygame.K_LEFT and current_x != 1:
                        main_game.snake.direction = Vector2(-1, 0)
                        main_game.direction_changed = True

                # Pause
                if event.key == pygame.K_p:
                    main_game.state = "PAUSED"
                    if menu_select_sound: menu_select_sound.play()

            # --- PAUSED controls ---
            elif main_game.state == "PAUSED":
                if event.key == pygame.K_p:
                    main_game.state = "PLAYING"
                    if menu_select_sound: menu_select_sound.play()
                if event.key == pygame.K_m:
                    main_game.state = "MAIN_MENU"
                    if menu_select_sound: menu_select_sound.play()

            # --- GAME OVER controls ---
            elif main_game.state == "GAME_OVER":
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # Play again with same settings
                    if menu_select_sound: menu_select_sound.play()
                    main_game.start_game()
                if event.key == pygame.K_m:
                    main_game.state = "MAIN_MENU"
                    if menu_select_sound: menu_select_sound.play()

    # ----- Drawing -----
    screen.fill((175, 215, 70))

    if main_game.state == "MAIN_MENU":
        main_game.draw_grass()
        main_game.draw_main_menu()
    else:
        main_game.draw_elements()
        if main_game.state == "PAUSED":
            main_game.draw_pause()
        elif main_game.state == "GAME_OVER":
            main_game.draw_game_over()

    pygame.display.update()
    clock.tick(60)