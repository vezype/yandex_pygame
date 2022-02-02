import pygame
import random
import math
from enum import Enum


class DinoState(Enum):
    RUN = 1
    JUMP = 2


class Dino:
    jump_power = 10
    cur_jump_power = jump_power
    sprites = {
        "run": [],
        "jump": []
    }
    image = None
    run_animation_index = [0, 5]
    hitbox = None
    state = DinoState.RUN

    def __init__(self, x, y):
        self.load_sprites()
        self.hitbox = pygame.Rect(x, y, self.sprites["run"][0].get_width(), self.sprites["run"][0].get_height())
        self.image = self.sprites["run"][0]

    def load_sprites(self):
        self.sprites["jump"].append(pygame.image.load(f"data_dino/dino/jump.png"))
        self.sprites["run"].append(pygame.image.load(f"data_dino/dino/run1.png"))
        self.sprites["run"].append(pygame.image.load(f"data_dino/dino/run2.png"))

    def update(self):
        if self.state == DinoState.RUN:
            self.run()
        elif self.state == DinoState.JUMP:
            self.jump()

    def run(self):
        self.sprites["run"][0] = pygame.image.load(f"data_dino/dino/run1.png")
        self.sprites["run"][1] = pygame.image.load(f"data_dino/dino/run2.png")

        self.image = self.sprites["run"][self.run_animation_index[0] // self.run_animation_index[1]]

        self.run_animation_index[0] += 1
        if self.run_animation_index[0] >= self.run_animation_index[1] * 2:
            self.run_animation_index[0] = 0

    def jump(self):
        if self.state == DinoState.JUMP:
            self.hitbox.y -= self.cur_jump_power * (2 * (game_speed / 8))
            self.cur_jump_power -= 0.5 * (game_speed / 8)

            if self.hitbox.y >= height - 170:
                self.hitbox.y = height - 170
                self.state = DinoState.RUN
                self.cur_jump_power = self.jump_power
        else:
            self.state = DinoState.JUMP
            self.image = pygame.image.load(f"data_dino/dino/jump.png")

    def draw(self, screen):
        screen.blit(self.image, (self.hitbox.x, self.hitbox.y))


class Cactus:
    available_types = ["1", "2", "3", "4", "5", "6"]
    cactus_type = None
    image = None
    hitbox = None
    is_active = True

    def __init__(self, x, y, forced_type=None):
        if forced_type is not None:
            self.cactus_type = forced_type

        self.load_image()
        self.hitbox.x = x
        self.hitbox.y = y - self.hitbox.height

    def randomize_cactus(self):
        self.cactus_type = random.choice(self.available_types)

    def load_image(self):
        if self.cactus_type is None:
            self.randomize_cactus()

        self.image = pygame.image.load(f"data_dino/cactus/{self.cactus_type}.png")
        self.hitbox = self.image.get_rect()

    def update(self):
        self.hitbox.x -= game_speed
        if self.hitbox.x < -self.hitbox.width:
            self.is_active = False

    def draw(self, scr):
        scr.blit(self.image, self.hitbox)


def calc_dist(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]

    return math.sqrt(dx ** 2 + dy ** 2)


if __name__ != '__main__':
    pygame.init()
    pygame.display.set_caption('Динозаврик')
    size = width, height = 1280, 720
    screen = pygame.display.set_mode(size)

    road = pygame.image.load('data_dino/road.png')
    font = pygame.font.SysFont('Roboto Condensed', 30)
    bg = (255, 255, 255)

    score = 0
    score_speedup = 100
    game_speed = 8.0

    enemies = [Cactus(width + 300 / random.uniform(0.8, 3), height - 85),
               Cactus(width * 2 + 200 / random.uniform(0.8, 3), height - 85),
               Cactus(width * 3 + 400 / random.uniform(0.8, 3), height - 85)]

    dinosaur = Dino(50, height - 170)

    road_chunks = [
        [pygame.image.load('data_dino/road.png'), [0, height - 100]],
        [pygame.image.load('data_dino/road.png'), [2404, height - 100]]
    ]

    score_font = pygame.font.SysFont("Roboto Condensed", 40)

    running = True
    stop_game = False
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(bg)

        for road_chunk in road_chunks:
            if road_chunk[1][0] <= -2400:
                road_chunk[1][0] = road_chunks[len(road_chunks) - 1][1][0] + 2400
                road_chunks[0], road_chunks[1] = road_chunks[1], road_chunks[0]
                break
            road_chunk[1][0] -= game_speed
            screen.blit(road_chunk[0], (road_chunk[1][0], road_chunk[1][1]))

        dinosaur.update()
        dinosaur.draw(screen)

        if stop_game:
            with open('records_from_dino', 'w', encoding='UTF-8') as file:
                strings = [f'Количество очков за последнюю игру: {score}\n',
                           f'Максимальная скорость за последнюю игру: {game_speed / 8}x']
                file.writelines(strings)
            break

        if len(enemies) < 3:
            enemies.append(Cactus(enemies[len(enemies) - 1].hitbox.x + width / random.uniform(0.8, 3), height - 85))

        rem_list = []
        for i, enemy in enumerate(enemies):
            enemy.update()
            enemy.draw(screen)
            if not enemy.is_active:
                rem_list.append(i)
                continue
            if dinosaur.hitbox.colliderect(enemy.hitbox):
                stop_game = True

        for i in rem_list:
            enemies.pop(i)

        score += 0.5 * (game_speed / 4)
        if score > score_speedup:
            score_speedup += 100 * (game_speed / 2)
            game_speed += 1

        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            if not dinosaur.state == DinoState.JUMP:
                dinosaur.jump()

        score_label = score_font.render("Очки: " + str(math.floor(score)), True, (50, 50, 50))
        score_label_rect = score_label.get_rect()
        score_label_rect.center = (width - 100, 50)
        screen.blit(score_label, score_label_rect)

        score_label = score_font.render("Скорость: " + str(game_speed / 8) + "x", True, (50, 50, 50))
        score_label_rect = score_label.get_rect()
        score_label_rect.center = (150, 50)
        screen.blit(score_label, score_label_rect)

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
