import math
import os.path

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

        self.track_img = [pygame.image.load('track.png').convert(), pygame.image.load('track_lap2.png').convert()]
        self.track_file = open('track.txt', 'r')

        self.game_state = 'playing'
        self.animation_tick = 0

        readmode = None
        writing_lap = 0
        self.checkpoints = list()
        self.walls = list()
        self.offroads = list()
        walls = list()
        checkpoints = list()
        offroads = list()
        self.max_laps = 1
        for line in self.track_file.readlines():
            if line.startswith('checkpoints'):
                readmode = 0
            elif line.startswith('walls'):
                readmode = 1
            elif line.startswith('offroads'):
                readmode = 2
            elif line.startswith('#'):
                pass
            elif line.startswith('lap'):
                writing_lap += 1
                self.checkpoints.append(checkpoints)
                self.walls.append(walls)
                self.offroads.append(offroads)
                checkpoints = list()
                walls = list()
                offroads = list()
                self.max_laps += 1
            else:
                if readmode == 0:
                    line_ = line.split(' ')
                    point_one = (int(line_[0].strip()), int(line_[1].strip()))
                    point_two = (int(line_[2].strip()), int(line_[3].strip()))

                    checkpoints.append((point_one, point_two))
                elif readmode == 1:
                    line_ = line.split(' ')
                    point_one = (int(line_[0].strip()), int(line_[1].strip()))
                    point_two = (int(line_[2].strip()), int(line_[3].strip()))

                    walls.append((point_one, point_two))
                elif readmode == 2:
                    line_ = line.split(' ')
                    topleft = (int(line_[0].strip()), int(line_[1].strip()))
                    size = (int(line_[2].strip()), int(line_[3].strip()))

                    offroads.append(pygame.Rect(topleft[0], topleft[1], size[0], size[1]))

        self.current_checkpoint = 0
        self.lap = 1
        self.time = 0
        self.best_time = 99999999
        self.displayed_time = 0
        self.lap_ui_tick = -1
        self.lap_position = 370

        self.car_img = pygame.image.load('car.png').convert()
        self.car_img.set_colorkey((0, 222, 255))

        self.car_pos = Vector2(509, 1251)
        self.old_car_pos = Vector2(509, 1251)
        self.car_vel = 0
        self.car_speed = 4
        self.car_handle = 1.5
        self.car_dir = -35
        self.car_rect = pygame.Rect(0, 0, 16, 16)
        self.drift_amount = 0
        self.drift_boosts = [75, 140, 200]
        self.is_offroad = False

        self.ghost_data = list()
        self.best_ghost = None
        self.ghost_tick = 0
        self.saved_ghost = False

        if os.path.isfile('ghost.txt'):
            with open('ghost.txt', 'r') as file:
                self.best_ghost = list()
                line_ = 0
                for line in file.readlines():
                    if line_ == 0:
                        self.best_time = float(line.strip())
                    else:
                        data = line.split(' ')

                        self.best_ghost.append(Vector2(float(data[0].strip()), float(data[1].strip())))
                    line_ += 1

        self.boost_ui = pygame.image.load('boost.png').convert()
        self.boost_ui.set_colorkey((0, 222, 255))

        #             accel, decel, left , right, drift, item
        self.input = [False, False, False, False, False, False]

        self.flag_animation = pygame.image.load('flag.png').convert()
        self.flag_animation.set_colorkey((0, 222, 255))

        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 12)
        self.ui_atlas = pygame.image.load('ui.png').convert()
        self.ui_atlas.set_colorkey((0, 222, 255))

    def initialise(self):
        self.animation_tick = 0
        self.ghost_tick = 0

        self.current_checkpoint = 0
        self.lap = 1
        self.time = 0
        self.displayed_time = 0
        self.lap_ui_tick = -1

        self.car_pos = Vector2(509, 1251)
        self.old_car_pos = Vector2(509, 1251)
        self.car_vel = 0
        self.car_speed = 4
        self.car_handle = 1.5
        self.car_dir = -35
        self.car_rect = pygame.Rect(0, 0, 16, 16)
        self.drift_amount = 0
        self.drift_boosts = [75, 140, 200]

        self.ghost_data = list()

    def run(self):
        while True:
            #timer
            if self.clock.get_time() > 0 and self.clock.get_fps() > 0:
                #increment by .016 because the game is locked to 60fps so this should count seconds
                if self.game_state == 'playing':
                    self.time += .016666666

                self.animation_tick += 1

                #awful code to make the displayed timer always show the tens digit in seconds, breaks for one frame but i dont care enough to fix
                if self.time % 60 < 10:
                    self.displayed_time = f'{int(self.time / 60)}:{f'0{'%.3f'%(self.time % 60)}'}'
                else:
                    self.displayed_time = f'{int(self.time / 60)}:{'%.3f'%(self.time % 60)}'
            #self.display.fill((0, 0, 0))
            pygame.display.set_caption(f'trackmorph | lap {self.lap} | time {self.displayed_time} | fps: {int(self.clock.get_fps())}')

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
                    if event.key == pygame.K_e:
                        self.game_state = 'finished'
                        self.animation_tick = 0

            #the time trial
            if self.game_state == 'playing':
                #offroad speed penalty
                max_speed = self.car_speed
                self.is_offroad = False
                for offroad in self.offroads[self.lap - 1]:
                    if self.car_rect.colliderect(offroad):
                        self.is_offroad = True

                if self.is_offroad:
                    max_speed = self.car_speed / 3
                    self.drift_amount = 0

                #if not drifting // if no direction is held while trying to start drift (give grace if attempting to drift just before selecting direction)
                if not self.input[4] or turn_dir == 0 or self.is_offroad:
                    if self.drift_amount > self.drift_boosts[2]:
                        #print('beeg boost')
                        self.car_vel = -(self.car_speed + 5)
                    elif self.drift_amount > self.drift_boosts[1]:
                        #print('mid boost')
                        self.car_vel = -(self.car_speed + 3.6)
                    elif self.drift_amount > self.drift_boosts[0]:
                        #print('smol boost')
                        self.car_vel = -(self.car_speed + 2.8)

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
                elif self.input[4] and move == -1 and not self.is_offroad:
                    turn_amount = turn_dir

                    if self.input[2]:
                        turn_amount += 0.4
                    if self.input[3]:
                         turn_amount -= 0.4

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
                print(turn_dir)

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
                    self.car_vel = -(self.car_speed + 6)

                #cap speed
                #reverse cap
                if self.car_vel > max_speed / 2.5:
                    self.car_vel -= 0.3
                #regular cap
                elif self.car_vel < -max_speed:
                    self.car_vel += 0.3

                #wall collisions
                collide = False
                for wall in self.walls[self.lap - 1]:
                    if self.car_rect.clipline(wall[0], wall[1]):
                        collide = True

                if collide:
                    self.car_vel = -self.car_vel + (-0 * move)
                    self.car_pos.x -= (self.car_vel * math.sin(math.radians(self.car_dir))) * 2
                    self.car_pos.y += (self.car_vel * math.cos(math.radians(self.car_dir))) * 2
                else:
                    #move car based on velocity and direction
                    self.car_pos.x -= (self.car_vel * math.sin(math.radians(self.car_dir)))
                    self.car_pos.y += (self.car_vel * math.cos(math.radians(self.car_dir)))

                self.car_rect = pygame.Rect(self.car_pos.x - 8, self.car_pos.y - 8, 16, 16)

                car_img = pygame.transform.rotate(self.car_img, -self.car_dir)

                self.display.blit(self.track_img[self.lap - 1], (-self.car_pos.x + 340, -self.car_pos.y + 180))
                car_img_rect = car_img.get_rect()
                car_img_rect.x = 340 - car_img.get_width() / 2
                car_img_rect.y = 180 - car_img.get_height() / 2
                car_rect = pygame.Rect(340 - 8, 180 - 8, 16, 16)

                #arbitarary ghost cutoff point (i think this is like 2m:30s)
                if self.animation_tick < 9000:
                    if self.animation_tick % 2 == 0:
                        self.ghost_data.append((float('%.3f'%self.car_pos.copy().x), float('%.3f'%self.car_pos.copy().y)))
                        self.ghost_tick += 1

                    if self.best_ghost != None:
                        if self.ghost_tick >= len(self.best_ghost) - 1:
                            self.ghost_tick = len(self.best_ghost) - 2

                        ghost_pos = (self.best_ghost[self.ghost_tick + 1][0] -self.car_pos.x + 340, self.best_ghost[self.ghost_tick + 1][1] -self.car_pos.y + 180)

                        pygame.draw.circle(self.display, (203, 219, 252), ghost_pos, 8)

                for offroad in self.offroads[self.lap - 1]:
                    pygame.draw.rect(self.display, (0, 100, 0), (offroad.x - self.car_pos.x + 340, offroad.y - self.car_pos.y + 180, offroad.width, offroad.height))

                for wall in self.walls[self.lap - 1]:
                    pygame.draw.line(self.display, (0, 0, 255),
                                     (-self.car_pos.x + 340 + wall[0][0], - self.car_pos.y + 180 + wall[0][1]),
                                     (-self.car_pos.x + 340 + wall[1][0], -self.car_pos.y + 180 + wall[1][1]))

                check = 0
                for checkpoint in self.checkpoints[self.lap - 1]:
                    #check for checkpoint collisions
                    if self.car_rect.clipline(checkpoint[0], checkpoint[1]):
                        #if the checkpoint we hit is 1 bigger than our current checkpoint (or first checkpoint and we on last)
                        #update our current checkpoint
                        if check == (self.current_checkpoint + 1) % len(self.checkpoints[self.lap - 1]):
                            self.current_checkpoint = check
                            #if we hit the first checkpoint, update the lap
                            if check == 0:
                                self.lap += 1
                                self.lap_ui_tick = self.animation_tick + 90

                                if self.lap >= self.max_laps:
                                    self.game_state = 'finished'
                                    self.animation_tick = 0
                                    self.input = [False, False, False, False, False, False]
                                    self.saved_ghost = False
                                    break

                        pygame.draw.line(self.display, (255, 0, 255), (-self.car_pos.x + 340 + checkpoint[0][0], - self.car_pos.y + 180 + checkpoint[0][1]), (-self.car_pos.x + 340 + checkpoint[1][0], -self.car_pos.y + 180 + checkpoint[1][1]))
                    else:
                        pygame.draw.line(self.display, (255, 0, 0), (-self.car_pos.x + 340 + checkpoint[0][0], - self.car_pos.y + 180 + checkpoint[0][1]), (-self.car_pos.x + 340 + checkpoint[1][0], -self.car_pos.y + 180 + checkpoint[1][1]))
                    check += 1

                #pygame.draw.rect(self.display, (0, 255, 0), self.car_rect)
                #pygame.draw.rect(self.display, (255, 255, 0), car_rect)
                self.display.blit(car_img, (340 - car_img.get_size()[0] / 2, 180 - car_img.get_size()[1] / 2))

                #drift ui
                if self.input[4]:
                    drift_ui = pygame.Rect(340 - 40, 180 - 30, 10, 3)

                    drift_ui.width = self.drift_amount / 3
                    if drift_ui.width > 80:
                        drift_ui.width = 80

                    if self.drift_amount > self.drift_boosts[2]:
                        drift_ui_colour = (255, 0, 0)
                    elif self.drift_amount > self.drift_boosts[1]:
                        drift_ui_colour = (0, 255, 0)
                    elif self.drift_amount > self.drift_boosts[0]:
                        drift_ui_colour = (0, 0, 255)
                    else:
                        drift_ui_colour = (100, 100, 100)

                    pygame.draw.rect(self.display, drift_ui_colour, drift_ui)
                    if drift_ui.width > 0:
                        self.display.blit(self.ui_atlas, (340 - 40 + 8, 180 - 30 - 17), (176, 48, 64, 16))

                #the rest of the ui
                if self.lap < self.max_laps:
                    #lap ui
                    self.display.blit(self.ui_atlas, (25, 25), (0, (self.lap - 1) * 48, 144, 48))
                    self.display.blit(self.ui_atlas, (340 - 148 / 2, self.lap_position), (144, 96, 128, 48))

                    if self.animation_tick <= self.lap_ui_tick:
                        if self.lap_position < 370:
                            self.lap_position -= 2
                        else:
                            self.lap_position = 360
                        if self.lap_position < 290:
                            self.lap_position = 290
                    else:
                        self.lap_position += 2

                    #timer
                    self.display.blit(self.ui_atlas, (640 - 25 - 288, 25), (144, 0, 288, 48))
                    self.display.blit(self.font.render(f'{self.displayed_time}', True, (255, 255, 255)), (640 - 25 - 288 + 155, 37))

                #self.display.blit(self.boost_ui, (25, 25))
            #finished race
            elif self.game_state == 'finished':
                pygame.draw.rect(self.display, (255, 255, 255), pygame.Rect(255, 135, 170, 90))
                pygame.draw.rect(self.display, (0, 0, 0), pygame.Rect(260, 140, 160, 80))

                flag_animation = (int(self.animation_tick / 6)) % 6

                self.saved_ghost = 0

                if self.animation_tick >= 0:
                    self.display.blit(pygame.transform.flip(self.flag_animation, True, False), (262 + 26, 142), (1, 18 * flag_animation, 21, 18))
                    self.display.blit(self.flag_animation, (344 + 26, 142), (0, 18 * flag_animation, 21, 18))
                    self.display.blit(self.font.render('Done!', True, (255, 255, 255)), (284 + 26, 141))
                if self.animation_tick > 20:
                    self.display.blit(self.small_font.render(f'> Time: {self.displayed_time}', True, (255, 255, 255)), (262, 142 + 20))
                if self.animation_tick > 40:
                    if self.best_time < self.time:
                        if self.best_time % 60 < 10:
                            displayed_time = f'{int(self.best_time / 60)}:{f'0{'%.3f' % (self.best_time % 60)}'}'
                        else:
                            displayed_time = f'{int(self.best_time / 60)}:{'%.3f' % (self.best_time % 60)}'

                        self.display.blit(self.small_font.render(f'> Best: {displayed_time}', True, (255, 255, 255)), (262, 142 + 20 + 12))
                    elif self.best_time >= self.time:
                        self.display.blit(self.small_font.render(f'> Best: New best time!', True, (255, 255, 255)), (262, 142 + 20 + 12))
                        self.save_ghost()


                if self.saved_ghost == 1:
                    self.display.blit(self.small_font.render(f'> Ghost saved.', True, (255, 255, 255)), (262, 142 + 20 + 12 + 12))
                elif self.saved_ghost == 2:
                    self.display.blit(self.small_font.render(f'> Failed to save ghost.', True, (255, 255, 255)), (262, 142 + 20 + 12 + 12))

                if self.animation_tick > 80:
                    self.display.blit(self.small_font.render('Press W to try again.', True, (255, 255, 255)), (262, 142 + 60))

                    if self.input[0]:
                        if self.best_time == None or self.best_time > self.time:
                            self.best_time = self.time
                            self.best_ghost = self.ghost_data

                            with open('ghost.txt', 'w') as file:
                                lines_to_write = list()
                                lines_to_write.append(str(self.time) + '\n')
                                for line in self.ghost_data:
                                    lines_to_write.append(f'{line[0]} {line[1]}\n')
                                file.writelines(lines_to_write)

                        self.initialise()

                        self.game_state = 'playing'

            screen = pygame.transform.scale(self.display, (640 * self.resolution_scale, 360 * self.resolution_scale))
            self.window.blit(screen, (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

    def save_ghost(self):
        if not self.saved_ghost:
            self.best_time = self.time
            self.best_ghost = self.ghost_data

            try:
                with open('ghost.txt', 'w') as file:
                    lines_to_write = list()
                    lines_to_write.append(str(self.time) + '\n')
                    for line in self.ghost_data:
                        lines_to_write.append(f'{line[0]} {line[1]}\n')
                    file.writelines(lines_to_write)
                    self.saved_ghost = 1
            except Exception as e:
                print(e)
                self.saved_ghost = 2
            self.saved_ghost = True


Game().run()