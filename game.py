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

        self.input = [False, False, False, False]

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
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        self.input[0] = False
                    if event.key == pygame.K_s:
                        self.input[1] = False
                    if event.key == pygame.K_a:
                        self.input[2] = False
                    if event.key == pygame.K_d:
                        self.input[3] = False

            move = 0
            if self.input[0]:
                move -= 1
            if self.input[1]:
                move += 1
            if self.input[2]:
                self.car_dir += self.car_handle * (self.car_vel / self.car_speed)
            if self.input[3]:
                self.car_dir -= self.car_handle * (self.car_vel / self.car_speed)

            if move == 1:
                self.car_vel += 0.2
            elif move == -1:
                self.car_vel -= 0.2
            elif move == 0:
                if self.car_vel >= 0.1:
                    self.car_vel -= 0.06
                elif self.car_vel <= -0.1:
                    self.car_vel += 0.06
                else:
                    self.car_vel = 0

            if self.car_vel > self.car_speed:
                self.car_vel = self.car_speed
            elif self.car_vel < -self.car_speed:
                self.car_vel = -self.car_speed

            print(self.car_vel)

            self.car_pos.x -= (self.car_vel * math.sin(math.radians(self.car_dir)))
            self.car_pos.y += (self.car_vel * math.cos(math.radians(self.car_dir)))

            car_img = pygame.transform.rotate(self.car_img, -self.car_dir)

            self.display.blit(self.track_img, (-self.car_pos.x + 340, -self.car_pos.y + 180))
            self.display.blit(car_img, (340 - car_img.get_size()[0] / 2, 180 - car_img.get_size()[1] / 2))
            pygame.draw.rect(self.display, (255, 0, 0), car_img.get_rect())

            screen = pygame.transform.scale(self.display, (640 * self.resolution_scale, 360 * self.resolution_scale))
            self.window.blit(screen, (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

Game().run()