import pygame
import time
import random
import os
import math 

pygame.font.init()
WIDTH,HEIGHT = 1750, 1000
WIN = pygame.display.set_mode((WIDTH,HEIGHT))      #for background
pygame.display.set_caption("Spaceship and Survival") 

#image input
myShip = pygame.transform.scale(pygame.image.load("myshipbattle.jpeg"), (50, 50))
Enemy = pygame.transform.scale(pygame.image.load("aliens.jpeg"), (50, 50))         #image taken by blit
BG = pygame.transform.scale(pygame.image.load("spacebackground.jpeg"),((WIDTH,HEIGHT)))

class Ship:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None 
        self.lasers = []
        self.cooldown_counter = 0
    def draw(self, window):
        window.blit(self.ship_image, (self.x, self.y))
    def get_width(self):
        return self.ship_image.get_width()
    def get_height(self):
        return self.ship_image.get_height()
    

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_image = myShip
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health
    def shoot(self, target_pos):
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        dist = (dx**2 + dy**2) ** 0.5
        if dist == 0:
            dist = 1
        dir_x = dx/dist
        dir_y = dy/dist
        self.lasers.append(Laser(self.x + 25, self.y + 25, dir_x, dir_y, color=(255, 0, 0)))


class Laser: #only circle
    def __init__(self, x, y, dir_x, dir_y, color=(255, 0, 0), speed=5):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = speed
        self.color = color
        self.radius = 4
    def move(self):
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
    def draw(self, window):
        pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)
    def off_screen(self, width, height):
        return not(0 <= self.x <= width and 0 <= self.y <= height)
    def collide(self, target):
        return target.x < self.x < target.x + target.get_width() and target.y < self.y < target.y + target.get_height()

