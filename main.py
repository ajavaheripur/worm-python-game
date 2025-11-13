#-------------------------------------------------------------------------------
# Name:        PyGame Worm Ultimate
# Purpose:     Classic snake game implemented with customizable speed and grid size,
#              where the player controls a worm to collect food, grow longer,
#              and avoid collisions with itself or the game boundaries. Use the arrow
#			   keys to turn your worm.
#
# Author:      Arvin Javaheripur
#
# Created:     2025/11/13
# Copyright:   (c) 2025 Arvin Javaheripur
# License:     GNU Lesser General Public License v3.0
#-------------------------------------------------------------------------------



from random import randint
import os
import pygame

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class SnakeBlock:
    def __init__(self, screen, col, row, width, height, is_head, color=(140, 20, 70)):
        self.screen = screen
        self.row = row
        self.col = col
        self.prev_col = col
        self.prev_row = row
        self.width = width
        self.height = height
        self.rect = pygame.Rect(col * width, row * height, width, height)
        self.color = color
        self.is_head = is_head

    def draw(self, x, y):
        pygame.draw.rect(screen, self.color, (x, y, self.width, self.height))

    def set_location(self, new_col, new_row):
        self.prev_col = self.col
        self.prev_row = self.row
        self.col = new_col
        self.row = new_row
        self.rect.topleft = (self.col * self.width, self.row * self.height)


    def get_row(self):
        return self.row

    def get_col(self):
        return self.col

class Food:
    def __init__(self, screen, col, row, width, height, image):
        self.screen = screen
        self.col = col
        self.row = row
        self.width = width
        self.height = height
        self.image = image
        self.rect = pygame.Rect(col * width, row * height, width, height)

    def draw(self):
        self.screen.blit(self.image, self.rect.topleft)

    def set_location(self, new_col, new_row):
        self.col = new_col
        self.row = new_row
        self.rect.topleft = (self.col * self.width, self.row * self.height)

    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)

    def get_position(self):
        return self.col, self.row


class Button:
    def __init__(self, screen, color, x, y, width, height, text,
                 text_color=(255, 255, 255), text_size=28,
                 light_up=400, font=None):
        self.screen = screen
        self.base_color = color
        self.current_color = self.base_color.copy()
        self.light_up_threshold = light_up

        self.rect = pygame.Rect(x, y, width, height)

        self.text = text
        self.text_color = text_color
        self.text_size = text_size
        self.font = pygame.font.Font(font, text_size)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self):
        pygame.draw.rect(self.screen, self.current_color, self.rect, border_radius=8)
        self.screen.blit(self.text_surface, self.text_rect)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        if is_hovered:
            if sum(self.current_color) < self.light_up_threshold:
                self.current_color[0] = min(self.current_color[0] + 4, 255)
                self.current_color[1] = min(self.current_color[1] + 4, 255)
                self.current_color[2] = min(self.current_color[2] + 4, 255)
        else:
            if sum(self.current_color) > sum(self.base_color):
                self.current_color[0] = max(self.current_color[0] - 10, self.base_color[0])
                self.current_color[1] = max(self.current_color[1] - 10, self.base_color[1])
                self.current_color[2] = max(self.current_color[2] - 10, self.base_color[2])

    def check_click(self, mouse_down):
        if mouse_down and self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False


class Slider:
    def __init__(self, screen, line_color, handle_color, x, y, width, height, min_val=0, max_val=10, initial_val=5):
        self.screen = screen
        self.line_color = line_color
        self.handle_color = handle_color
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_radius = height // 2 + 4
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False

    def draw(self):
        pygame.draw.rect(self.screen, self.line_color, self.rect, border_radius=8)
        handle_x = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        handle_y = self.rect.centery
        pygame.draw.circle(self.screen, self.handle_color, (handle_x, handle_y), self.handle_radius)

    def update(self, mouse_down):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if mouse_down and not self.dragging:
            if self._handle_hit(mouse_x, mouse_y):
                self.dragging = True

        if not mouse_down:
            self.dragging = False

        if self.dragging:
            rel_x = max(0, min(mouse_x - self.rect.x, self.rect.width))
            self.value = self.min_val + rel_x / self.rect.width * (self.max_val - self.min_val)

    def _handle_hit(self, x, y):
        handle_x = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        handle_y = self.rect.centery
        return (x - handle_x) ** 2 + (y - handle_y) ** 2 <= self.handle_radius ** 2

    def get_value(self):
        return self.value


def random_food_location():
    while True:
        rand_col = randint(0, number_of_tiles - 1)
        rand_row = randint(0, number_of_tiles - 1)
        if all(block.get_col() != rand_col or block.get_row() != rand_row for block in snake_blocks):
            return rand_col, rand_row


