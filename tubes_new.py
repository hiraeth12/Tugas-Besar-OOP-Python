import os
import random
import math
import pygame
from pygame.locals import *
from os import listdir
from os.path import isfile, join

pygame.mixer.pre_init(44100,16,2,4096)
pygame.init()

pygame.display.set_caption("Tubes")

WIDTH, HEIGHT = 1360, 800
FPS = 60
PLAYER_VEL = 10
window = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.mixer.music.load("anthem_barca.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

congrats_sound = pygame.mixer.Sound("siuu.mp3")
congrats_sound.set_volume(2)

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "(1)Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size) #ambil gambar dari asset terrain
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_block2(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 64, size, size) #ambil gambar dari asset terrain
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_block3(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0,128, size, size) #ambil gambar dari asset terrain
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_block4(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0,0, size, size) #ambil gambar dari asset terrain
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 10
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block2(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block2(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block3(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block3(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block4(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block4(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class HealthBar:
    def __init__(self, x, y, width, height, max_health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_health = max_health
        self.current_health = max_health
    def draw(self, window):
        outline_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(window, (255, 0, 0), outline_rect, 2)

        health_width = (self.current_health / self.max_health) * self.width
        health_rect = pygame.Rect(self.x, self.y, health_width, self.height)
        pygame.draw.rect(window, (0, 255, 0), health_rect)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
    def on(self):
        self.animation_name = "on"
    def off(self):
        self.animation_name = "off"
    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Saw(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "saw")
        self.saw = load_sprite_sheets("Traps", "Saw", width, height)
        self.image = self.saw["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
    def on(self):
        self.animation_name = "on"
    def off(self):
        self.animation_name = "off"
    def loop(self):
        sprites = self.saw[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Checkpoint(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "checkpoint")
        self.checkpoint = load_sprite_sheets("Items", "Finish",width, height)
        self.image = self.checkpoint["bendera"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "bendera"

    def on(self):
        self.animation_name = "bendera"
    
    def loop(self):
        sprites = self.checkpoint[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def reset_game(player):
    player.rect.x = 100
    player.rect.y = 100
    return 0


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
        elif obj and obj.name == "saw":
            player.make_hit()
        elif obj and obj.name == "checkpoint": 
            offset_x = reset_game(player)
            player.rect.x = 100
            player.rect.y = 100

pygame.font.init()
font = pygame.font.SysFont('Arial', 36)


def main(window):
    global checkpoint_reached
    checkpoint_reached = False
    global initial_offset_x
    clock = pygame.time.Clock()
    background, bg_image = get_background("LeBG.jpg")

    block_size = 96

    initial_offset_x = 0

    player = Player(100 ,100, 50, 50)
    health_bar = HealthBar(50, 30, 200, 20, 100) 

    checkpoint = Checkpoint(6364, HEIGHT - block_size* 3.3, 64, 64)
    checkpoint.on()
    
    # congrats_text = new_font.render('Congrats', True, (255, 255, 255))  # Warna teks putih, Anda bisa mengganti sesuai keinginan
    # window.blit(congrats_text, (50, 50))  # x_pos dan y_pos adalah posisi di mana Anda ingin teks tersebut ditampilkan

    saws =[]
    start_saw = 4616
    gaps = 192
    
    for j in range(4): 
        saw = Saw(start_saw + j * gaps, HEIGHT - block_size - 64, 38, 38)
        saws.append(saw)
    for saw in saws:
        saw.on()
    
    fires = []
    start_x = 2208 
    gap = 32  

    for i in range(9): 
        fire = Fire(start_x + i * gap, HEIGHT - block_size - 64, 16, 32)
        fires.append(fire)
    for fire in fires:
        fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size,(WIDTH*5) // block_size)]

    objects = [*floor,
               #Block3(-1280, HEIGHT - block_size * 2, block_size), #tinggi / y
               #Block3(2496, HEIGHT - block_size * 2, block_size),#mendatar tanah/floor
               
               Block4(block_size * 7, HEIGHT - block_size *3, block_size),
               Block4(block_size * 8, HEIGHT - block_size *3, block_size),
               Block4(block_size * 9, HEIGHT - block_size *3, block_size),
               
               Block(block_size * 20, HEIGHT - block_size *2, block_size),#mendatar
               Block(block_size * 21, HEIGHT - block_size *2, block_size),
               Block(block_size * 21, HEIGHT - block_size *3, block_size),
               Block(block_size * 22, HEIGHT - block_size *2, block_size),
               Block(block_size * 22, HEIGHT - block_size *3, block_size),
               Block(block_size * 22, HEIGHT - block_size *4, block_size),

               Block(block_size * 26, HEIGHT - block_size *4, block_size),
               Block(block_size * 26, HEIGHT - block_size *3, block_size),
               Block(block_size * 26, HEIGHT - block_size *2, block_size),
               Block(block_size * 27, HEIGHT - block_size *3, block_size),
               Block(block_size * 27, HEIGHT - block_size *2, block_size),
               Block(block_size * 27, HEIGHT - block_size *2, block_size),
               Block(block_size * 28, HEIGHT - block_size *2, block_size),

               Block4(block_size * 35, HEIGHT - block_size *3, block_size),
               Block4(block_size * 35, HEIGHT - block_size *4, block_size),
               Block4(block_size * 35, HEIGHT - block_size *5, block_size),
               Block4(block_size * 36, HEIGHT - block_size *5, block_size),
               Block4(block_size * 35, HEIGHT - block_size *6, block_size),
               Block4(block_size * 35, HEIGHT - block_size *7, block_size),

               Block4(block_size * 36, HEIGHT - block_size *7, block_size),
               Block4(block_size * 37, HEIGHT - block_size *7, block_size),
               Block4(block_size * 38, HEIGHT - block_size *7, block_size),
               #Block(block_size * 39, HEIGHT - block_size *7, block_size),

               Block4(block_size * 38, HEIGHT - block_size *3, block_size),
               Block4(block_size * 37, HEIGHT - block_size *3, block_size),
               Block4(block_size * 38, HEIGHT - block_size *4, block_size),
               Block4(block_size * 38, HEIGHT - block_size *5, block_size),
               Block4(block_size * 38, HEIGHT - block_size *2, block_size),
               Block4(block_size * 38, HEIGHT - block_size *7, block_size),
               Block4(block_size * 38, HEIGHT - block_size *3, block_size),

               Block4(block_size * 46, HEIGHT - block_size *2, block_size),
               Block4(block_size * 47, HEIGHT - block_size *2, block_size),
               Block4(block_size * 47, HEIGHT - block_size *3, block_size),

               Block4(block_size * 49, HEIGHT - block_size *2, block_size),
               Block4(block_size * 49, HEIGHT - block_size *3, block_size),
               Block4(block_size * 49, HEIGHT - block_size *4, block_size),

               Block4(block_size * 51, HEIGHT - block_size *2, block_size),
               Block4(block_size * 51, HEIGHT - block_size *3, block_size),
               Block4(block_size * 51, HEIGHT - block_size *4, block_size),
               Block4(block_size * 51, HEIGHT - block_size *5, block_size),

               Block4(block_size * 53, HEIGHT - block_size *2, block_size),
               Block4(block_size * 53, HEIGHT - block_size *3, block_size),
               Block4(block_size * 53, HEIGHT - block_size *4, block_size),
               Block4(block_size * 53, HEIGHT - block_size *5, block_size),

               Block4(block_size * 55, HEIGHT - block_size *4, block_size),
               Block4(block_size * 55, HEIGHT - block_size *3, block_size),
               Block4(block_size * 55, HEIGHT - block_size *2, block_size),

               Block3(block_size * 58, HEIGHT - block_size *6, block_size),
               
               Block4(block_size * 61, HEIGHT - block_size *4, block_size),
               Block4(block_size * 61, HEIGHT - block_size *3, block_size),
               Block4(block_size * 61, HEIGHT - block_size *2, block_size),

               Block3(block_size * 66, HEIGHT - block_size *1, block_size),
               Block3(block_size * 66, HEIGHT - block_size *2, block_size),
               
               *fires,*saws,checkpoint]
    start_x = -1343
    num_blocks = 7
    for i in range(2, num_blocks + 2):
        objects.append(Block3(start_x, HEIGHT - block_size * i, block_size))
    offset_x = 0
    scroll_area_width = 200

    # # congrats_font = pygame.font.SysFont('Arial', 36) 
    # # congrats_text_rendered = congrats_font.render('Congratulations!', True, (255, 255, 255)) 
    # if player.rect.colliderect(checkpoint.rect) and not checkpoint_reached:
    #     checkpoint_reached = True  # Set variabel ke True jika pemain mencapai checkpoint
    #     # Jika Anda ingin menampilkan teks 'Congratulations!', Anda bisa memasukkannya di sini
    #     congrats_text_rendered = congrats_font.render('Congratulations!', True, (255, 255, 255))
    #     window.blit(congrats_text_rendered, (WIDTH // 2 - congrats_text_rendered.get_width() // 2, HEIGHT // 2))

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                elif event.key == pygame.K_BACKSPACE:
                    offset_x = reset_game(player)
                    health_bar.current_health = health_bar.max_health
                    initial_offset_x = offset_x

            # Di dalam loop utama Anda, setelah deteksi checkpoint:
        if player.rect.colliderect(checkpoint.rect) and not checkpoint_reached:
            checkpoint_reached = True  # Atur variabel ke True jika pemain mencapai checkpoint
            congrats_font = pygame.font.SysFont('supermario85', 40)
            congrats_text_rendered = congrats_font.render('Congrats!', True, (255, 255, 255))
            window.blit(congrats_text_rendered, (WIDTH // 2 - congrats_text_rendered.get_width() // 2, HEIGHT // 2))
            congrats_sound.play()
            # Reset posisi pemain atau lakukan tindakan lain yang Anda inginkan setelah mencapai checkpoint
            player.rect.x = 100  # Contoh: reset posisi pemain ke 100
            player.rect.y = 100  # Contoh: reset posisi pemain ke 100
            offset_x = 0


        for fire in fires:
            fire.loop()
        
        for saw in saws:
            saw.loop()

        
        checkpoint.loop()
        checkpoint.draw(window, offset_x) 
        
        player.loop(FPS)
        fire.loop()
        saw.loop()
        handle_move(player, objects)

        
        if player.hit:
            player.hit_count += 1
            if player.hit_count > FPS: 
                player.hit = False
                player.hit_count = 0
                health_bar.current_health -= 25 

        if health_bar.current_health <= 0:
            reset_game(player)
            health_bar.current_health = health_bar.max_health
            offset_x = reset_game(player)
        
        draw(window, background, bg_image, player, objects, offset_x)
        health_bar.draw(window)

        # if checkpoint_reached:
        #     window.blit(congrats_text_rendered, (WIDTH // 2 - congrats_text_rendered.get_width() // 2, HEIGHT // 2))


        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
        
        # if player.rect.colliderect(checkpoint.rect) and not checkpoint_reached:
        #     checkpoint_reached = True
        #     # Menampilkan pesan "Congrats"
        #     font = pygame.font.SysFont('Arial', 64)
        #     text = font.render('Congrats!', True, (255, 255, 255))
        #     window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            
            # # Mengatur ulang posisi pemain ke awal
            # player.rect.x = 100
            # player.rect.y = 100
            
            # # Mengatur ulang posisi kamera (jika menggunakan offset)
            # offset_x = 0
        if checkpoint_reached:
            window.blit(congrats_text_rendered, (WIDTH // 2 - congrats_text_rendered.get_width() // 2, HEIGHT // 2))
            reset_game(player)  # Atur ulang pemain ke posisi awal

        pygame.display.update()
        
    pygame.quit()
    quit()

def reset_game(player):
    """Atur ulang posisi pemain ke awal."""
    player.rect.x = 100
    player.rect.y = 100
    return 0

if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Title")
    main(window)
