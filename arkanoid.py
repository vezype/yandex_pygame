import pygame
from random import choice, randint
import pygame.sprite
import os
import sys


def load_file(name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    fullname = os.path.join(base_path + '/data_arkanoid/', name)
    if not os.path.isfile(fullname):
        print(f"Файл '{fullname}' не найден")
        sys.exit()
    else:
        return fullname


class Circle(pygame.sprite.Sprite):
    def __init__(self, x, y, all_sprites, cirles):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(pygame.image.load(load_file('circle.png')), (10 * 2, 10 * 2))
        self.mask = pygame.mask.from_surface(self.image)
        # self.image = pygame.Surface((2 * 10, 2 * 10), pygame.SRCALPHA, 32, color=(255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.add(cirles)
        self.x_pos = x
        self.y_pos = y
        self.q = 1
        self.w = 1

    def move(self, time):
        e = int(speed) * time / 1000
        if height - 10 <= self.y_pos:
            global lifes
            if lifes:
                lifes -= 1
                self.x_pos = 200
                self.y_pos = 400
            else:
                global running
                running = False
                global final
                final = 'lose'
        elif width - 10 <= self.x_pos:
            self.q = -1
        elif self.x_pos <= 10:
            self.q = 1
        elif self.y_pos <= 10:
            self.w = 1
        self.rect = self.rect.move(self.x_pos, self.y_pos)
        global sticks
        global blocked
        if pygame.sprite.spritecollideany(self, sticks):
            self.q = (-1) * self.q
        if pygame.sprite.spritecollideany(self, blocked):
            self.q = (-1) * self.q

        # pygame.draw.circle(screen, (0, 0, 0), (self.x_pos, self.y_pos), 10)
        self.x_pos += e * self.q  # v * t в секундах
        self.y_pos += e * self.w
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos
        return (self.x_pos, self.y_pos)

    def update(self):
        global stick
        if pygame.sprite.collide_mask(self, stick):
            # circle.w = (-1) * circle.w
            self.w = (-1) * self.w
        else:
            global BLOCKS
            for i in BLOCKS:
                for j in i:
                    if j == 0:
                        pass
                    elif pygame.sprite.collide_mask(self, j):
                        self.q = (-1) * self.q
                        j.destruction()
                        break


class Stick(pygame.sprite.Sprite):
    def __init__(self, screen, all_sprites, sticks):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(pygame.image.load(load_file('stick.png')), (70, 30))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 250
        self.rect.y = 680
        self.add(sticks)
        self.x = 250
        self.status_move = False
        self.k = 0

    def move(self, screen, time):
        e = 2 * int(speed) * time / 1000
        if self.x + self.k * e >= 0 and self.x + self.k * e <= 500:
            # pygame.draw.rect(screen, (0, 0, 0), (self.x, 680, 60, 10), width=0)
            self.x += self.k * e
            self.rect.x = self.x
            # pygame.draw.rect(screen, (40, 70, 255), (self.x, 680, 60, 10), width=0)
        else:
            self.status_move = False

    def move2(self, screen):
        e = 7
        # pygame.draw.rect(screen, (40, 70, 255), (self.x, 680, 60, 10), width=0)


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, all_sprites, blocked):
        super().__init__(all_sprites)
        dfg = load_file('block' + str(randint(1, 3)) + '.png')
        self.image = pygame.transform.scale(pygame.image.load(dfg), (40 * 2, 20 * 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x * 80
        self.rect.y = y * 40
        self.add(blocked)
        self.x = x
        self.y = y

    def destruction(self):
        global speed
        speed += 5
        BLOCKS[self.x][self.y] = 0
        self.kill()
        global SCORE
        SCORE += 10
        global count
        count -= 1
        if count == 0:
            global running
            running = False
            global final
            final = 'win'
        if randint(0, 3) == 1:
            q = randint(-2, 2)
            if q:
                if speed + q > 9.5:
                    speed += q
            else:
                global lifes
                lifes += 1
        # if self.x == 6 and BLOCKS[6].count(0) == 7:
        #   del BLOCKS[6]
        #  BLOCKS.insert(0, [0, 0, 0, 0, 0, 0, 0])
        # for i in range(randint(3, 7)):
        #    sdf = randint(0, 6)
        #   if not BLOCKS[0][sdf]:
        #      BLOCKS[0][sdf] = Block(0, sdf)


def draw1(screen):
    font = pygame.font.Font(None, 20)
    text = font.render("Оставшиеся жизни: " + str(lifes), True, (242, 61, 0))
    text_x = 20
    text_y = 600
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (242, 61, 0), (text_x - 10, text_y - 10, text_w + 20, text_h + 20), 1)


def draw2(screen):
    font = pygame.font.Font(None, 20)
    text = font.render("Очки: " + str(SCORE), True, (242, 61, 0))
    text_x = 470
    text_y = 600
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (242, 61, 0), (text_x - 10, text_y - 10, text_w + 20, text_h + 20), 1)


