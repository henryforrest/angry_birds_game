import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Angry Birds - Python Edition")

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
BLUE = (50, 50, 255)
BROWN = (139, 69, 19)
GREY = (100, 100, 100)

# Clock
clock = pygame.time.Clock()

# Gravity
gravity = 0.5

# Fonts
font = pygame.font.SysFont(None, 48)

# Projectile class
class Projectile:
    def __init__(self, x, y, radius=15):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.radius = radius
        self.color = RED
        self.vel_x = 0
        self.vel_y = 0
        self.launched = False

    def launch(self, power, angle):
        self.vel_x = math.cos(angle) * power
        self.vel_y = math.sin(angle) * power
        self.launched = True

    def move(self):
        if self.launched:
            self.vel_y += gravity
            self.x += self.vel_x
            self.y += self.vel_y
        if self.y + self.radius > HEIGHT - 50:  # 50 is ground height
            self.y = HEIGHT - 50 - self.radius
            self.vel_y *= -0.7  # Reverse Y velocity and lose some energy
            self.vel_x *= 0.8  # Reduce horizontal speed too
        # Roll along the ground if almost no vertical movement
        if abs(self.vel_y) < 1 and self.y + self.radius >= HEIGHT - 50:
            self.vel_y = 0
            # Apply friction to horizontal velocity
            if self.vel_x > 0:
                self.vel_x -= 0.2
                if self.vel_x < 0:
                    self.vel_x = 0
            elif self.vel_x < 0:
                self.vel_x += 0.2
                if self.vel_x > 0:
                    self.vel_x = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.vel_x = 0
        self.vel_y = 0
        self.launched = False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

# Block/Target Physics Object
class PhysicsObject:
    def __init__(self, x, y, width, height, color, movable=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.movable = movable
        self.hit = False
        self.scored = False

    def update(self, objects):
        if self.movable:
            self.vel_y += gravity
            self.rect.x += int(self.vel_x)
            self.rect.y += int(self.vel_y)

            # Collisions with other objects
            for obj in objects:
                if obj is not self and self.rect.colliderect(obj.rect):
                    if self.vel_y > 0:
                        self.rect.bottom = obj.rect.top
                        self.vel_y = 0
                    if self.vel_x != 0:
                        self.vel_x *= 0.5  # slow sideways motion

            # Hit ground
            if self.rect.bottom > HEIGHT - 50:
                self.rect.bottom = HEIGHT - 50
                self.vel_y = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# Button class
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GREY
        self.text = text
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        txt = self.font.render(self.text, True, BLACK)
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Level Data
levels = [
    {
        "blocks": [
            (700, HEIGHT - 70, 60, 20),
            (770, HEIGHT - 70, 60, 20),
            (735, HEIGHT - 90, 60, 20),
        ],
        "targets": [
            (710, HEIGHT - 110, 40, 40),
            (780, HEIGHT - 110, 40, 40),
        ]
    },
    {
        "blocks": [
            (600, HEIGHT - 70, 60, 20),
            (660, HEIGHT - 100, 60, 20),
            (720, HEIGHT - 130, 60, 20),
        ],
        "targets": [
            (630, HEIGHT - 170, 40, 40),
            (690, HEIGHT - 200, 40, 40),
        ]
    }
]

current_level = 0

# Create objects for a level
def load_level(level_data):
    blocks = [PhysicsObject(x, y, w, h, BROWN, movable=True) for (x, y, w, h) in level_data["blocks"]]
    targets = [PhysicsObject(x, y, w, h, BLUE, movable=True) for (x, y, w, h) in level_data["targets"]]
    return blocks, targets

# Home screen
def home_screen():
    while True:
        screen.fill(WHITE)
        title = font.render("Angry Birds - Python Edition", True, BLACK)
        start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60, "Start Game")
        start_button.draw(screen)
        screen.blit(title, (WIDTH//2 - 250, 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(pygame.mouse.get_pos()):
                    return

        pygame.display.flip()
        clock.tick(60)

# Main Game
def main_game():
    global current_level
    projectile = Projectile(150, HEIGHT - 100)
    blocks, targets = load_level(levels[current_level])
    reset_button = Button(50, 30, 100, 40, "Reset")
    next_button = Button(WIDTH - 150, 30, 100, 40, "Next")

    score = 0
    start_pos = None
    end_pos = None
    used_throw = False

    while True:
        screen.fill(WHITE)

        # Draw ground
        pygame.draw.rect(screen, GREEN, (0, HEIGHT-50, WIDTH, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button.is_clicked(pygame.mouse.get_pos()):
                    projectile.reset()
                    blocks, targets = load_level(levels[current_level])
                    score = 0
                    used_throw = False
                elif next_button.is_clicked(pygame.mouse.get_pos()):
                    current_level = (current_level + 1) % len(levels)
                    blocks, targets = load_level(levels[current_level])
                    projectile.reset()
                    score = 0
                    used_throw = False
                elif not projectile.launched:
                    start_pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP:
                if start_pos and not used_throw:
                    end_pos = pygame.mouse.get_pos()
                    dx = start_pos[0] - end_pos[0]
                    dy = start_pos[1] - end_pos[1]
                    angle = math.atan2(dy, dx)
                    power = math.hypot(dx, dy) * 0.2
                    projectile.launch(power, angle)
                    used_throw = True
                    start_pos = None
                    end_pos = None

        # Aiming line
        if start_pos:
            current_pos = pygame.mouse.get_pos()
            pygame.draw.line(screen, BLACK, start_pos, current_pos, 3)

        projectile.move()

        all_objects = blocks + targets

        # Physics updates
        for obj in all_objects:
            obj.update(all_objects)

        # Check for collisions
        for obj in all_objects:
            if projectile.get_rect().colliderect(obj.rect):
                if not obj.hit:
                    obj.hit = True
                    obj.vel_x += projectile.vel_x * 0.2
                    obj.vel_y += projectile.vel_y * 0.2
                    if not obj.scored and obj.color == BLUE:  # Only score targets
                        score += 10
                        obj.scored = True

        # Draw blocks and targets
        for obj in all_objects:
            obj.draw(screen)

        projectile.draw(screen)
        reset_button.draw(screen)
        next_button.draw(screen)

        # Score Display
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (WIDTH - 350, 30))

        # Level Complete check
        targets_down = all(t.rect.bottom >= HEIGHT-50 and abs(t.vel_y) < 1 for t in targets)
        if targets_down:
            complete_text = font.render("Level Complete!", True, BLACK)
            screen.blit(complete_text, (WIDTH//2 - 150, HEIGHT//2 - 50))

        pygame.display.flip()
        clock.tick(60)

# Run
home_screen()
main_game()
