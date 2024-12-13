import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
FPS = 30
GRAVITY = 0.4
FLAP_STRENGTH = -7

# colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PIPE_GREEN = (10, 200, 50)

# Player settings
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_colour = GREEN

# Pipe settings
PIPE_WIDTH = 50
PIPE_colour = PIPE_GREEN
PIPE_SPEED = 3
PIPE_GAP = 150
MIN_PIPE_DISTANCE = 200
MAX_PIPE_DISTANCE = 400

# Heal settings
HEAL_RADIUS = 15
HEAL_colour = RED

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Programming Assignment")
clock = pygame.time.Clock()
##########################################################################################################################################################################

# Load all images
BACKGROUND_IMAGE = pygame.image.load(r"c:\Users\adity\Desktop\SYMF\back3.png")
start_screen_pic = pygame.image.load(r"c:\Users\adity\Desktop\SYMF\start screen.png")
restart_game_pic = pygame.image.load(r"c:\Users\adity\Desktop\SYMF\end screen.png")
background_x = 0  # Background scrolling position


# Classes ########################################################################################################
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.colour = (0, 0, 255)
        
    def update(self):
        self.x -= PIPE_SPEED #currently the power up spawn about 1000 pixels away from player and moves towards their direction of travel in then x axis, potential fix set speed to pass and reduce spawn distance
    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), self.radius)
        
class Player:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.colour = PLAYER_colour
        self.velocity = 0
        self.health = 100
        self.has_powerup = False
        self.invincible = False
        self.invincible_timer = 0
        # Load player image
        self.image = pygame.image.load(r'c:\Users\adity\Desktop\SYMF\ship-transformed.png')  # still need to fix this issue
        self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))  # Resize if needed

    def flap(self):
        self.velocity = FLAP_STRENGTH
    
    def activate_powerup(self):
        if self.has_powerup:
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            self.has_powerup =  False
        

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.y < 0 or self.y + self.height > SCREEN_HEIGHT:
            self.health -= 100  # Hitting screen edges reduces health
        
        if self.invincible:
            elapsed_time = pygame.time.get_ticks() - self.invincible_timer
            if elapsed_time > 10000:
                self.invincible = False
                
        if not self.invincible and (self.y < 0 or self.y + self.height > SCREEN_HEIGHT):
            self.health -= 100    

    def draw(self):
        screen.blit(self.image, (self.x, self.y)) 
        #changed the square code ->>> def draw(self): pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.height)) <<<- to my own player pic
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_start = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.width = PIPE_WIDTH
        self.colour = PIPE_colour
        self.coin = Coin(self.x + self.width, self.gap_start + PIPE_GAP // 2)

    def update(self):
        self.x -= PIPE_SPEED
        if self.coin:
            self.coin.update()

    def draw(self):
        pygame.draw.rect(screen, self.colour, (self.x, 0, self.width, self.gap_start)) 
        pygame.draw.rect(screen, self.colour, (self.x, self.gap_start + PIPE_GAP, self.width, SCREEN_HEIGHT))
        if self.coin:
            self.coin.draw()


class Heal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = HEAL_RADIUS
        self.colour = HEAL_colour

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), self.radius)


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
            and player.y < heal.y + heal.radius
        ):
            player.health = min(player.health + 10, 100)
            heals_to_remove.append(heal)

    # Collision with powerups
    for powerup in powerups:
        if (
            player.x + player.width > powerup.x - powerup.radius
            and player.x < powerup.x + powerup.radius
            and player.y + player.height > powerup.y - powerup.radius
            and player.y < powerup.y + powerup.radius
        ):
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

def restart_game():
    player = Player()
    pipes = [Pipe(SCREEN_WIDTH + i * 300) for i in range(3)]
    heals = [heal_spawns(pipes) for _ in range(2)]
    return player, pipes, heals


# Main Game Loop ############################################################################################################################################################################
def main():
    start_screen()  # added a display start screen before starting the game in ordeer to save coding space
    
    player, pipes, heals = restart_game()
    powerups = []
    score = 0
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
            player, pipes, heals = restart_game()

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

        # Health bar
        pygame.draw.rect(screen, RED, (10, 10, player.health * 3, 20))
        pygame.draw.rect(screen, BLACK, (10, 10, 300, 20), 2)

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__=="__main__":
        main()