def draw3(screen):
    font = pygame.font.Font(None, 50)
    text = font.render("Вы выиграли!", True, (242, 61, 0))
    text_x = width // 2 - text.get_width() // 2
    text_y = height // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (242, 61, 0), (text_x - 10, text_y - 10, text_w + 20, text_h + 20), 1)
    text1 = font.render("Счёт: " + str(SCORE + lifes * 30), True, (242, 61, 0))
    text1_x = width // 2 - text1.get_width() // 2
    text1_y = height // 2 - text1.get_height() // 2 + 80
    text1_w = text1.get_width()
    text1_h = text1.get_height()
    screen.blit(text1, (text1_x, text1_y))
    pygame.draw.rect(screen, (242, 61, 0), (text1_x - 10, text1_y - 10, text1_w + 20, text1_h + 20), 1)
    pygame.display.flip()


def draw4(screen):
    font = pygame.font.Font(None, 50)
    text = font.render("Вы проиграли!", True, (242, 61, 0))
    text_x = width // 2 - text.get_width() // 2
    text_y = height // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (242, 61, 0), (text_x - 10, text_y - 10, text_w + 20, text_h + 20), 1)
    text1 = font.render("Счёт: " + str(SCORE + lifes * 30), True, (242, 61, 0))
    text1_x = width // 2 - text1.get_width() // 2
    text1_y = height // 2 - text1.get_height() // 2 + 80
    text1_w = text1.get_width()
    text1_h = text1.get_height()
    screen.blit(text1, (text1_x, text1_y))
    pygame.draw.rect(screen, (242, 61, 0), (text1_x - 10, text1_y - 10, text1_w + 20, text1_h + 20), 1)
    pygame.display.flip()


def start_game():
    global SCORE
    global final
    global lifes
    global speed
    global running
    global sticks
    global cirles
    global blocked
    global stick
    global BLOCKS
    global count
    global coun
    pygame.init()
    pygame.display.set_caption('ARCANOID')
    screen = pygame.display.set_mode(size)
    all_sprites = pygame.sprite.Group()
    sticks = pygame.sprite.Group()
    cirles = pygame.sprite.Group()
    blocked = pygame.sprite.Group()
    circle = Circle(250, 640, all_sprites, cirles)
    stick = Stick(screen, all_sprites, sticks)
    SCORE = 0
    final = 0
    lifes = 0
    speed = 100
    BLOCKS = []
    running = True
    for _ in range(7):
        BLOCKS.append([0] * 7)
    count = randint(35, 49)
    coun = count
    while coun:
        asd = randint(0, 6)
        sdf = randint(0, 6)
        if not BLOCKS[asd][sdf]:
            BLOCKS[asd][sdf] = Block(asd, sdf, all_sprites, blocked)
            coun -= 1

    clock = pygame.time.Clock()
    # r = [circle]
    # pygame.draw.rect(screen, (40, 70, 255), (250, 680, 60, 10), width=0)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #   r.append(Circle(*event.pos))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                stick.k = -1
                stick.status_move = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                stick.k = 1
                stick.status_move = True
        t = clock.tick()
        screen.fill((0, 0, 0))
        if stick.status_move:
            stick.move(screen, t)
        else:
            stick.move2(screen)
        circle.move(t)
        all_sprites.draw(screen)
        draw1(screen)
        draw2(screen)
        # pygame.draw.circle(screen, (255, 255, 255), , 10)
        # circle.rect = circle.rect.move(circle.x_pos, circle.y_pos)
        all_sprites.update()
        # speed += 4 * t / 1000 # любое число

        # for i in r:
        pygame.display.flip()
    screen.fill((0, 0, 0))
    # running = True
    if final == 'win':
        draw3(screen)
    else:
        draw4(screen)
    # while running:
    #   for event in pygame.event.get():
    #    if event.type == pygame.QUIT:
    #       running = False
    pygame.time.wait(3000)
    pygame.quit()


SCORE = 0
final = 0
lifes = 0
speed = 100
BLOCKS = []
running = True
count = randint(35, 49)
coun = 0
size = width, height = 560, 710
sticks = 0
cirles = 0
blocked = 0
stick = 0
