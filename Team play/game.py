from main import *
from map import *
from os import listdir
from os.path import join
import settings as set
from os.path import isfile

game.CURRENT_LEVEL = 0

pygame.init()
pygame.display.set_caption("Platformer")
clock = pygame.time.Clock()
window = pygame.display.set_mode((set.WIDTH, set.HEIGHT))

collide_left = False
collide_right = False

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

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        if self.name == "HealthBar":
            win.blit(self.image, (self.rect.x, self.rect.y))
        else:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class Block(Object):

    def get_block(self, size):
        path = join("assets", "Terrain", "Terrain.png")
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)

        if game.CURRENT_LEVEL <= 3:
            rect = pygame.Rect(96, 0, size, size)
        if game.CURRENT_LEVEL > 3 and game.CURRENT_LEVEL < 7:
            rect = pygame.Rect(96, 64, size, size)
        if game.CURRENT_LEVEL > 6:
            rect = pygame.Rect(96, 128, size, size)

        surface.blit(image, (0, 0), rect)
        return pygame.transform.scale2x(surface)

    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = self.get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class HealthBar(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        path = join("assets", "MainCharacters", "health_4.png")
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, width, height)
        surface.blit(image, (0, 0), rect)
        self.image = image
        self.name = "HealthBar"
        self.image.blit(surface, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Finish(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)

        path = join("assets", "Items", "Checkpoints", "End", "End (Idle).png")
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        rect = pygame.Rect(0, 0, size, size)
        surface.blit(image, (0, 0), rect)

        self.name = "finish"
        self.image.blit(surface, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Saw(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Saw")
        self.Saw = load_sprite_sheets("Traps", "Saw", width, height)
        self.image = self.Saw["on"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"
        self.name = "saw"

    def loop(self):
        sprites = self.Saw[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"

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
        self.current_character = "MaskDude"
        self.health = 4

    def jump(self):
        keys = pygame.key.get_pressed()

        if self.current_character == "MaskDude":

            if keys[pygame.K_a]:
                self.x_vel = -300
            elif keys[pygame.K_d]:
                self.x_vel = 300
        else:
            self.y_vel = - 1 * 8
            self.animation_count = 0
            self.jump_count += 1
            if self.jump_count == 1:
                if self.current_character == "VirtualGuy":
                    pygame.mixer.Channel(4).play(pygame.mixer.Sound(r'assets\Music\rocket.mp3'))
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

    def loop(self, fps, CharHealthBar):

        if self.health > 0:
            path = join("assets", "MainCharacters", f"health_{self.health}.png")
            image = pygame.image.load(path).convert_alpha()
            CharHealthBar.image = image


        if self.health <= 0:
            pygame.mixer.Channel(1).pause()
            pygame.mixer.Channel(0).play(pygame.mixer.Sound('assets\Menu\menu.mp3'))
            levels_menu()

        keys = pygame.key.get_pressed()

        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)

        if self.current_character == "NinjaFrog" and (keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]) \
                and (game.collide_left or game.collide_right):
            self.y_vel = -2

        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.health -= 1
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

    def change_charecter(self, choice):
        self.SPRITES = load_sprite_sheets("MainCharacters", set.MainCharacters[choice - 1], 32, 32, True)
        self.current_character = set.MainCharacters[choice - 1]
        if choice == 3: # VirtualGuy
            self.GRAVITY = 0.3
        else:
            self.GRAVITY = 1

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

def get_background():

    if game.CURRENT_LEVEL <= 3:
        name = "blue sky.png"
    if game.CURRENT_LEVEL > 3 and game.CURRENT_LEVEL < 7:
        name = "pink sky.png"
    if game.CURRENT_LEVEL > 6:
        name = "dusk.sky.png"

    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(set.WIDTH // width + 1):
        for j in range(set.HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x, offset_y):

    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x, offset_y)
        if obj.name == "fire" or obj.name == "saw":
            obj.loop()

    player.draw(window, offset_x, offset_y)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if obj.name == "HealthBar":
                continue
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
        if pygame.sprite.collide_mask(player, obj) and obj.name != "HealthBar":
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    game.collide_left = collide(player, objects, -set.PLAYER_VEL * 2)
    game.collide_right = collide(player, objects, set.PLAYER_VEL * 2)

    if keys[pygame.K_a] and not game.collide_left:
        player.move_left(set.PLAYER_VEL)
    if keys[pygame.K_d] and not game.collide_right:
        player.move_right(set.PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [game.collide_left, game.collide_right, *vertical_collide]

    for obj in to_check:
        if obj and (obj.name == "fire" or obj.name == "saw"):
            player.make_hit()
            pygame.mixer.music.load('assets\Music\8-bit-punch.wav')
            pygame.mixer.music.play()
        if obj and obj.name == "finish":

            if game.CURRENT_LEVEL == set.CURRENT_MAX_LEVEL:
                set.CURRENT_MAX_LEVEL += 1
                with open('saving.txt', 'w') as f:
                    f.write(str(game.CURRENT_LEVEL + 1 if game.CURRENT_LEVEL + 1 <= set.LEVELS else set.LEVELS))
            pygame.mixer.Channel(1).pause()
            pygame.mixer.Channel(0).play(pygame.mixer.Sound('assets\Menu\menu.mp3'))
            levels_menu()

def play():

    pygame.mixer.Channel(1).play(pygame.mixer.Sound('assets\Music\level 1 theme.mp3'))

    background, bg_image = get_background()

    player = Player(100, 100, 50, 50)

    CharHealthBar = HealthBar(0, 0, 300, 40)

    floor = []
    floor.append(CharHealthBar)
    for idx_y, row in enumerate(maps[game.CURRENT_LEVEL - 1]):
        for idx_x, block in enumerate(row):
            if block == 1:
                floor.append(Block(idx_x * set.BLOCK_SIZE, set.HEIGHT - idx_y * set.BLOCK_SIZE, set.BLOCK_SIZE))
            if block == 9:
                floor.append(Finish(idx_x * set.BLOCK_SIZE, set.HEIGHT - idx_y * set.BLOCK_SIZE, 64))
            if block == 2:
                fire = Fire(idx_x * set.BLOCK_SIZE + randrange(0, 48), set.HEIGHT - idx_y * set.BLOCK_SIZE + 32, 16, 48)
                floor.append(fire)
            if block == 3:
                saw = Saw(idx_x * set.BLOCK_SIZE, set.HEIGHT - idx_y * set.BLOCK_SIZE + 32, 38, 304)
                floor.append(saw)



    objects = [*floor,Block(0, set.HEIGHT - set.BLOCK_SIZE * 2, set.BLOCK_SIZE),
               Block(set.BLOCK_SIZE * 3, set.HEIGHT - set.BLOCK_SIZE * 4, set.BLOCK_SIZE), Block(set.BLOCK_SIZE * 5, set.HEIGHT - set.BLOCK_SIZE * 6, set.BLOCK_SIZE), CharHealthBar]

    offset_x = 0
    offset_y = 0


    run = True
    while run:

        clock.tick(set.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.Channel(1).pause()
                    pygame.mixer.Channel(0).play(pygame.mixer.Sound('assets\Menu\menu.mp3'))
                    levels_menu()
                if event.key == pygame.K_1:
                    player.change_charecter(1)
                if event.key == pygame.K_2:
                    player.change_charecter(2)
                if event.key == pygame.K_3:
                    player.change_charecter(3)

        player.loop(set.FPS, CharHealthBar)
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x, offset_y)

        if ((player.rect.right - offset_x >= set.WIDTH - set.SCROLL_AREA_WIDTH) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= set.SCROLL_AREA_WIDTH) and player.x_vel < 0):
            offset_x += player.x_vel
        if (((player.rect.centery - offset_y >= (set.HEIGHT - set.SCROLL_AREA_HEIGHT)) and player.y_vel > 0) or \
                ((player.rect.centery - offset_y <= set.SCROLL_AREA_HEIGHT) and player.y_vel < 0)) and player.rect.bottom < (set.HEIGHT - set.BLOCK_SIZE * 3):
            offset_y += player.y_vel

    pygame.quit()
    quit()