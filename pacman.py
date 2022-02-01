import pygame
import os
import sys
from PIL import Image
from threading import Timer
from random import choice
from math import sqrt

PLAYER_SPEED = 2  # 2 * 60(FPS) = 120; 120 / 20(cell_size) = 6(клеток в секунду)
ENEMY_SPEED = 2
FPS = 60
FULNM = 'enemy'
INDENT_X_ABOVE = 0
INDENT_Y_ABOVE = 50
INDENT_BELOW = 40
WIDTH = 560 + INDENT_X_ABOVE
HEIGHT = 620 + INDENT_Y_ABOVE + INDENT_BELOW


def draw_lifes(lifes, screen):
    image = pygame.transform.scale(pygame.image.load(load_file('packman1.png')),
                                   (23, 23))
    for i in range(lifes):
        screen.blit(image, (10 + i * (image.get_width() + 5),
                            HEIGHT - INDENT_BELOW + 3))


def draw_text(screen, s):
    font = pygame.font.SysFont('arial black', 18)
    text = font.render(f'HIGH SCORE {max(s)}', True, (255, 255, 255))
    text_x = WIDTH // 2 - text.get_width() // 2
    text_y = 10
    screen.blit(text, (text_x, text_y))
    text = font.render(f'SCORE {s[-1]}', True, (255, 255, 255))
    text_x = 10
    text_y = 10
    screen.blit(text, (text_x, text_y))


def load_file(name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    fullname = os.path.join(base_path + '/data_pacman/', name)
    if not os.path.isfile(fullname):
        print(f"Файл '{fullname}' не найден")
        sys.exit()
    else:
        return fullname


def scan_pict(cell_size):
    def pr(y, x):
        s = 0
        for y1 in range(y - 1, y + 2):
            for x1 in range(x - 1, x + 2):
                try:
                    if not board[y1][x1][2]:
                        s += 1
                except IndexError:
                    s += 1
        return s

    im = Image.open(load_file('field11.png'))
    board = []
    pixels = im.load()
    x, y = im.size  # ширина (x) и высота (y)
    for j in range(0, y, cell_size):
        row = []
        for i in range(0, x, cell_size):
            break_pr = True
            for k_j in range(cell_size):
                for k_i in range(cell_size):
                    if 9 * cell_size <= j + k_j <= 19 * cell_size and j != 14 * cell_size and \
                            (0 <= i + k_i <= 5 * cell_size or
                             x - 5 * cell_size <= i + k_i <= x):
                        row.append([0, 0, 0])
                        break_pr = False
                        break
                    elif i + k_i < x and j + k_j < y:
                        r, g, b, *arg = pixels[i + k_i, j + k_j]
                        if b != 0:
                            row.append([0, 0, 0])
                            break_pr = False
                            break
                if not break_pr:
                    break
            else:
                row.append([1, 0, 1])
        board.append(row.copy())
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x][0]:
                if pr(y, x) >= 7:
                    board[y][x][2] = 0
                if 9 <= y <= 19 and x != 6 and x != len(board[0]) - 7:
                    board[y][x][2] = 0
    im.close()
    return board