SCREEN_WIDTH = 500  # 500
SCREEN_HEIGHT = 500  # 500
INITIAL_SNAKE_LENGTH = 3  # 3
SNAKE_BLOCK_WIDTH = 40  # 40
SNAKE_BLOCK_HEIGHT = 40  # 40
MOVE_SPEED = 1
WIN_LENGTH = 25  # 25

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("PyGame Worm(TM) Ultimate")
icon = pygame.image.load("images/icon.png")
pygame.display.set_icon(icon)

FOOD_IMG = pygame.image.load("images/food.png")

button_start = Button(screen, [50, 160, 70], SCREEN_WIDTH / 2 - 57, SCREEN_HEIGHT - 100, 115, 70, "Start", text_size=45,
                      light_up=350)
button_retry = Button(screen, [50, 160, 70], SCREEN_WIDTH / 2 - 57, SCREEN_HEIGHT - 200, 115, 70, "Retry", text_size=45,
                      light_up=350)
button_quit = Button(screen, [50, 160, 70], SCREEN_WIDTH / 2 - 57, SCREEN_HEIGHT - 100, 115, 70, "Quit", text_size=45,
                      light_up=350)
slider_speed = Slider(screen, (120, 220, 120), (40, 120, 40), 100, SCREEN_HEIGHT - 220, 300, 15, min_val=0.5, max_val=8,
                      initial_val=2.5)
slider_tiles = Slider(screen, (120, 220, 120), (40, 120, 40), 100, SCREEN_HEIGHT - 160, 300, 15, min_val=4, max_val=20,
                      initial_val=8)

title_text1 = pygame.font.SysFont("Comic Sans MS", 48).render("Worm\u2122", True, (255, 255, 255))
title_text2 = pygame.font.SysFont("Comic Sans MS", 28).render("By Arvin Javaheripur", True, (255, 255, 255))
press_to_start_text = pygame.font.SysFont("Comic Sans MS", 40).render("Press any key to start!", True, (255, 255, 255))

mouse_down = False
mouse_held = False
stage = -2
run = True
FPS = 30

start_time = pygame.time.get_ticks()

MOVE_INTERVAL = 1000 // MOVE_SPEED
last_move_time = pygame.time.get_ticks()

