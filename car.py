import pygame
import os
import sys
from PIL import Image
from random import randint, sample
from Box2D import (b2CircleShape, b2EdgeShape, b2FixtureDef, b2PolygonShape,
                   b2World)
from math import degrees

PPM = 20.0  # пиксель на метр
FPS = 60
TIME_STEP = 1.0 / FPS
WIDTH, HEIGHT = 800, 500


def load_file(name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    fullname = os.path.join(base_path + '/data_car/', name)
    if not os.path.isfile(fullname):
        print(f"Файл '{fullname}' не найден")
        sys.exit()
    else:
        return fullname


class Car(pygame.sprite.Sprite):
    def __init__(self, group, world, x=2.5, y=abs(HEIGHT - (HEIGHT - 250)) / PPM):
        super().__init__(group)
        self.world = world
        self.x = x
        self.y = y
        self.wheel_radius = 0.5
        self.wheel_separation = 3.0
        self.scale = (1, 1)  # применяется только для шасси
        self.wheel_axis = (0, 1)
        self.wheel_torques = [50.0, 30.0]
        self.wheel_drives = [True, False]
        self.hz = 5.0
        self.zeta = 0.9
        # chassis - шасси
        self.chassis_vertices = [(-2.3, -0.5), (2.2, -0.5), (2.2, 0.0), (0.0, 0.9), (-1.15, 0.9), (-2.3, 0.2)]
        self.chassis_vertices = [(self.scale[0] * x, self.scale[1] * y) for x, y in self.chassis_vertices]
        self.chassis = self.world.CreateDynamicBody(position=(self.x, self.y),
                                                    fixtures=b2FixtureDef(
                                                        shape=b2PolygonShape(vertices=self.chassis_vertices),
                                                        density=2))
        self.wheels, self.springs, self.wheels_sprites = [], [], []
        for x, torque, can_drive in zip([-self.wheel_separation / 2.0, self.wheel_separation / 2.0],
                                        self.wheel_torques, self.wheel_drives):
            wheel = self.world.CreateDynamicBody(
                position=(self.x + x, self.y - self.wheel_radius),
                fixtures=b2FixtureDef(
                    shape=b2CircleShape(radius=self.wheel_radius),
                    density=1,
                    friction=1))

            spring = world.CreateWheelJoint(
                bodyA=self.chassis,
                bodyB=wheel,
                anchor=wheel.position,
                axis=self.wheel_axis,
                motorSpeed=0.0,
                maxMotorTorque=torque,
                enableMotor=can_drive,
                frequencyHz=self.hz,
                dampingRatio=self.zeta)
            wheel_sprite = pygame.sprite.Sprite()
            group.add(wheel_sprite)
            self.wheels_sprites.append(wheel_sprite)
            self.wheels.append(wheel)
            self.springs.append(spring)
        self.image = None
        self.update(0, 0)

    def update(self, m_side, m_top):
        # колеса

        for ind, wheel in enumerate(self.wheels):
            position = wheel.transform.position * PPM
            position = (position[0] - wheel.fixtures[0].shape.radius * PPM + m_side,
                        HEIGHT - position[1] - wheel.fixtures[0].shape.radius * PPM + m_top)
            image_main = Image.open(load_file('wheel.png'))
            image_rotated = image_main.rotate(degrees(wheel.angle)).resize(
                (int(wheel.fixtures[0].shape.radius * PPM * 2),
                 int(wheel.fixtures[0].shape.radius * PPM * 2)))
            image_wheel = pygame.image.fromstring(image_rotated.tobytes(), image_rotated.size, image_rotated.mode)
            self.wheels_sprites[ind].image = image_wheel
            self.wheels_sprites[ind].rect = image_wheel.get_rect()
            self.wheels_sprites[ind].rect.x, self.wheels_sprites[ind].rect.y = position
            image_main.close()
            image_rotated.close()
        # машина

        vertices = [(self.chassis.transform * v) * PPM for v in self.chassis.fixtures[0].shape.vertices]
        vertices = [[round(v[0]), HEIGHT - round(v[1])] for v in vertices][::-1]
        image_main = Image.open(load_file('car.png'))
        image_rotated = image_main.rotate(round(degrees(self.chassis.angle), 2), expand=True)
        pixels = image_rotated.load()
        x, y = image_rotated.size
        x_mn, y_mn, x_mx, y_mx = -1, -1, -1, -1
        for i in range(x):
            for j in range(y):
                if pixels[i, j] != (0, 0, 0, 0):
                    if x_mn == -1 or x_mn > i:
                        x_mn = i
                    if y_mn == -1 or y_mn > j:
                        y_mn = j
                    if x_mx == -1 or x_mx < i:
                        x_mx = i
                    if y_mx == -1 or y_mx < j:
                        y_mx = j
        image_rotated = image_rotated.crop((x_mn, y_mn, x_mx, y_mx))
        self.image = pygame.image.fromstring(image_rotated.tobytes(), image_rotated.size, image_rotated.mode)
        self.image.set_colorkey((0, 0, 0))
        # image_rotated.save('car_test.png', quality=95)
        image_main.close()
        image_rotated.close()
        self.rect = self.image.get_rect()
        self.rect.x = max(vertices, key=lambda x: x[0])[0] - self.image.get_width() + m_side
        # print(self.rect.x - m_side)
        self.rect.y = max(vertices, key=lambda x: x[1])[1] - self.image.get_height() + 5 + m_top


class App:
    def __init__(self, len_road=6000, fuel_consumption=5):
        pygame.init()
        self.len_road = len_road
        self.fuel_consumption = fuel_consumption
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()
        self.world = b2World(gravity=(0, -10))
        self.ground = self.world.CreateStaticBody(shapes=b2EdgeShape())
        ground_to_screen1 = pygame.Surface((self.len_road + 30, HEIGHT))  # + 30 т.к. это погрешность в создании карты
        vertices, future_bridges = self.create_map(ground_to_screen1, self.len_road)
        self.all_road = [k.copy() for i in vertices for k in i]
        self.len_road = vertices[-1][-1][0]
        self.len_road_ind = len(self.all_road)
        # print(self.len_road)
        self.ground_to_screen = pygame.Surface((vertices[-1][-1][0], HEIGHT))
        self.ground_to_screen.fill((11, 160, 255))
        self.ground_to_screen.blit(ground_to_screen1.copy(), (0, 0))
        vertices[-1].extend([[vertices[-1][-1][0], vertices[-1][-1][1] - i] for i in range(200)])
        vertices[0] = [[vertices[0][0][0], vertices[0][0][1] - i] for i in range(200)][::-1] + vertices[0]
        self.bridges = []
        for gr in range(len(vertices)):
            x_l = 0
            y_l = 0
            for coord in vertices[gr]:
                if x_l != 0 or y_l != 0:
                    self.ground.CreateEdgeFixture(
                        vertices=[(x_l, y_l), (coord[0] / PPM, abs(coord[1] - HEIGHT) / PPM)],
                        friction=0.7)
                x_l, y_l = coord[0] / PPM, abs(coord[1] - HEIGHT) / PPM
            if gr != len(vertices) - 1:
                self.bridges.append(self.create_bridge((1, 0.3), ((future_bridges[gr][0] + 10) / PPM,
                                                                  abs(HEIGHT - future_bridges[gr][2]) / PPM - 0.2),
                                                       int((future_bridges[gr][1] - future_bridges[gr][0]) // PPM + 1),
                                                       density=2))
        self.car = Car(self.all_sprites, self.world)
        self.petrol = 100
        self.check_petrol = 0
        self.petrol_check = [[True, self.all_road[i][0]] for i in range(2000, self.len_road_ind, 2000)]
        self.check_end = FPS * 3
        self.section = 'play'
        self.m_side, self.m_top = 0, 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Car game')
        pygame.mixer.music.set_volume(0.5)

    def run(self):
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise pygame.error
                    elif event.type == pygame.WINDOWFOCUSLOST:
                        self.section = 'stop'
                    elif event.type == pygame.WINDOWFOCUSGAINED:
                        self.section = 'play'
                    elif event.type == pygame.KEYDOWN:
                        if pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_s] or \
                                pygame.key.get_pressed()[pygame.K_LEFT]:
                            self.car.springs[0].motorSpeed = 100
                            self.car.springs[1].motorSpeed = 100
                        elif pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_w] or \
                                pygame.key.get_pressed()[pygame.K_RIGHT]:
                            self.car.springs[0].motorSpeed = -100
                            self.car.springs[1].motorSpeed = -100
                        elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
                            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                raise pygame.error
                            if self.section == 'play':
                                self.section = 'stop'
                            else:
                                self.section = 'play'
                if (not pygame.key.get_pressed()[pygame.K_ESCAPE] and not any(pygame.key.get_pressed())) or \
                        self.petrol <= 0:
                    self.car.springs[0].motorSpeed = 0
                    self.car.springs[1].motorSpeed = 0
                if self.section == 'play':
                    if self.petrol > 0:
                        self.petrol -= self.fuel_consumption / FPS
                    vertices = [(self.car.chassis.transform * v) * PPM
                                for v in self.car.chassis.fixtures[0].shape.vertices]
                    vertices = [(v[0], HEIGHT - v[1]) for v in vertices]
                    target_x = (min(vertices, key=lambda x: x[0])[0] + max(vertices, key=lambda x: x[0])[0]) // 2
                    target_x1 = min(vertices, key=lambda x: x[0])[0]
                    target_x2 = max(vertices, key=lambda x: x[0])[0]
                    # target_y = (min(vertices, key=lambda x: x[1])[1] + max(vertices, key=lambda x: x[1])[1]) // 2
                    target_y2 = max(vertices, key=lambda x: x[1])[1]

                    self.m_side = int(-(target_x - WIDTH // 2))
                    # self.m_top = -(target_y - HEIGHT // 2)

                    for ind in range(len(self.petrol_check)):
                        if self.petrol_check[ind][0] and target_x1 <= self.petrol_check[ind][1] <= target_x2:
                            if len(self.petrol_check[ind]) == 2 or (len(self.petrol_check[ind]) == 3 and
                                                                    target_y2 >= self.petrol_check[ind][2]):
                                self.petrol = 100
                                self.petrol_check[ind][0] = False

                    self.screen.fill((11, 160, 255))
                    self.screen.blit(self.ground_to_screen, (self.m_side, self.m_top))
                    self.draw_bridges()
                    self.drawandcheck_flag(target_x2)
                    self.draw_petrol(target_x)
                    self.all_sprites.update(self.m_side, self.m_top)
                    self.all_sprites.draw(self.screen)
                    self.world.Step(TIME_STEP, 10, 10)
                    pygame.display.flip()
                    self.check_gameend()
                    self.clock.tick(FPS)
                elif self.section == 'stop':
                    self.clock.tick(FPS)

        except pygame.error or KeyboardInterrupt or InterruptedError:
            self.exit()

    def check_gameend(self):
        if self.petrol > 0 and self.check_petrol != 0:
            self.check_petrol = 0
        if self.check_end / FPS < 3 and (self.check_end / FPS + 0.1 >= 3 or self.check_end / FPS == 2 or
                                         self.check_end / FPS == 1):
            pygame.mixer.music.load(load_file('part_end.mp3'))
            pygame.mixer.music.play()
        elif self.check_end == 0 or self.check_petrol == FPS * 3:
            pygame.mixer.music.load(load_file('end.mp3'))
            pygame.mixer.music.play()
            self.screen.blit(pygame.image.load(load_file('end.jpg')), (0, 0))
            pygame.display.flip()
            pygame.time.wait(1000)
            raise pygame.error
        elif self.petrol <= 0:
            if self.check_petrol % FPS == 0:
                pygame.mixer.music.load(load_file('part_end.mp3'))
                pygame.mixer.music.play()
            self.check_petrol += 1

    def draw_petrol(self, target_x):
        im = pygame.image.load(load_file('petrol.png'))
        for x1 in range(2000, self.len_road_ind, 2000):
            if self.petrol_check[x1 // 2000 - 1][0]:
                s = 0
                for i in self.all_road[x1:min([x1 + im.get_width(), len(self.all_road)])]:
                    s += i[1]
                y = round(s / min([im.get_width(), len(self.all_road) - x1])) - im.get_height()
                self.screen.blit(im, (self.all_road[x1][0] + self.m_side, y))
                if len(self.petrol_check[x1 // 2000 - 1]) == 2:
                    self.petrol_check[x1 // 2000 - 1].append(y)
        x = target_x + self.m_side - WIDTH // 2
        self.screen.blit(im, (x, 3 + self.m_top))
        if self.petrol > 50:
            color = (0, 255, 0)
        elif self.petrol > 20:
            color = (255, 165, 0)
        else:
            color = (255, 0, 0)
        pygame.draw.rect(self.screen, color, (x + im.get_width() + 5, 3 + self.m_top + 8, round(self.petrol) * 2,
                                              im.get_height() - 10))

    def drawandcheck_flag(self, target_x):
        x = target_x + self.m_side
        im = pygame.transform.scale(pygame.image.load(load_file('flag.png')), (100, 100))
        self.screen.blit(im, (self.all_road[-100][0] + self.m_side,
                              self.all_road[-100][1] - im.get_height()))
        if self.all_road[-100][0] + self.m_side <= x <= self.all_road[-100][0] + self.m_side + im.get_width():
            self.check_end -= 1
        elif self.check_end != FPS * 3:
            self.check_end = FPS * 3

    def draw_bridges(self):
        for bridge in self.bridges:
            for part_bridge in bridge:
                vertices = [(part_bridge.transform * v) * PPM for v in part_bridge.fixtures[0].shape.vertices]
                vertices = [[round(v[0]) + self.m_side, HEIGHT - round(v[1]) + self.m_top] for v in vertices][::-1]
                pygame.draw.polygon(self.screen, (100, 36, 36), vertices)

    def create_map(self, screen, width, x=0, y=HEIGHT - 200):
        # создание осн дороги
        screen.fill((11, 160, 255))
        x_st = x
        x_end = 0
        way = ''
        limit_y = 0
        len_to_alignment = 30
        len_alignment = randint(30, 150)
        vertices = [[[x + i, y] for i in range(100 * 2 + 1)]]
        x += 100 * 2 + 1
        straight_ground = 0
        try:
            bridges_ind = sample(range(1, width // 600), randint(1, round(width / 600 / 3)))
        except:
            bridges_ind = []
        bridges = []
        while x < width - 100 * 2:
            if y >= screen.get_height() - 200:
                way = 1  # top
                limit_y = 100
            else:
                way = -1  # down
                limit_y = 400
            row = [[x + k, y] for k in range(len_to_alignment)]
            if way == 1:
                for i in range(0, len_to_alignment, 6):
                    y -= 2
                    for k in range(i, len_to_alignment):
                        row[k][1] = y
            else:
                for i in range(0, len_to_alignment, 6):
                    y += 2
                    for k in range(i, len_to_alignment):
                        row[k][1] = y
            x += len_to_alignment
            vertices[-1].extend(row)
            width_way = randint(100, 600)
            height_way = randint(50, limit_y) if way == 1 else randint(50, HEIGHT - limit_y)
            k = width_way / height_way
            l = 0
            for i in range(width_way):
                vertices[-1].append([x, y])
                if i // k == l:
                    l += 1
                    if way == 1:
                        y -= 1
                    else:
                        y += 1
                    if y == limit_y:
                        break
                x += 1
                if x >= width - 100 * 2 - len_to_alignment:
                    break
            straight_ground += 1
            if x + len_to_alignment <= width - 100 * 2:
                row = [[x + k, y] for k in range(len_to_alignment)]
                if way == 1:
                    for i in range(0, len_to_alignment, 6):
                        y -= 2
                        for k in range(i, len_to_alignment):
                            row[k][1] = y
                else:
                    for i in range(0, len_to_alignment, 6):
                        y += 2
                        for k in range(i, len_to_alignment):
                            row[k][1] = y
                x += len_to_alignment
                vertices[-1].extend(row)
            if x + len_alignment <= width - 100 * 2:
                if straight_ground not in bridges_ind:
                    vertices[-1].extend([[x + i, y] for i in range(len_alignment)])
                    x += len_alignment
                    if x >= width - 100 * 2:
                        break
                    len_alignment = randint(30, 150)
                else:
                    a = sample(range(100, 200, 10), 1)[0]
                    bridges.append([x, x + a, y])
                    x += a
                    vertices.append([])
        vertices[-1].extend([[x + i, y] for i in range(100 * 2 + 1)])
        x += 100 * 2 + 1
        # vertices[-1] = vertices[-1][:len(vertices[-1]) - (x - width)]
        vertices_toworld = [i.copy() for i in vertices]
        for gr in range(len(vertices)):
            for i in range(len(vertices[gr]) - 1, -1, -1):
                vertices[gr].append([vertices[gr][i][0], vertices[gr][i][1] + 20])
        ground = [vertices[gr][len(vertices[gr]) // 2:][::-1] + [[vertices_toworld[gr][-1][0], screen.get_height()],
                                                                 [vertices_toworld[gr][0][0], screen.get_height()]] for
                  gr in range(len(vertices))]
        for gr in range(len(vertices)):
            pygame.draw.polygon(screen, (40, 170, 40), vertices[gr])
        for gr in range(len(ground)):
            pygame.draw.polygon(screen, (130, 75, 10), ground[gr])

        # создание доп текстур

        for gr in range(len(ground)):
            ground[gr].pop()
            ground[gr].pop()
            x_end = ground[gr][-1][0]
            for i, ind in zip(range(ground[gr][0][0], x_end - x_end % 50 - 1, 50),
                              range(0, len(ground[gr]) - len(ground[gr]) % 50 - 1, 50)):
                im = Image.open(load_file('rock.png'))
                a = randint(30, 50)
                k = round(im.width / im.height, 2) if im.width < im.height else round(im.height / im.width, 2)
                im = im.resize((a, int(a * k)))
                im = im.rotate(randint(-90, 90), expand=True)
                im1 = pygame.image.fromstring(im.tobytes(), im.size, im.mode)
                im.close()
                size = im1.get_size()
                y1 = max(ground[gr][ind:min([ind + size[0] - 2, len(ground[gr]) - 2])], key=lambda x: x[1])[1] + 10
                try:
                    x = randint(i, i + im.size[0])
                    if x + size[0] > x_end:
                        x -= x + size[0] - x_end
                    y = randint(y1, screen.get_height() - size[1] - ((screen.get_height() - size[1]) - y1) // 2)
                    screen.blit(im1, (x, y))
                except:
                    pass
                try:
                    x = randint(i, i + im.size[0])
                    if x + size[0] > x_end:
                        x -= x + size[0] - x_end
                    y = randint(y1 + ((screen.get_height() - size[1]) - y1) // 2, screen.get_height() - size[1])
                    screen.blit(im1, (x, y))
                except:
                    pass
                    # print(y1 + ((screen.get_height() - size[1]) - y1) // 2, screen.get_height() - size[1])
        for gr in range(len(ground)):
            x_end = ground[gr][-1][0]
            for i, ind in zip(range(ground[gr][0][0], x_end - x_end % 50 - 1, 750),
                              range(0, len(ground[gr]) - len(ground[gr]) % 50 - 1, 750)):
                im = pygame.image.load(load_file(f'cloud{randint(1, 2)}.png'))
                size = im.get_size()
                try:
                    x = randint(i, i + 750 - size[0])
                    if x + size[0] > x_end:
                        x -= x + size[0] - x_end
                    y = randint(0, min(ground[gr][ind:min([ind + 748, len(ground[gr]) - 2])], key=lambda x: x[1])[1] -
                                size[1] - 100)
                    screen.blit(im, (x, y))
                except:
                    pass
        return vertices_toworld, bridges

    def create_bridge(self, size, coord, plank_count, friction=0.6, density=1.0):
        width, height = size
        x, y = coord
        plank = b2FixtureDef(
            shape=b2PolygonShape(box=(width / 2, height / 2)),
            friction=friction,
            density=density)
        bodies = []
        prevBody = self.ground
        for i in range(plank_count):
            body = self.world.CreateDynamicBody(
                position=(x + width * i, y),
                fixtures=plank)
            bodies.append(body)
            self.world.CreateRevoluteJoint(
                bodyA=prevBody,
                bodyB=body,
                anchor=(x + width * (i - 0.5), y))
            prevBody = body
        self.world.CreateRevoluteJoint(
            bodyA=prevBody,
            bodyB=self.ground,
            anchor=(x + width * (plank_count - 0.5), y))
        self.world.Step(TIME_STEP, 10, 10)

        return bodies

    def exit(self):
        pygame.quit()
        # sys.exit()


def start_game():
    pygame.init()
    pygame.display.set_caption('Difficulty')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill((11, 160, 255))
    screen.blit(pygame.transform.scale(pygame.image.load(load_file('1.png')), (WIDTH, HEIGHT)), (0, 0))
    pygame.display.flip()
    pr = True
    running = True
    k = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pr = False
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                if y <= 135:
                    k = 5
                    running = False
                elif 182 <= y <= 318:
                    k = 10
                    running = False
                elif y >= 363:
                    k = 15
                    running = False
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        pr = False
                        running = False
    if pr:
        app = App(fuel_consumption=k)
        app.run()