class Player(pygame.sprite.Sprite):
    def __init__(self, gr1, gr2, board, cell_size, y, x):
        super().__init__(gr1)
        self.type_image = 1
        self.timer = None
        self.gr = gr2
        self.can_eat = False
        self.way = 'l'
        self.way_m = ''
        self.check_move = True
        self.y = y
        self.x = x
        self.x_goal = 0
        self.y_goal = 0
        self.x_move = 0
        self.y_move = 0
        self.cell_size = cell_size
        self.board = board
        self.board.board[x][y][1] = 1
        self.image = pygame.transform.scale(pygame.image.load(load_file(f'packman{self.type_image}.png')), (20, 20))
        self.im_left()
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.cell_size + INDENT_X_ABOVE
        self.rect.y = self.y * self.cell_size + INDENT_Y_ABOVE
        self.set_pl()

    def im_right(self):
        self.image = pygame.transform.scale(pygame.image.load(load_file(f'packman{self.type_image}.png')), (20, 20))

    def im_left(self):
        self.image = pygame.transform.scale(pygame.image.load(load_file(f'packman{self.type_image}.png')), (20, 20))
        self.image = pygame.transform.rotate(self.image, 180)
        self.image = pygame.transform.flip(self.image, False, True)

    def im_up(self):
        self.image = pygame.transform.scale(pygame.image.load(load_file(f'packman{self.type_image}.png')), (20, 20))
        self.image = pygame.transform.rotate(self.image, 90)

    def im_down(self):
        self.image = pygame.transform.scale(pygame.image.load(load_file(f'packman{self.type_image}.png')), (20, 20))
        self.image = pygame.transform.rotate(self.image, 270)

    def set_pl(self):
        if self.way == 'r':
            self.x_goal = self.x + 1
            self.y_goal = self.y
            self.im_right()
            self.x_move = PLAYER_SPEED
            self.y_move = 0
        elif self.way == 'l':
            self.x_goal = self.x - 1
            self.y_goal = self.y
            self.im_left()
            self.x_move = -PLAYER_SPEED
            self.y_move = 0
        elif self.way == 'u':
            self.x_goal = self.x
            self.y_goal = self.y - 1
            self.im_up()
            self.x_move = 0
            self.y_move = -PLAYER_SPEED
        elif self.way == 'd':
            self.x_goal = self.x
            self.y_goal = self.y + 1
            self.im_down()
            self.x_move = 0
            self.y_move = PLAYER_SPEED

    def can_move(self, way):
        if (self.rect.x - INDENT_X_ABOVE) / 20 == self.x and \
                (self.rect.y - INDENT_Y_ABOVE) / 20 == self.y:
            if (way == 'l' or way == 'r') and (self.y == 14 and
                                               (self.x + 1 == self.board.width or self.x - 1 == -1)):
                return True
            if way == 'r' and self.board.board[self.y][self.x + 1][0]:
                return True
            elif way == 'l' and self.board.board[self.y][self.x - 1][0]:
                return True
            elif way == 'u' and self.board.board[self.y - 1][self.x][0]:
                return True
            elif way == 'd' and self.board.board[self.y + 1][self.x][0]:
                return True
        return False

    def do_move(self, way):
        if self.can_move(way):
            self.way = way
            self.way_m = ''
            self.set_pl()
        elif (self.way == 'r' and way == 'l' and self.board.board[self.y][self.x - 1][0]) or \
                (self.way == 'l' and way == 'r' and self.board.board[self.y][self.x + 1][0]) or \
                (self.way == 'u' and way == 'd' and self.board.board[self.y + 1][self.x][0]) or \
                (self.way == 'd' and way == 'u' and self.board.board[self.y - 1][self.x][0]):
            self.way = way
            self.way_m = ''
            self.set_pl()
        else:
            self.way_m = way

    def update(self):
        if any([True for i in self.gr if i.end]):
            return None
        if (self.rect.x - INDENT_X_ABOVE) / 20 == self.x_goal and \
                (self.rect.y - INDENT_Y_ABOVE) / 20 == self.y_goal:
            if self.type_image == 1:
                self.type_image = 2
            else:
                self.type_image = 1
            if self.y_goal == 14 and (self.x_goal == -1 or self.x_goal == self.board.width):
                if self.x_goal == -1:
                    self.x_goal = self.board.width - 1
                else:
                    self.x_goal = 0
                self.rect.x = self.cell_size * self.x_goal
            self.board.board[self.y][self.x][1] = 0
            self.board.board[self.y_goal][self.x_goal][1] = 1
            self.x = self.x_goal
            self.y = self.y_goal
            self.x_goal = -1
            self.y_goal = -1
            self.set_pl()
            if not self.can_move(self.way):
                self.x_move = 0
                self.y_move = 0
            if self.way_m != '' and self.can_move(self.way_m):
                self.way = self.way_m
                self.way_m = ''
                self.set_pl()
        self.rect.x += self.x_move
        self.rect.y += self.y_move


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, en_number, gr1, gr2, board, cell_size, speed, s):
        super().__init__(gr1, gr2)
        self.time_passed = 0
        self.sound = s
        self.speed = speed
        self.way_type = 'runaway'
        self.way = ''
        self.nextway = ''
        self.sec = 0
        self.sec_r = 5
        self.count_of_changewaytypes = 0
        self.gr = gr2
        self.player = player
        self.can_eat = False
        self.end = False
        self.timer = None
        self.timer1 = None
        self.check_im = False
        self.image_prev = None
        self.in_home = False
        self.out_home = False
        self.en_number = en_number
        self.x_goal = -1
        self.y_goal = -1
        self.x_move = 0
        self.y_move = 0
        self.x = 0
        self.y = 0
        self.cell_size = cell_size
        self.board = board
        self.im_right()
        self.rect = self.image.get_rect()
        if self.en_number == 1:
            self.way = 'l'
            self.x_tomove_r = 25
            self.y_tomove_r = 0
            self.x = 14
            self.y = 11
            self.set_pl()
            self.rect.x = self.x * self.cell_size + INDENT_X_ABOVE
            self.rect.y = self.y * self.cell_size + INDENT_Y_ABOVE
            self.choose_nextway()
        elif self.en_number == 2:
            self.x_tomove_r = 2
            self.y_tomove_r = 0
            self.home(1)
        elif self.en_number == 3:
            self.x_tomove_r = 27
            self.y_tomove_r = 35
            self.home(6)
        elif self.en_number == 4:
            self.x_tomove_r = 0
            self.y_tomove_r = 35
            self.home(10)

    def im_right(self):
        if not self.can_eat:
            self.image = pygame.transform.scale(pygame.image.load(load_file(f'{FULNM}{self.en_number}r.png')), (20, 20))

    def im_left(self):
        if not self.can_eat:
            self.image = pygame.transform.scale(pygame.image.load(load_file(f'{FULNM}{self.en_number}l.png')), (20, 20))

    def im_up(self):
        if not self.can_eat:
            self.image = pygame.transform.scale(pygame.image.load(load_file(f'{FULNM}{self.en_number}u.png')), (20, 20))

    def im_down(self):
        if not self.can_eat:
            self.image = pygame.transform.scale(pygame.image.load(load_file(f'{FULNM}{self.en_number}d.png')), (20, 20))

    def im_en1(self):
        self.image = pygame.transform.scale(pygame.image.load(load_file(f'enemy51.png')), (20, 20))

    def im_en2(self):
        self.image = pygame.transform.scale(pygame.image.load(load_file(f'enemy52.png')), (20, 20))

    def home(self, sec=None):
        self.in_home = True
        if sec is None:
            sec = self.en_number
        if self.en_number == 1:
            self.x = 11
            self.y = 13
        elif self.en_number == 2:
            self.x = 12
            self.y = 13
        elif self.en_number == 3:
            self.x = 15
            self.y = 13
        elif self.en_number == 4:
            self.x = 16
            self.y = 13
        self.rect.x = self.x * self.cell_size + INDENT_X_ABOVE
        self.rect.y = self.y * self.cell_size + INDENT_Y_ABOVE
        self.way = 'd'
        self.set_pl()
        self.timer = Timer(sec, self.go_out_home)
        self.timer.start()

    def go_out_home(self):
        self.in_home = False
        self.out_home = True

    def set_pl(self):
        if self.way == 'r':
            self.x_goal = self.x + 1
            self.y_goal = self.y
            self.im_right()
            self.x_move = self.speed
            self.y_move = 0
        elif self.way == 'l':
            self.x_goal = self.x - 1
            self.y_goal = self.y
            self.im_left()
            self.x_move = -self.speed
            self.y_move = 0
        elif self.way == 'u':
            self.x_goal = self.x
            self.y_goal = self.y - 1
            self.im_up()
            self.x_move = 0
            self.y_move = -self.speed
        elif self.way == 'd':
            self.x_goal = self.x
            self.y_goal = self.y + 1
            self.im_down()
            self.x_move = 0
            self.y_move = self.speed

    def can_move(self, way, x=None, y=None):
        if x is None:
            x = self.x
            y = self.y
            if (self.rect.x - INDENT_X_ABOVE) / 20 != x or \
                    (self.rect.y - INDENT_Y_ABOVE) / 20 != y:
                return False
        if (way == 'l' or way == 'r') and (y == 14 and
                                           (x + 1 == self.board.width or x - 1 == -1)):
            return True
        if way == 'r' and self.board.board[y][x + 1][0]:
            return True
        elif way == 'l' and self.board.board[y][x - 1][0]:
            return True
        elif way == 'u' and self.board.board[y - 1][x][0]:
            return True
        elif way == 'd' and self.board.board[y + 1][x][0]:
            return True
        return False

    def opponent(self, way):
        if way == 'r':
            return 'l'
        if way == 'l':
            return 'r'
        if way == 'u':
            return 'd'
        if way == 'd':
            return 'u'

    def choose_nextway(self):
        if self.way_type == 'runaway':
            x1 = self.x_tomove_r
            y1 = self.y_tomove_r
        elif self.way_type == 'pursuit':
            if self.en_number == 1:
                x1 = self.player.x
                y1 = self.player.y
            elif self.en_number == 2:
                if self.player.way == 'u':
                    x1 = self.player.x
                    y1 = self.player.y - 4
                elif self.player.way == 'd':
                    x1 = self.player.x
                    y1 = self.player.y + 4
                elif self.player.way == 'r':
                    x1 = self.player.x + 4
                    y1 = self.player.y
                elif self.player.way == 'l':
                    x1 = self.player.x - 4
                    y1 = self.player.y
            elif self.en_number == 3:
                if self.player.way == 'u':
                    x1 = self.player.x
                    y1 = self.player.y - 2
                elif self.player.way == 'd':
                    x1 = self.player.x
                    y1 = self.player.y + 2
                elif self.player.way == 'r':
                    x1 = self.player.x + 2
                    y1 = self.player.y
                elif self.player.way == 'l':
                    x1 = self.player.x - 2
                    y1 = self.player.y
                for i in self.gr:
                    if i.en_number == 1:
                        x1 = x1 + abs(i.x - x1)
                        y1 = y1 + abs(i.y - y1)
                        break
            elif self.en_number == 4:
                if abs(self.x_goal - self.player.x) + \
                        abs(self.y_goal - self.player.y) > 8:
                    x1 = self.player.x
                    y1 = self.player.y
                else:
                    x1 = self.x_tomove_r
                    y1 = self.y_tomove_r
        ways = ['r', 'l', 'u', 'd']
        ways_new = []
        for i in ways:
            if i != self.opponent(self.way) and self.can_move(i, self.x_goal,
                                                              self.y_goal):
                ways_new.append(i)
        if not self.can_eat and (self.way == 'l' or self.way == 'r') and \
                ((self.y_goal == 11 or self.y_goal == 23) and
                 (self.x_goal == 12 or self.x_goal == 15)):
            try:
                ways_new.remove('u')
            except ValueError:
                pass
        minn = -1
        way = ''
        if not self.can_eat:
            for i in ways_new:
                if i == 'r':
                    x = self.x_goal + 1
                    y = self.y_goal
                elif i == 'l':
                    x = self.x_goal - 1
                    y = self.y_goal
                elif i == 'u':
                    x = self.x_goal
                    y = self.y_goal - 1
                elif i == 'd':
                    x = self.x_goal
                    y = self.y_goal + 1
                s = round(sqrt((x - x1) ** 2 + (y - y1) ** 2), 2)
                if minn == s or abs(s - minn) < 0.1:
                    if way == 'u':
                        continue
                    elif i == 'u':
                        minn = s
                        way = i
                    elif way == 'l':
                        continue
                    elif i == 'l':
                        minn = s
                        way = i
                    elif way == 'd':
                        continue
                    elif i == 'd':
                        minn = s
                        way = i
                elif minn == -1 or minn > s:
                    minn = s
                    way = i
        else:
            way = choice(ways_new)
        self.nextway = way

    def update(self):
        if self.can_eat:
            self.time_passed += 1
        if not self.can_eat and self.count_of_changewaytypes <= 3:
            self.sec += 1
        if self.way_type == 'runaway' and self.sec / FPS == self.sec_r:
            self.nextway = self.opponent(self.way)
            self.count_of_changewaytypes += 1
            self.sec = 0
            self.way_type = 'pursuit'
        elif self.way_type == 'pursuit' and self.sec / FPS == 20:
            self.nextway = self.opponent(self.way)
            self.sec = 0
            self.way_type = 'runaway'
        if any([True for i in self.gr if i.end]):
            return None
        if any([True for i in range(self.rect.x - 2, self.rect.x + 3, 2)
                for k in range(self.player.rect.x - 2, self.player.rect.x + 3,
                               2) if i == k]) and \
                any([True for i in range(self.rect.y - 2, self.rect.y + 3, 2)
                     for k in range(self.player.rect.y - 2, self.player.rect.y + 3,
                                    2) if i == k]):
            if self.can_eat:
                self.sound.play()
                self.timer.cancel()
                self.board.s[-1] += 100
                self.can_eat_stop()
                self.home(1)
            else:
                self.end = True
                return None
        if (self.rect.x - INDENT_X_ABOVE) / 20 == self.x_goal and \
                (self.rect.y - INDENT_Y_ABOVE) / 20 == self.y_goal:
            if self.y_goal == 14 and (self.x_goal == -1 or self.x_goal == self.board.width):
                if self.x_goal == -1:
                    self.x_goal = self.board.width - 1
                else:
                    self.x_goal = 0
                self.rect.x = self.cell_size * self.x_goal
            self.board.board[self.y][self.x][1] = 0
            self.board.board[self.y_goal][self.x_goal][1] = -1
            self.x = self.x_goal
            self.y = self.y_goal
            self.x_goal = -1
            self.y_goal = -1
            if not self.in_home and not self.out_home:
                self.way = self.nextway
            self.set_pl()
            if not (self.y_goal == 14 and (self.x_goal == -1 or self.x_goal == self.board.width)):
                self.choose_nextway()
            if (self.way == 'r' or self.way == 'l') and self.x == 14 and \
                    self.out_home:
                self.board.board[self.y][self.x][1] = 0
                self.x = 14
                self.y = 11
                self.board.board[self.y][self.x][1] = -1
                self.rect.x = self.x * self.cell_size + INDENT_X_ABOVE
                self.rect.y = self.y * self.cell_size + INDENT_Y_ABOVE
                self.x_goal = 14
                self.y_goal = 11
                self.way = 'u'
                self.choose_nextway()
                self.way = self.nextway
                self.set_pl()
                self.choose_nextway()
                self.out_home = False
            if not self.can_move(self.way):
                if self.out_home and self.y == 13:
                    if self.en_number > 2:
                        self.way = 'l'
                    else:
                        self.way = 'r'
                    self.set_pl()
                elif self.out_home:
                    self.way = 'u'
                    self.set_pl()
                elif self.in_home:
                    if self.way == 'd':
                        self.way = 'u'
                    else:
                        self.way = 'd'
                    self.set_pl()
                else:
                    self.x_move = 0
                    self.y_move = 0
        self.rect.x += self.x_move
        self.rect.y += self.y_move

    def can_eat_stop(self):
        self.speed = PLAYER_SPEED
        self.can_eat = False
        if self.timer1 is not None:
            self.timer1.cancel()

    def change_im(self):
        if self.check_im:
            self.im_en1()
            self.check_im = False
            self.timer1 = Timer(0.5, self.change_im)
            self.timer1.start()
        else:
            self.im_en2()
            self.check_im = True
            self.timer1 = Timer(0.5, self.change_im)
            self.timer1.start()

    def can_eat_start(self):
        self.time_passed = 0
        if self.timer is not None and self.timer1 is not None:
            self.timer.cancel()
            self.timer1.cancel()
        # self.way_type = 'scared'
        self.speed = PLAYER_SPEED - 1
        self.can_eat = True
        self.check_im = False
        self.timer = Timer(5, self.can_eat_stop)
        self.timer.start()
        self.timer1 = Timer(3, self.change_im)
        self.timer1.start()
        self.im_en1()


