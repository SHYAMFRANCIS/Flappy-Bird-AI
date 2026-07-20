import pygame
import neat
import random
import os

pygame.init()

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800
GAP_SIZE = 150
PIPE_WIDTH = 80
BIRD_RADIUS = 15
GRAVITY = 0.5
JUMP_STRENGTH = -8
SCROLL_SPEED = 4
PIPE_SPAWN_INTERVAL = 100
GROUND_HEIGHT = 100

WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("NEAT Flappy Bird")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 24)

generation = 0
best_score = 0


class Bird:
    def __init__(self):
        self.x = 100
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.radius = BIRD_RADIUS

        self.surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, RED, (self.radius, self.radius), self.radius)
        self.mask = pygame.mask.from_surface(self.surface)

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        screen.blit(self.surface, (self.x - self.radius, int(self.y) - self.radius))


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap = GAP_SIZE
        self.height = random.randint(200, 600)
        self.passed = False

        self.top_height = self.height - self.gap // 2
        self.bottom_y = self.height + self.gap // 2
        self.bottom_height = WINDOW_HEIGHT - GROUND_HEIGHT - self.bottom_y

        self.top_surface = pygame.Surface((PIPE_WIDTH, self.top_height))
        self.top_surface.fill(GREEN)
        self.top_mask = pygame.mask.from_surface(self.top_surface)

        self.bottom_surface = pygame.Surface((PIPE_WIDTH, self.bottom_height))
        self.bottom_surface.fill(GREEN)
        self.bottom_mask = pygame.mask.from_surface(self.bottom_surface)

    def update(self):
        self.x -= SCROLL_SPEED

    def draw(self):
        screen.blit(self.top_surface, (int(self.x), 0))
        screen.blit(self.bottom_surface, (int(self.x), self.bottom_y))

    def offscreen(self):
        return self.x + PIPE_WIDTH < 0

    def collide(self, bird):
        if bird.x + bird.radius < self.x or bird.x - bird.radius > self.x + PIPE_WIDTH:
            return False

        bx = bird.x - bird.radius
        by = bird.y - bird.radius

        offset_x = int(self.x - bx)
        offset_y_top = int(0 - by)
        if bird.mask.overlap(self.top_mask, (offset_x, offset_y_top)):
            return True

        offset_y_bottom = int(self.bottom_y - by)
        if bird.mask.overlap(self.bottom_mask, (offset_x, offset_y_bottom)):
            return True

        return False


def draw_background():
    screen.fill(BLUE)
    pygame.draw.rect(screen, BROWN, (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, GROUND_HEIGHT))
    pygame.draw.rect(screen, BLACK, (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, 2))


def eval_genomes(genomes, config):
    global generation, best_score
    generation += 1

    nets = []
    birds = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird())
        ge.append(genome)

    pipes = [Pipe(WINDOW_WIDTH + 200)]
    score = 0
    frame_count = 0

    while len(birds) > 0:
        clock.tick(60)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pipe_ind = 0
        if len(pipes) > 1 and birds:
            if pipes[0].x + PIPE_WIDTH < birds[0].x:
                pipe_ind = 1
        if pipe_ind >= len(pipes):
            pipe_ind = 0

        for i, bird in enumerate(birds):
            bird.update()
            ge[i].fitness += 0.1

            if len(pipes) > 0:
                pipe = pipes[pipe_ind]
                output = nets[i].activate((
                    bird.y / WINDOW_HEIGHT,
                    bird.velocity / 10,
                    (pipe.x + PIPE_WIDTH - bird.x) / WINDOW_WIDTH,
                    bird.y - (pipe.height - pipe.gap / 2),
                    bird.y - (pipe.height + pipe.gap / 2),
                ))

                if output[0] > 0.5:
                    bird.jump()

        if frame_count % PIPE_SPAWN_INTERVAL == 0:
            pipe_x = WINDOW_WIDTH
            pipes.append(Pipe(pipe_x))

        for pipe in pipes[:]:
            pipe.update()
            if pipe.offscreen():
                pipes.remove(pipe)

        for pipe in pipes:
            if not pipe.passed and pipe.x + PIPE_WIDTH < birds[0].x:
                pipe.passed = True
                score += 1
                for g in ge:
                    g.fitness += 5

        for i in range(len(birds) - 1, -1, -1):
            bird = birds[i]

            if bird.y + bird.radius >= WINDOW_HEIGHT - GROUND_HEIGHT or bird.y - bird.radius <= 0:
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)
                continue

            for pipe in pipes:
                if pipe.collide(bird):
                    birds.pop(i)
                    nets.pop(i)
                    ge.pop(i)
                    break

        draw_background()
        for pipe in pipes:
            pipe.draw()
        for bird in birds:
            bird.draw()

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        gen_text = font.render(f"Generation: {generation} | Alive: {len(birds)}", True, WHITE)
        screen.blit(gen_text, (10, 40))
        best_text = font.render(f"Best Score: {best_score}", True, WHITE)
        screen.blit(best_text, (10, 70))

        pygame.display.update()

    if score > best_score:
        best_score = score

    print(f"Generation: {generation} | Score: {score} | Best Score: {best_score}")


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    p.run(eval_genomes, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
    pygame.quit()
