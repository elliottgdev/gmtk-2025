import math

import pygame
import sys

from pygame import Vector2


class Game:
    def __init__(self):
        pygame.init()

        self.resolution_scale = 3
        self.window = pygame.display.set_mode((640 * self.resolution_scale, 360 * self.resolution_scale))
        self.display = pygame.Surface((640, 360))
        pygame.display.set_caption('trackmorph')
        self.clock = pygame.time.Clock()

        self.track_img = pygame.image.load('test_map.png').convert()
        self.car_img = pygame.image.load('car.png').convert()
        self.car_img.set_colorkey((0, 222, 255))

        self.car_pos = Vector2(0, 0)
        self.car_vel = 0
        self.car_speed = 5
        self.car_handle = 2
        self.car_dir = 0
        self.car_rect = pygame.Rect(0, 0, 16, 16)
        self.drift_amount = 0
        self.drift_boosts = [90, 180, 260]

        self.boost_ui = pygame.image.load('boost.png').convert()
        self.boost_ui.set_colorkey((0, 222, 255))

        #             accel, decel, left , right, drift, item
        self.input = [False, False, False, False, False, False]

    def run(self):
        while True:
            self.display.fill((0, 0, 0))
            pygame.display.set_caption(f'trackmorph | fps: {int(self.clock.get_fps())}')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.input[0] = True
                    if event.key == pygame.K_s:
                        self.input[1] = True
                    if event.key == pygame.K_a:
                        self.input[2] = True
                    if event.key == pygame.K_d:
                        self.input[3] = True
                    if event.key == pygame.K_SPACE:
                        self.input[4] = True
                    if event.key == pygame.K_LCTRL:
                        self.input[5] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        self.input[0] = False
                    if event.key == pygame.K_s:
                        self.input[1] = False
                    if event.key == pygame.K_a:
                        self.input[2] = False
                    if event.key == pygame.K_d:
                        self.input[3] = False
                    if event.key == pygame.K_SPACE:
                        self.input[4] = False
                    if event.key == pygame.K_LCTRL:
                        self.input[5] = False

            #if not drifting // if no direction is held while trying to start drift (give grace if attempting to drift just before selecting direction)
            if not self.input[4] or turn_dir == 0:
                if self.drift_amount > self.drift_boosts[2]:
                    print('beeg boost')
                    self.car_vel = -(self.car_speed + 5)
                elif self.drift_amount > self.drift_boosts[1]:
                    print('mid boost')
                    self.car_vel = -(self.car_speed + 3)
                elif self.drift_amount > self.drift_boosts[0]:
                    print('smol boost')
                    self.car_vel = -(self.car_speed + 2.3)

                move = 0
                turn_dir = 0
                self.drift_amount = 0

                #if key w, move up
                if self.input[0] and not self.input[1]:
                    move -= 1
                #if key s, move down
                elif self.input[1] and not self.input[0]:
                    move += 1
                #if key a, turn left
                if self.input[2]:
                    turn_dir += 1
                #if key s, turn right
                if self.input[3]:
                    turn_dir -= 1

                turn_amount = turn_dir
            # if drifting pause inputs
            elif self.input[4] and move == -1:
                turn_amount = turn_dir

                if self.input[2]:
                    turn_amount += 0.3
                if self.input[3]:
                     turn_amount -= 0.3

                #increase drift bonus depending on how tight the drift is
                #inside drift
                if abs(turn_amount) > 1:
                    self.drift_amount += 3
                #outside drift
                elif abs(turn_amount) < 1:
                    self.drift_amount += 1
                #regular drift
                else:
                    self.drift_amount += 2

            #turn car based on turn_dir
            self.car_dir += (self.car_handle * (self.car_vel / self.car_speed)) * (turn_dir * abs(turn_amount))

            #accelerate and decelerate
            if move != 0:
                self.car_vel += 0.2 * move
            else:
                #slow car
                if self.car_vel >= 0.1:
                    self.car_vel -= 0.06
                elif self.car_vel <= -0.1:
                    self.car_vel += 0.06
                #if velocity is too low, just stop velocity
                else:
                    self.car_vel = 0

            if self.input[5]:
                self.input[5] = False
                self.car_vel = -(self.car_speed + 5)

            #cap speed
            #reverse cap
            if self.car_vel > self.car_speed / 2.5:
                self.car_vel -= 0.3
            #regular cap
            elif self.car_vel < -self.car_speed:
                self.car_vel += 0.3

            #move car based on velocity and direction
            self.car_pos.x -= (self.car_vel * math.sin(math.radians(self.car_dir)))
            self.car_pos.y += (self.car_vel * math.cos(math.radians(self.car_dir)))
            self.car_rect.x = self.car_pos.x
            self.car_rect.y = self.car_pos.y

            car_img = pygame.transform.rotate(self.car_img, -self.car_dir)

            self.display.blit(self.track_img, (-self.car_pos.x + 340, -self.car_pos.y + 180))
            car_img_rect = car_img.get_rect()
            car_img_rect.x = 340 - car_img.get_width() / 2
            car_img_rect.y = 180 - car_img.get_height() / 2
            car_rect = self.car_rect
            car_rect.x = 340 - 8
            car_rect.y = 180 - 8
            #pygame.draw.rect(self.display, (0, 255, 0), car_img_rect)
            pygame.draw.rect(self.display, (255, 255, 0), car_rect)
            self.display.blit(car_img, (340 - car_img.get_size()[0] / 2, 180 - car_img.get_size()[1] / 2))

            #drift ui
            if self.input[4]:
                drift_ui = pygame.Rect(340 - 30, 180 - 30, 10, 3)

                drift_ui.width = self.drift_amount / 5
                if drift_ui.width > 60:
                    drift_ui.width = 60

                if self.drift_amount > self.drift_boosts[2]:
                    drift_ui_colour = (255, 0, 0)
                elif self.drift_amount > self.drift_boosts[1]:
                    drift_ui_colour = (0, 255, 0)
                elif self.drift_amount > self.drift_boosts[0]:
                    drift_ui_colour = (0, 0, 255)
                else:
                    drift_ui_colour = (100, 100, 100)

                pygame.draw.rect(self.display, drift_ui_colour, drift_ui)

            self.display.blit(self.boost_ui, (25, 25))

            screen = pygame.transform.scale(self.display, (640 * self.resolution_scale, 360 * self.resolution_scale))
            self.window.blit(screen, (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

Game().run()