class Board:
    def __init__(self, width, height, cell_size):
        self.count_sound = 0
        self.width = width
        self.height = height
        self.cell_size = cell_size
        # self.board = [[0] * width for _ in range(height)]
        self.board = scan_pict(cell_size)
        self.s = [0]

    def render_net(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen,
                                 (255, 255, 255),
                                 (x * self.cell_size + INDENT_X_ABOVE,
                                  y * self.cell_size + INDENT_Y_ABOVE,
                                  self.cell_size, self.cell_size), 1)

    def render_all(self, screen, player, enemies, sound1_1, sound1_2, sound2):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x][1] == 1 and self.board[y][x][2]:
                    if (y == 3 and (x == 1 or x == self.width - 2)) or \
                            (y == 23 and (x == 1 or x == self.width - 2)):
                        self.s[-1] += 50
                        if sound2 is not None:
                            sound2.play()
                        for i in enemies:
                            i.can_eat_start()
                    else:
                        self.s[-1] += 10
                        if sound1_1 is not None:
                            if self.count_sound == 0:
                                self.count_sound = 1
                                sound1_1.play()
                            else:
                                self.count_sound = 0
                                sound1_2.play()
                    self.board[y][x][2] = 0
                if self.board[y][x][2]:
                    if (y == 3 and (x == 1 or x == self.width - 2)) or \
                            (y == 23 and (x == 1 or x == self.width - 2)):
                        pygame.draw.circle(screen,
                                           (255, 255, 0),
                                           (x * self.cell_size +
                                            self.cell_size // 2 +
                                            INDENT_X_ABOVE,
                                            y * self.cell_size +
                                            self.cell_size // 2 +
                                            INDENT_Y_ABOVE),
                                           self.cell_size // 3)
                    else:
                        pygame.draw.circle(screen,
                                           (255, 255, 0),
                                           (x * self.cell_size +
                                            self.cell_size // 2 +
                                            INDENT_X_ABOVE,
                                            y * self.cell_size +
                                            self.cell_size // 2 +
                                            INDENT_Y_ABOVE),
                                           self.cell_size // 5)


class App:
    def __init__(self):
        # для игры
        self.all_sprites = pygame.sprite.Group()
        self.ghosts = pygame.sprite.Group()
        self.board = Board((WIDTH - INDENT_X_ABOVE) // 20,
                           (HEIGHT - INDENT_Y_ABOVE - INDENT_BELOW) // 20, 20)
        self.image = pygame.image.load(load_file('field11.png'))
        self.image_sound_n = 1
        self.image_sound = pygame.transform.scale(pygame.image.load(load_file(f'sound{self.image_sound_n}.png')),
                                                  (35, 35))
        self.lifes = 3
        self.s = 0
        self.music_now = 0
        self.pause = False

        pygame.init()
        self.clock = pygame.time.Clock()
        self.section = 'init'
        self.section_prev = ''
        self.check_section = True
        self.timer = None
        self.time_add = 0

        # звук
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pac-Man')
        self.sound_death = pygame.mixer.Sound(load_file('pacman_death.wav'))
        self.sound_death.set_volume(0.2)
        self.eat_coin_1 = pygame.mixer.Sound(load_file('munch_1.wav'))
        self.eat_coin_1.set_volume(0.2)
        self.eat_coin_2 = pygame.mixer.Sound(load_file('munch_2.wav'))
        self.eat_coin_2.set_volume(0.2)
        self.eat_bigcoin = pygame.mixer.Sound(load_file('munch_3.wav'))
        self.eat_bigcoin.set_volume(0.2)
        self.eat_enemy = pygame.mixer.Sound(load_file('eat_ghost.wav'))
        self.eat_enemy.set_volume(0.2)
        pygame.mixer.music.set_volume(0.2)

        # игрок и противники
        self.player = Player(self.all_sprites, self.ghosts, self.board, 20, 23, 14)
        self.create_enemies()

    def run(self):
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise pygame.error
                    elif event.type == pygame.WINDOWFOCUSLOST:
                        if self.section != 'stop':
                            pygame.mixer.music.pause()
                            for i in self.enemies:
                                if i.can_eat:
                                    i.timer.cancel()
                                    i.timer1.cancel()
                            self.section_prev = self.section
                            self.section = 'stop'
                            if self.section_prev == 'init':
                                self.timer.cancel()
                    elif event.type == pygame.WINDOWFOCUSGAINED:
                        if self.section == 'stop' and not self.pause:
                            pygame.mixer.music.unpause()
                            for i in self.enemies:
                                if i.can_eat:
                                    i.timer = Timer((4.4 - i.time_passed / 60),
                                                    i.can_eat_stop)
                                    i.timer.start()
                                    if i.time_passed / 60 < 3.4:
                                        i.timer1 = Timer((3.4 - i.time_passed / 60),
                                                         i.change_im)
                                    else:
                                        i.timer1 = Timer(0.5, i.change_im)
                                    i.timer1.start()
                            self.pause = False
                            self.section = self.section_prev
                            self.check_section = True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.pos[0] >= WIDTH - self.image_sound.get_width() and \
                                event.pos[1] <= 5 + self.image_sound.get_height():
                            if self.image_sound_n == 1:
                                self.image_sound_n = 2
                                self.sound_death.set_volume(0)
                                self.eat_coin_1.set_volume(0)
                                self.eat_coin_2.set_volume(0)
                                self.eat_bigcoin.set_volume(0)
                                self.eat_enemy.set_volume(0)
                                pygame.mixer.music.set_volume(0)
                            else:
                                self.image_sound_n = 1
                                self.sound_death.set_volume(0.2)
                                self.eat_coin_1.set_volume(0.2)
                                self.eat_coin_2.set_volume(0.2)
                                self.eat_bigcoin.set_volume(0.2)
                                self.eat_enemy.set_volume(0.2)
                                pygame.mixer.music.set_volume(0.2)
                            self.image_sound = pygame.transform.scale(
                                pygame.image.load(load_file(f'sound{self.image_sound_n}.png')),
                                (35, 35))
                    elif event.type == pygame.KEYDOWN:
                        if self.section == 'play':
                            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                                self.player.do_move('r')
                            if pygame.key.get_pressed()[pygame.K_LEFT]:
                                self.player.do_move('l')
                            if pygame.key.get_pressed()[pygame.K_UP]:
                                self.player.do_move('u')
                            if pygame.key.get_pressed()[pygame.K_DOWN]:
                                self.player.do_move('d')
                        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                raise pygame.error
                            else:
                                if self.section != 'stop':
                                    pygame.mixer.music.pause()
                                    for i in self.enemies:
                                        if i.can_eat:
                                            i.timer.cancel()
                                            i.timer1.cancel()

                                    self.pause = True
                                    self.section_prev = self.section
                                    self.section = 'stop'
                                    if self.section_prev == 'init':
                                        self.timer.cancel()
                                else:
                                    pygame.mixer.music.unpause()
                                    for i in self.enemies:
                                        if i.can_eat:
                                            i.timer = Timer((4.4 - i.time_passed / 60),
                                                            i.can_eat_stop)
                                            i.timer.start()
                                            if i.time_passed / 60 < 3.4:
                                                i.timer1 = Timer((3.4 - i.time_passed / 60),
                                                                 i.change_im)
                                            else:
                                                i.timer1 = Timer(0.5, i.change_im)
                                            i.timer1.start()
                                    self.pause = False
                                    self.section = self.section_prev
                                    self.check_section = True
                if self.section == 'init':
                    self.time_add += 1
                    self.start_section()
                elif self.section == 'play':
                    self.check_music()
                    self.screen.fill((0, 0, 0))
                    self.screen.blit(self.image_sound, (WIDTH - self.image_sound.get_width() - 10, 5))
                    self.screen.blit(self.image, (INDENT_X_ABOVE, INDENT_Y_ABOVE))
                    # board.render_net(screen)
                    self.board.render_all(self.screen, self.player, self.enemies, self.eat_coin_1,
                                          self.eat_coin_2, self.eat_bigcoin)
                    self.all_sprites.update()
                    draw_text(self.screen, self.board.s)
                    self.check_situation()
                    self.all_sprites.draw(self.screen)
                    draw_lifes(self.lifes, self.screen)
                    self.s += 1
                    self.clock.tick(FPS)
                    pygame.display.flip()
                elif self.section == 'stop':
                    self.clock.tick(FPS)
        except pygame.error or KeyboardInterrupt or InterruptedError:
            if self.timer is not None:
                self.timer.cancel()
            pygame.quit()
            with open('records_from_pacman.txt', 'w', encoding='UTF-8') as file:
                file.write(f'Осталось жизней: {self.lifes}\nМаксимальный счет: {max(self.board.s)}')
            sys.exit()

    def check_situation(self):
        if any([True for i in self.enemies if i.end]):
            if self.lifes != 1:
                pygame.mixer.music.pause()
                self.s = 0
                self.lifes -= 1
                self.screen.fill((0, 0, 0))
                self.screen.blit(pygame.transform.scale(pygame.image.load(load_file(f'looselife.png')),
                                                        (WIDTH, HEIGHT)), (0, 0))
                pygame.display.flip()
                self.sound_death.play()
                pygame.time.delay(2000)
                self.all_sprites = pygame.sprite.Group()
                self.ghosts = pygame.sprite.Group()
                self.board.s.append(0)
                self.image = pygame.image.load(load_file('field11.png'))
                self.player = Player(self.all_sprites, self.ghosts, self.board, 20, 23, 14)
                self.create_enemies()
                self.section = 'init'
                self.check_section = True
                self.music_now = 1
                self.time_add = 0
            else:
                self.exit(0)
        if len([1 for y in range(self.board.height) for x in range(self.board.width) if
                self.board.board[y][x][2]]) == 0:
            self.exit(1)

    def start_section(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.image_sound, (WIDTH - self.image_sound.get_width() - 10, 5))
        draw_text(self.screen, self.board.s)
        self.screen.blit(self.image, (INDENT_X_ABOVE, INDENT_Y_ABOVE))
        self.all_sprites.draw(self.screen)
        draw_lifes(self.lifes, self.screen)
        self.board.render_all(self.screen, self.player, self.enemies, self.eat_coin_1,
                              self.eat_coin_2, self.eat_bigcoin)
        self.screen.blit(pygame.transform.scale(pygame.image.load(load_file(f'ready.png')),
                                                (WIDTH - 100, HEIGHT // 2)), (50, -30))
        pygame.display.flip()
        if self.check_section:
            if self.time_add == 1:
                pygame.mixer.music.load(load_file('pacman_beginning.wav'))
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            self.check_section = False
            self.timer = Timer(4 - self.time_add // 60, self.end_initsection)
            self.timer.start()

    def end_initsection(self):
        pygame.mixer.music.stop()
        self.section = 'play'

    def check_music(self):
        if not any([True for i in self.enemies if i.can_eat]) and \
                (self.s % (FPS + 10) == 0 or self.music_now == 1):
            self.music_now = 0
            pygame.mixer.music.load(load_file('siren_1.wav'))
            pygame.mixer.music.play()
        elif any([True for i in self.enemies if i.can_eat]) and \
                (self.s % (FPS + 10) == 0 or self.music_now == 0):
            self.s = 0
            self.music_now = 1
            pygame.mixer.music.load(load_file('power_pellet.wav'))
            pygame.mixer.music.play()

    def create_enemies(self):
        self.enemies = [Enemy(self.player, 1, self.all_sprites, self.ghosts, self.board, 20, ENEMY_SPEED,
                              self.eat_enemy),
                        Enemy(self.player, 2, self.all_sprites, self.ghosts, self.board, 20, ENEMY_SPEED,
                              self.eat_enemy),
                        Enemy(self.player, 3, self.all_sprites, self.ghosts, self.board, 20, ENEMY_SPEED,
                              self.eat_enemy),
                        Enemy(self.player, 4, self.all_sprites, self.ghosts, self.board, 20, ENEMY_SPEED,
                              self.eat_enemy)]

    def exit(self, way):
        if not way:
            pygame.mixer.music.pause()
            self.sound_death.play()
        self.screen.blit(pygame.transform.scale(pygame.image.load(load_file(f'gameover.jpg')),
                                                (WIDTH, HEIGHT)), (0, 0))
        pygame.display.flip()
        pygame.time.delay(1000)
        pygame.quit()
        with open('records_from_pacman.txt', 'w', 'UTF-8') as file:
            file.write(f'Осталось жизней: {self.lifes}\nМаксимальный счет: {max(self.board.s)}')
        sys.exit()


if __name__ != '__main__':
    app = App()
    app.run()
