import pygame
import random
import os

# Initialize pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
GAP_SIZE = 150
PIPE_WIDTH = 80
BIRD_RADIUS = 15
GRAVITY = 0.5
JUMP_STRENGTH = -8
SCROLL_SPEED = 3

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 191, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

class Bird:
    def __init__(self):
        self.x = 100
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.radius = BIRD_RADIUS
        
    def jump(self):
        self.velocity = JUMP_STRENGTH
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Keep bird on screen
        if self.y < self.radius:
            self.y = self.radius
            self.velocity = 0
        if self.y > WINDOW_HEIGHT - self.radius:
            self.y = WINDOW_HEIGHT - self.radius
            self.velocity = 0
            
    def draw(self):
        pygame.draw.circle(screen, RED, (self.x, int(self.y)), self.radius)
        
    def get_mask(self):
        # Simple circle collision mask
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, 350)
        self.top_pipe = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height - GAP_SIZE // 2)
        self.bottom_pipe = pygame.Rect(self.x, self.height + GAP_SIZE // 2, 
                                      PIPE_WIDTH, WINDOW_HEIGHT - (self.height + GAP_SIZE // 2))
        self.passed = False
        
    def update(self):
        self.x -= SCROLL_SPEED
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x
        
    def draw(self):
        pygame.draw.rect(screen, GREEN, self.top_pipe)
        pygame.draw.rect(screen, GREEN, self.bottom_pipe)
        
    def collide(self, bird):
        bird_mask = bird.get_mask()
        return bird_mask.colliderect(self.top_pipe) or bird_mask.colliderect(self.bottom_pipe)

def draw_background():
    screen.fill(BLUE)
    
def draw_ground():
    pygame.draw.rect(screen, (139, 69, 19), (0, WINDOW_HEIGHT - 20, WINDOW_WIDTH, 20))

def main():
    bird = Bird()
    pipes = []
    score = 0
    font = pygame.font.SysFont(None, 36)
    frame_count = 0
    
    running = True
    while running:
        clock.tick(60)  # 60 FPS
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
            if event.type == pygame.MOUSEBUTTONDOWN:
                bird.jump()
                
        # Update
        bird.update()
        
        # Add new pipes
        if frame_count % 100 == 0:  # Every 100 frames
            pipes.append(Pipe(WINDOW_WIDTH))
            
        # Update pipes and remove off-screen pipes
        for pipe in pipes[:]:
            pipe.update()
            if pipe.x + PIPE_WIDTH < 0:
                pipes.remove(pipe)
                
        # Check for collisions
        for pipe in pipes:
            if pipe.collide(bird):
                running = False  # Game over
                
        # Check for scoring
        for pipe in pipes:
            if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                pipe.passed = True
                score += 1
                
        # Check if bird hits the ground or goes above screen
        if bird.y >= WINDOW_HEIGHT - 20 - bird.radius:  # Ground collision
            running = False
            
        # Draw everything
        draw_background()
        for pipe in pipes:
            pipe.draw()
        draw_ground()
        bird.draw()
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        frame_count += 1
        
    pygame.quit()

if __name__ == "__main__":
    main()