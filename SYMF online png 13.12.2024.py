import pygame
import sys
import random
import time
import requests
from io import BytesIO

def load_image(url, width, height):
    response = requests.get(url)
    response.raise_for_status()
    image = pygame.image.load(BytesIO(response.content))
    image = pygame.transform.scale(image, (width, height)) 
    return image


pygame.init()

# Screen dimensions and settings
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
FPS = 30
GRAVITY = 0.4
FLAP_STRENGTH = -7

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PIPE_GREEN = (10, 200, 50)

# Player settings
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_COLOUR = GREEN

# Pipe settings
PIPE_WIDTH = 50

PIPE_SPEED = 3
PIPE_GAP = 160
MIN_PIPE_DISTANCE = 200
MAX_PIPE_DISTANCE = 400

# Load images
TOP_PIPE_IMAGE = load_image("https://github.com/adi-txt/SYMF/blob/main/SYMF/pipe/topipe1.png?raw=true", SCREEN_WIDTH, SCREEN_HEIGHT)
BOTTOM_PIPE_IMAGE = load_image("https://github.com/adi-txt/SYMF/blob/main/SYMF/pipe/bopipe1.png?raw=true", SCREEN_WIDTH, SCREEN_HEIGHT)
HEAL_IMAGE = load_image("https://github.com/adi-txt/SYMF/blob/main/SYMF/entities/health.png?raw=true", 45, 45)
powerup_image = load_image("https://github.com/adi-txt/SYMF/blob/main/SYMF/entities/shield2.png?raw=true", 65, 65)

# Scale the images if needed
TOP_PIPE_IMAGE = pygame.transform.scale(TOP_PIPE_IMAGE, (PIPE_WIDTH, 550))
BOTTOM_PIPE_IMAGE = pygame.transform.scale(BOTTOM_PIPE_IMAGE, (PIPE_WIDTH, 550))



# Heal settings
HEAL_RADIUS = 15
HEAL_COLOuR = RED

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
##########################################################################################################################################################################

# Load all images
BACKGROUND_IMAGE = load_image("https://github.com/adi-txt/SYMF/blob/main/SYMF/back3.png?raw=true", SCREEN_WIDTH, SCREEN_HEIGHT)
start_screen_pic = load_image("https://github.com/adi-txt/SYMF/blob/main/SYMF/start%20screen.png?raw=true", SCREEN_WIDTH, SCREEN_HEIGHT)
restart_game_pic = load_image("https://github.com/adi-txt/SYMF/blob/main/SYMF/end%20screen.png?raw=true", SCREEN_WIDTH, SCREEN_HEIGHT)
background_x = 0  # Background scrolling position


# Classes ########################################################################################################

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40  # Width of the powerup image
        self.height = 40  # Height of the powerup image
        self.image = powerup_image  # Loaded PNG image

    def update(self):
        self.x -= PIPE_SPEED #currently the power up spawn about 1000 pixels away from player and moves towards their direction of travel in then x axis, potential fix set speed to pass and reduce spawn distance

    def draw(self):
        screen.blit(self.image, (self.x, self.y)) 
        
class Player:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.colour = PLAYER_COLOUR
        self.velocity = 0
        self.health = 100
        self.has_powerup = False
        self.invincible = False
        self.invincible_timer = 0
        self.powerup_timer_duration = 10  # Duration in seconds
        self.powerup_timer_start = None  # Track when powerup starts
        # Load player image
        self.image = load_image("https://github.com/adi-txt/SYMF/blob/main/SYMF/ship-transformed.png?raw=true", PLAYER_WIDTH, PLAYER_HEIGHT)  # still need to fix this issue
        self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))  # Resize if needed

    def flap(self):
        self.velocity = FLAP_STRENGTH
    
    def activate_powerup(self):
        if self.has_powerup:
            self.invincible = True
            self.powerup_timer_start = pygame.time.get_ticks()  # Start the timer as soon as I activate the powerup
            self.has_powerup = False
            
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.y < 0 or self.y + self.height > SCREEN_HEIGHT:
            self.health -= 100  # Hitting screen edges reduces health to 0, = death

        if self.invincible:
            elapsed_time = (pygame.time.get_ticks() - self.powerup_timer_start) / 1000  # pygame.time.get_ticks() = when the power was activated -
            if elapsed_time > self.powerup_timer_duration:
                self.invincible = False  # Ends invincibility
                self.powerup_timer_start = None

        if not self.invincible and (self.y < 0 or self.y + self.height > SCREEN_HEIGHT):
            self.health -= 100


    def draw(self):
        screen.blit(self.image, (self.x, self.y)) 
        #changed the square player code ->>> def draw(self): pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.height)) <<<- to my own player pic
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_start = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.width = PIPE_WIDTH
        self.coin = Coin(self.x + self.width, self.gap_start + PIPE_GAP // 2)

    def update(self):
        self.x -= PIPE_SPEED
        if self.coin:
            self.coin.update()

    def draw(self):
        # adding the top pipe
        top_pipe_rect = TOP_PIPE_IMAGE.get_rect(bottomleft=(self.x, self.gap_start))
        screen.blit(TOP_PIPE_IMAGE, top_pipe_rect)

        # adding the bottom pipe
        bottom_pipe_rect = BOTTOM_PIPE_IMAGE.get_rect(topleft=(self.x, self.gap_start + PIPE_GAP))
        screen.blit(BOTTOM_PIPE_IMAGE, bottom_pipe_rect)

class Heal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = HEAL_RADIUS
        self.colour = HEAL_COLOuR

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        screen.blit(HEAL_IMAGE, (self.x - self.radius, self.y - self.radius)) #changed from pygame.draw.circle(screen, self.colour, (self.x, self.y), self.radius)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.colour = (255, 215, 0)

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), self.radius)