while run:
    tick = pygame.time.Clock()
    tick.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True
        else:
            mouse_down = False

    if stage == -2:
        screen.fill((30, 140, 50))
        screen.blit(title_text1, title_text1.get_rect(center=(SCREEN_WIDTH // 2, 70)))
        screen.blit(title_text2, title_text2.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        mouse_held = pygame.mouse.get_pressed()[0]
        slider_speed.update(mouse_held)
        slider_speed.draw()
        slider_tiles.update(mouse_held)
        slider_tiles.draw()

        font = pygame.font.SysFont("Arial", 18)
        screen.blit(font.render(f"Speed (tile/s): {slider_speed.get_value():.1f}", True, (255, 255, 255)), (100, SCREEN_HEIGHT-250))
        screen.blit(font.render(f"Grid Size: {int(slider_tiles.get_value())}", True, (255, 255, 255)), (100, SCREEN_HEIGHT-190))

        button_start.update()
        button_start.draw()

        if button_start.check_click(mouse_down):
            number_of_tiles = int(slider_tiles.get_value())
            MOVE_SPEED = slider_speed.get_value()
            MOVE_INTERVAL = 1000 // MOVE_SPEED
            tile_size = min(SCREEN_WIDTH, SCREEN_HEIGHT) // number_of_tiles
            screen_area = (SCREEN_WIDTH - SCREEN_WIDTH % number_of_tiles,
                           SCREEN_HEIGHT - SCREEN_HEIGHT % number_of_tiles)
            FOOD_IMG = pygame.transform.scale(FOOD_IMG, (tile_size, tile_size))
            stage = -1

    elif stage == -1:
        tile_center = number_of_tiles // 2
        snake_blocks = [SnakeBlock(screen, tile_center, tile_center, tile_size, tile_size, True, color=(217, 76, 135))]
        for i in range(0, INITIAL_SNAKE_LENGTH-1):
            snake_block_x = tile_center - i - 1
            snake_block_y = tile_center
            snake_block_color = (217, 76, 135) if i % 2 else (197, 56, 115)
            snake_blocks.append(SnakeBlock(screen, snake_block_x, snake_block_y, tile_size, tile_size, False,
                                           color=(snake_block_color)))
        head = snake_blocks[0]
        d_row = 0
        d_col = 1
        head.next_dir = (d_row, d_col)
        food_col, food_row = random_food_location()
        food = Food(screen, food_col, food_row, tile_size, tile_size, FOOD_IMG)
        score = INITIAL_SNAKE_LENGTH

        pygame.mouse.set_visible(False)
       
        stage = 0
        
    elif stage == 0:
        screen.fill((102, 69, 49))
        for i in range(number_of_tiles + 1):
            pygame.draw.line(screen, (40, 40, 40), (i * tile_size, 0), (i * tile_size, screen_area[1]))
            pygame.draw.line(screen, (40, 40, 40), (0, i * tile_size), (screen_area[0], i * tile_size))
        for block in snake_blocks[::-1]:
            x = (block.prev_col + (block.get_col() - block.prev_col)) * tile_size
            y = (block.prev_row + (block.get_row() - block.prev_row)) * tile_size
            block.draw(x, y)
        screen.blit(press_to_start_text, press_to_start_text.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        
        if any(pygame.key.get_pressed()):
            stage = 1

    elif stage == 1:
        screen.fill((102, 69, 49))

        for i in range(number_of_tiles + 1):
            pygame.draw.line(screen, (40, 40, 40), (i * tile_size, 0), (i * tile_size, screen_area[1]))
            pygame.draw.line(screen, (40, 40, 40), (0, i * tile_size), (screen_area[0], i * tile_size))

        state = pygame.key.get_pressed()
        if state[pygame.K_UP] and d_row != 1:
            head.next_dir = (-1, 0)
        elif state[pygame.K_DOWN] and d_row != -1:
            head.next_dir = (1, 0)
        elif state[pygame.K_LEFT] and d_col != 1:
            head.next_dir = (0, -1)
        elif state[pygame.K_RIGHT] and d_col != -1:
            head.next_dir = (0, 1)

        current_time = pygame.time.get_ticks()
        dt = current_time - last_move_time
        progress = min(1, dt / MOVE_INTERVAL)

        food.draw()

        for block in snake_blocks[::-1]:
            x = (block.prev_col + (block.get_col() - block.prev_col) * progress) * tile_size
            y = (block.prev_row + (block.get_row() - block.prev_row) * progress) * tile_size
            block.draw(x, y)

        if dt >= MOVE_INTERVAL:
            last_move_time = current_time
            d_row, d_col = head.next_dir

            for i in range(len(snake_blocks) - 1, 0, -1):
                snake_blocks[i].set_location(snake_blocks[i - 1].get_col(), snake_blocks[i - 1].get_row())
                if i > 1:
                    if (snake_blocks[i].get_col() == head.get_col() + d_col) and (snake_blocks[i].get_row() == head.get_row() + d_row):
                        stage = 2

            if food.get_position() == (head.get_col(), head.get_row()):
                new_block = SnakeBlock(screen, snake_blocks[-1].get_col(), snake_blocks[-1].get_row(), tile_size,
                                       tile_size, False,
                                       color=(217, 76, 135) if not len(snake_blocks) % 2 else (197, 56, 115))
                snake_blocks.append(new_block)
                score += 1

                food_col, food_row = random_food_location()
                food.set_location(food_col, food_row)

            head.set_location(head.get_col() + d_col, head.get_row() + d_row)
            if (head.get_col() == number_of_tiles) or (head.get_row() == number_of_tiles) or (head.get_col() == -1) or (head.get_row() == -1):
                stage = 2


    elif stage == 2:
        game_over_text = pygame.font.SysFont("Comic Sans MS", 48).render("Game Over!", True, (255, 255, 255))
        game_over_score_text1 = pygame.font.SysFont("Comic Sans MS", 32).render("Score: " + str(score), True, (255, 255, 255))
        game_over_score_text2 = pygame.font.SysFont("Comic Sans MS", 32).render("Grid Size: " + str(number_of_tiles), True, (255, 255, 255))
        stage = 3

    elif stage == 3:
        pygame.mouse.set_visible(True)
        screen.fill((30, 140, 50))
        screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        screen.blit(game_over_score_text1, game_over_score_text1.get_rect(center=(SCREEN_WIDTH // 2, 160)))
        screen.blit(game_over_score_text2, game_over_score_text2.get_rect(center=(SCREEN_WIDTH // 2, 210)))

        button_retry.update()
        button_retry.draw()
        button_quit.update()
        button_quit.draw()

        if button_retry.check_click(mouse_down):
            stage = -2
        if button_quit.check_click(mouse_down):
            run = False
            break

    pygame.display.update()

pygame.quit()
