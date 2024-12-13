import pygame 
import random
import sys

# Initialize Pygame
pygame.init()

# screen dimensions
screen_width = 540
screen_height = 720

# Giving names to the colour codes to help change it easily
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GREEN_PIPE = (10, 200, 50)

# Game settings
FPS = 30
GRAVITY = 0.5
FLAP_STRENGTH = -10

# player settings
player_width = 30
player_height = 30
player_colour = GREEN

# Pipe settings
PIPE_width = 50
PIPE_colour = GREEN_PIPE
PIPE_SPEED = 3
PIPE_GAP = 150
MIN_PIPE_DISTANCE = 200
MAX_PIPE_DISTANCE = 400

# Obstacle settings
OBSTACLE_RADIUS = 15
OBSTACLE_colour = RED

# Initialize screen
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# player class
class Player:
    def __init__(self):
        self.x = 50
        self.y = screen_height // 2
        self.width = player_width
        self.height = player_height
        self.colour = player_colour
        self.velocity = 0
        self.health = 100

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.height))

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_start = random.randint(100, screen_height - PIPE_GAP - 100)
        self.width = PIPE_width
        self.colour = PIPE_colour

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        pygame.draw.rect(screen, self.colour, (self.x, 0, self.width, self.gap_start))
        pygame.draw.rect(screen, self.colour, (self.x, self.gap_start + PIPE_GAP, self.width, screen_height))

# Obstacle class
class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = OBSTACLE_RADIUS
        self.colour = OBSTACLE_colour

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), self.radius)

# Check collision
def check_collision(player, pipes, obstacles):
    pipes_to_remove = []
    obstacles_to_remove = []

    for pipe in pipes:
        if player.x + player.width > pipe.x and player.x < pipe.x + pipe.width:
            if player.y < pipe.gap_start or player.y + player.height > pipe.gap_start + PIPE_GAP:
                player.health -= 25
                pipes_to_remove.append(pipe)

    for obstacle in obstacles:
        if (
            player.x + player.width > obstacle.x - obstacle.radius
            and player.x < obstacle.x + obstacle.radius
            and player.y + player.height > obstacle.y - obstacle.radius
            and player.y < obstacle.y + obstacle.radius
        ):
            player.health += 10
            obstacles_to_remove.append(obstacle)

    for pipe in pipes_to_remove:
        pipes.remove(pipe)

    for obstacle in obstacles_to_remove:
        obstacles.remove(obstacle)

# Restart the game
def restart_game():
    player = Player()
    pipes = [Pipe(screen_width + i * 300) for i in range(3)]
    obstacles = [Obstacle(random.randint(screen_width, screen_width + 600), random.randint(100, screen_height - 100))]
    return player, pipes, obstacles

# Game over screen
def game_over_screen():
    font = pygame.font.Font(None, 32)
    game_over_text = font.render("Game Over", True, BLACK)
    restart_text = font.render("Press SPACE to Restart", True, BLACK)
    screen.fill(WHITE)
    screen.blit(game_over_text, ((screen_width - game_over_text.get_width()) // 2, screen_height // 3))
    screen.blit(restart_text, ((screen_width - restart_text.get_width()) // 2, screen_height // 2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

# Main game function
def main():
    player, pipes, obstacles = restart_game()
    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.flap()

        player.update()

        # Updates the pipes and spawn new ones
        for pipe in pipes[:]:
            pipe.update()
            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)

            if len(pipes) < 3:
                rightmost_pipe_x = max((pipe.x for pipe in pipes), default=screen_width)
                new_x = rightmost_pipe_x + random.randint(MIN_PIPE_DISTANCE, MAX_PIPE_DISTANCE)
                if new_x < screen_width:
                    new_x = screen_width + MIN_PIPE_DISTANCE
                pipes.append(Pipe(new_x))

        # Update obstacles
        for obstacle in obstacles:
            obstacle.update()
        if len(obstacles) < 1:
            obstacles.append(Obstacle(screen_width + random.randint(200, 400), random.randint(100, screen_height - 100)))

        # Check collisions
        check_collision(player, pipes, obstacles)

        # Check for game over
        if player.health <= 0:
            game_over_screen()
            player, pipes, obstacles = restart_game()

        # Draw everything
        player.draw()
        for pipe in pipes:
            pipe.draw()
        for obstacle in obstacles:
            obstacle.draw()

        # Draw health bar
        pygame.draw.rect(screen, RED, (10, 10, player.health * 3, 20))
        pygame.draw.rect(screen, BLACK, (10, 10, 300, 20), 2)

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