# Core Functions ################################################################################################

def start_screen():
    while True:
        # Draw the start screen image
        screen.blit(start_screen_pic, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_9:
                return 
            
def check_collision(player, pipes, heals, powerups, score):
    pipes_to_remove = []
    heals_to_remove = []
    powerups_to_remove = []

    for pipe in pipes:
        # Collision with pipes
        if not player.invincible:
            if player.x + player.width > pipe.x and player.x < pipe.x + pipe.width:
                if player.y < pipe.gap_start or player.y + player.height > pipe.gap_start + PIPE_GAP:
                    player.health -= 25
                    pipes_to_remove.append(pipe)

 # Collision with coins
        if pipe.coin:
            if (
                player.x + player.width > pipe.coin.x - pipe.coin.radius
                and player.x < pipe.coin.x + pipe.coin.radius
                and player.y + player.height > pipe.coin.y - pipe.coin.radius
                and player.y < pipe.coin.y + pipe.coin.radius
            ):
                score += 1
                pipe.coin = None  # Remove the coin from the pipe.

    # Collision with heals
    for heal in heals:
        if (
            player.x + player.width > heal.x - heal.radius
            and player.x < heal.x + heal.radius
            and player.y + player.height > heal.y - heal.radius
            and player.y < heal.y + heal.radius):
            player.health = min(player.health + 10, 100)
            heals_to_remove.append(heal)

    # Collision with powerups
        for powerup in powerups:
            if (
        player.x + player.width > powerup.x
        and player.x < powerup.x + powerup.width
        and player.y + player.height > powerup.y
        and player.y < powerup.y + powerup.height):
                if not player.has_powerup:
                    player.has_powerup = True
                    powerups_to_remove.append(powerup) 



    # Remove collided items
    for item in pipes_to_remove:
        pipes.remove(item)
    for item in heals_to_remove:
        heals.remove(item)
    for item in powerups_to_remove:
        powerups.remove(item)

    return score

def heal_spawns(pipes):
    min_x = SCREEN_WIDTH
    max_x = SCREEN_WIDTH + 600
    min_y = 50
    max_y = SCREEN_HEIGHT - 50
    buffer = 10

    while True:
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        overlap = False

        for pipe in pipes:
            if pipe.x < x < pipe.x + pipe.width:
                if pipe.gap_start + buffer < y < pipe.gap_start + PIPE_GAP - buffer:
                    overlap = True
                    break

        if not overlap:
            return Heal(x, y)
        
def spawn_powerups():
    x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 300)
    y = random.randint(50, SCREEN_HEIGHT - 50)
    
    return PowerUp(x, y)

def draw_timer(player):
    if player.invincible:
        elapsed_time = (pygame.time.get_ticks() - player.powerup_timer_start) / 1000
        remaining_time = max(0, player.powerup_timer_duration - elapsed_time)
        
        font = pygame.font.Font(None, 60)
        timer_text = font.render(f"Power-Up: {remaining_time:.1f}s", True, BLACK)
        screen.blit(timer_text, (420, 50))  # Position of the timer 

def game_over_screen():
    screen.blit(restart_game_pic, (0, 0))
    pygame.display.flip()
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()


def restart_game():
    player = Player()
    pipes = [Pipe(SCREEN_WIDTH + i * 300) for i in range(3)]
    heals = [heal_spawns(pipes) for _ in range(2)]
    score = 0  # Reset the score to 0 when restarting <--------------------
    return player, pipes, heals, score 

# Main Game Loop ################################################################################################
def main():
    start_screen()  # Show start screen before starting the game

    player, pipes, heals, score = restart_game()  # Unpack the score as well
    powerups = []
    global background_x

    last_powerup_spawn = pygame.time.get_ticks()
    while True:
        background_x -= 2
        if background_x <= -1080:
            background_x = 0

        # Draw background
        screen.blit(BACKGROUND_IMAGE, (background_x, 0))
        screen.blit(BACKGROUND_IMAGE, (background_x + 1080, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.flap()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                player.activate_powerup()

        # Update player and entities
        player.update()
        score = check_collision(player, pipes, heals, powerups, score)

        if player.health <= 0:
            game_over_screen()
            player, pipes, heals, score = restart_game()  # Reset the score on game over

        # Entity spawns
        if len(pipes):
            new_x = max(pipe.x for pipe in pipes) + random.randint(MIN_PIPE_DISTANCE, MAX_PIPE_DISTANCE)
            pipes.append(Pipe(new_x))
        if len(heals) < 2:
            heals.append(heal_spawns(pipes))
        if len(powerups) < 1 and random.random() < 100:
            powerups.append(spawn_powerups())

        current_time = pygame.time.get_ticks()
        if current_time - last_powerup_spawn >= 10000:  # 10 seconds
            powerups.append(spawn_powerups())
            last_powerup_spawn = current_time  # Reset the spawn timer

        # Draw entities
        player.draw()
        for pipe in pipes:
            pipe.update()
            pipe.draw()
        for heal in heals:
            heal.update()
            heal.draw()
        for powerup in powerups:
            powerup.update()
            powerup.draw()

        # Draw timer
        draw_timer(player)

        # Health bar
        pygame.draw.rect(screen, RED, (10, 10, player.health * 3, 20))
        pygame.draw.rect(screen, BLACK, (10, 10, 300, 20), 2)

        # Display score
        font = pygame.font.Font(None, 39)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(FPS)

if __name__=="__main__":
        main()