class Enemy(Ship):
    COLOR_MAP = {"red": (Enemy)}
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_image= self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.lasers = []
        self.shoot_cooldown = random.randint(30, 90)
    def move(self, target_x, target_y, vel):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx**2 + dy**2) ** 0.5
        if distance != 0:
            self.x += vel* dx/distance
            self.y += vel* dy/distance
    def shoot(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist == 0:
            dist = 1
        dir_x = dx / dist
        dir_y = dy / dist
        self.lasers.append(Laser(self.x + 25, self.y + 25, dir_x, dir_y))
    def move_laser(self, player):
        for laser in self.lasers[:]:
            laser.move()
            if laser.collide(player):
                player.health -= 1
                self.lasers.remove(laser)
            elif laser.off_screen(WIDTH, HEIGHT):
                self.lasers.remove(laser)


def main():
    run = True
    FPS = 60
    life = 5
    scores = 0
    main_font = pygame.font.SysFont("comicsans", 50)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    trap_phase = False
    trap_timer = 0
    trap_pattern = []
    trap_cooldown = 0
    noncore = 0

    player_vel = 23
    player  = Player(875, 500)
    clock = pygame.time.Clock()

    def drawWindow():
        WIN.blit(BG, (0,0))      #open background
        life_label = main_font.render(f"lives: {life}", 1,(255, 255, 255)) 
        enemy_total = main_font.render(f"Enemy total: {len(enemies)}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score: {scores}", 1,(255, 255, 255))
        WIN.blit(life_label, (10, 10)) 
        WIN.blit(enemy_total, (10, 70))
        WIN.blit(score_label, (WIDTH - score_label.get_width() -10, 10))
        noncore_label = main_font.render(f"Noncore: {noncore}", 1, (255, 255, 0))
        WIN.blit(noncore_label, (10, 130))

        for enemy in enemies:
            enemy.draw(WIN)
            for laser in enemy.lasers:
                laser.draw(WIN)

        player.draw(WIN)
        for laser in player.lasers:
            laser.draw(WIN)
        pygame.display.update()

    while run:
        clock.tick(FPS)
        
        if len(enemies) == 0:
            wave_length = 2 + scores// 50
            for i in range(wave_length):
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    x = random.randint(0, WIDTH)
                    y = random.randint(-100, -40)
                elif side == "bottom":
                    x = random.randint(0, WIDTH)
                    y = random.randint(HEIGHT + 40, HEIGHT + 100)
                elif side == "left":
                    x = random.randint(-100, -40)
                    y = random.randint(0, HEIGHT)
                elif side == "right":
                    x = random.randint(WIDTH + 40, WIDTH + 100)
                    y = random.randint(0, HEIGHT)
                enemy = Enemy(x, y, "red")
                enemies.append(enemy)

        for enemy in enemies:
            enemy.move(player.x, player.y, enemy_vel)
            enemy.shoot_cooldown -= 1
            if enemy.shoot_cooldown <= 0:
                enemy.shoot(player)
                enemy.shoot_cooldown = random.randint(60, 120)
            enemy.move_laser(player)

        for laser in player.lasers[:]:
            laser.move()
            for enemy in enemies[:]:
                if laser.collide(enemy):
                    enemies.remove(enemy)
                    player.lasers.remove(laser)
                    scores += 10
                    life += 1
                    break
            else:
                if laser.off_screen(WIDTH, HEIGHT):
                    player.lasers.remove(laser)

        if scores == 540 and not trap_phase:
            enemies.clear()
            trap_phase = True
            trap_timer = pygame.time.get_ticks()
            trap_patterns = []
        if trap_phase:
            now = pygame.time.get_ticks()
            if trap_cooldown <= 0:
                for _ in range(random.randint(3, 6)):
                    angle = random.uniform(0, 2*3.14)
                    dir_x = math.cos(angle)
                    dir_y = math.sin(angle)
                    trap_patterns.append({
                        "x":player.x + 25, 
                        "y":player.y + 25, 
                        "dx":dir_x, 
                        "dy":dir_y,
                        "start_time":now, 
                        "warn":True
                    })
                trap_cooldown = 2000
            else:
                trap_cooldown -= clock.get_time()
            for trap in trap_patterns[:]:
                if trap["warn"]:
                    end_x = trap["x"] + trap["dx"]* 300
                    end_y = trap["y"] + trap["dy"]* 300
                    pygame.draw.line(WIN, (150, 150, 150), (trap["x"], trap["y"]), (end_x, end_y), 2)
                if now - trap["start_time"] > 800:
                    trap["warn"] = False
                    trap["start_time"] = now
            else:
                trap["x"] += trap["dx"] * 10
                trap["y"] += trap["dy"] * 10
                pygame.draw.line(WIN, (250, 0, 0), (trap["x"], trap["y"]), (trap["x"] + trap["dx"] * 10, trap["y"] + trap["dy"] * 10), 3)
                if player.x < trap["x"] < player.x + 50 and player.y < trap["y"] < player.y + 50:
                    life -= 1 
                    if trap in trap_patterns:
                        trap_patterns.remove(trap)
            if now - trap_timer > 15000 and not trap_patterns: #15 seconds
                trap_phase = False
                trap_cooldown = 0
                enemies.append(Enemy(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100, "red")))
                #enemies[0].lasers.clear()
        if not trap_phase and len(enemies) == 1:
            enemy = enemies[0]
            if player.x < enemy.x < player.x + 50 and player.y < enemy.y < player.y + 50:
                life -= 1
                enemies.remove(enemy)
            for laser in player.lasers[:]:
                if laser.collide(enemy):
                    enemies.remove(enemy)
                    player.lasers.remove(laser)
                    noncore += 1
                    break

        for event in pygame.event.get():        #to quit
            if event.type == pygame.QUIT:        #if a button click, pygame quit
                run = False     #quit pygame
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                player.shoot(mouse_pos)
        key = pygame.key.get_pressed()
        if key[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        key = pygame.key.get_pressed() 
        if key[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        key = pygame.key.get_pressed()
        if key[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT:
            player.y += player_vel
        key = pygame.key.get_pressed()
        if key[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH :
            player.x += player_vel 
        if key[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        key = pygame.key.get_pressed() 
        if key[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        key = pygame.key.get_pressed()
        if key[pygame.K_DOWN] and player.y + player_vel + player.get_height() < HEIGHT:
            player.y += player_vel
        key = pygame.key.get_pressed()
        if key[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH :
            player.x += player_vel 
        for enemy in enemies:
            enemy.move(player.x, player.y, enemy_vel)

        drawWindow()
main()