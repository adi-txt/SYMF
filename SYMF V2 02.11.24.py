import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# screen dimensions and settings
screen_width = 900
screen_height = 720
FPS = 30
GRAVITY = 0.5
FLAP_STRENGTH = -10

# colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
pipe_GREEN = (10, 200, 50)

# Player settings
PLAYER_width = 30
PLAYER_height = 30
PLAYER_colour = GREEN

# pipe settings
pipe_width = 50
pipe_colour = pipe_GREEN
pipe_speed = 3
pipe_gap = 150
MIN_pipe_DISTANCE = 200
MAX_pipe_DISTANCE = 400

# Heal settings
HEAL_RADIUS = 15
HEAL_colour = RED

# Initialize screen and clock
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Programming Assignment")
clock = pygame.time.Clock()

# Load background image
BACKGROUND_IMAGE = pygame.image.load(r'c:\Users\adity\Desktop\SYMF\back3.png')
background_x = 0  # Background scrolling position


# Classes ########################################################################################################
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.colour = (0, 0, 255)
        
    def update(self):
        self.x -= pipe_speed #currently the power up spawn about 1000 pixels away from player and moves towards their direction of travel in then x axis, potential fix set speed to pass and reduce spawn distance
    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), self.radius)
        
class Player:
    def __init__(self):
        self.x = 50
        self.y = screen_height // 2
        self.width = PLAYER_width
        self.height = PLAYER_height
        self.colour = PLAYER_colour
        self.velocity = 0
        self.health = 100
        self.has_powerup = False
        self.invincible = False
        self.invincible_timer = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH
    
    def activate_powerup(self):
        if self.has_powerup:
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            self.has_powerup = False
        

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.y < 0 or self.y + self.height > screen_height:
            self.health -= 100  # Hitting screen edges reduces health
        
        if self.invincible:
            elapsed_time = pygame.time.get_ticks() - self.invincible_timer
            if elapsed_time > 10000:
                self.invincible = False
                
        if not self.invincible and (self.y < 0 or self.y + self.height > screen_height):
            self.health -= 100    

        
    def draw(self):
        pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.height))


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_start = random.randint(100, screen_height - pipe_gap - 100)
        self.width = pipe_width
        self.colour = pipe_colour
        self.coin = Coin(self.x + self.width, self.gap_start + pipe_gap // 2)

    def update(self):
        self.x -= pipe_speed
        if self.coin:
            self.coin.update()

    def draw(self):
        pygame.draw.rect(screen, self.colour, (self.x, 0, self.width, self.gap_start))
        pygame.draw.rect(screen, self.colour, (self.x, self.gap_start + pipe_gap, self.width, screen_height))
        if self.coin:
            self.coin.draw()


class Heal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = HEAL_RADIUS
        self.colour = HEAL_colour

    def update(self):
        self.x -= pipe_speed

    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), self.radius)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.colour = (255, 215, 0)

    def update(self):
        self.x -= pipe_speed

    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), self.radius)


# Core Functions ################################################################################################

def check_collision(player, pipes, heals, powerups, score):
    pipes_to_remove = []
    heals_to_remove = []
    powerups_to_remove = []

    for pipe in pipes:
        # Collision with pipes
        if not player.invincible:
            if player.x + player.width > pipe.x and player.x < pipe.x + pipe.width:
                if player.y < pipe.gap_start or player.y + player.height > pipe.gap_start + pipe_gap:
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
    min_x = screen_width
    max_x = screen_width + 600
    min_y = 50
    max_y = screen_height - 50
    buffer = 10

    while True:
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        overlap = False

        for pipe in pipes:
            if pipe.x < x < pipe.x + pipe.width:
                if pipe.gap_start + buffer < y < pipe.gap_start + pipe_gap - buffer:
                    overlap = True
                    break

        if not overlap:
            return Heal(x, y)
        
def spawn_powerups():
    x = random.randint(screen_width, screen_width + 300)
    y = random.randint(50, screen_height - 50)
    
    return PowerUp(x, y)


def game_over_screen():
    font = pygame.font.Font(None, 32)
    game_over_text = font.render("Game Over", True, BLACK)
    restart_text = font.render("Press SPACE to Restart", True, BLACK)
    screen.fill(WHITE)
    screen.blit(game_over_text, ((screen_width - game_over_text.get_width()) // 2, screen_height // 3))
    screen.blit(restart_text, ((screen_width - restart_text.get_width()) // 2, screen_height // 2))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


def restart_game():
    player = Player()
    pipes = [Pipe(screen_width + i * 300) for i in range(3)]
    heals = [heal_spawns(pipes) for _ in range(2)]
    return player, pipes, heals


# Main Game Loop ################################################################################################
def main():
    player, pipes, heals = restart_game()
    powerups = []
    score = 0
    global background_x

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

        # Entity spawns
        if len(pipes) < 3:
            new_x = max(pipe.x for pipe in pipes) + random.randint(MIN_pipe_DISTANCE, MAX_pipe_DISTANCE)
            pipes.append(Pipe(new_x))
        if len(heals) < 2:
            heals.append(heal_spawns(pipes))
        if len(powerups) < 1 and random.random() < 0.01:
            powerups.append(spawn_powerups())

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
        screen.blit(score_text, (screen_width - score_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(FPS)

if __name__=="__main__":
        main()