import pygame
import neat
import random
import os
import math

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
PARTICLE_LIFETIME = 25
MAX_PARTICLES = 200
TRANSITION_FRAMES = 45

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_TOP = (80, 160, 240)
SKY_BOTTOM = (190, 225, 250)
GREEN_PIPE = (60, 185, 60)
GREEN_CAP = (35, 120, 35)
YELLOW = (255, 220, 50)
YELLOW_DARK = (220, 180, 20)
ORANGE = (255, 150, 20)
BEAK_LINE = (200, 120, 10)
GRASS_TOP = (70, 195, 50)
GROUND_BROWN = (139, 90, 43)
GROUND_DARK = (100, 65, 30)
CLOUD_COLOR = (240, 245, 255)
GOLD = (255, 215, 0)
HUD_BG = (0, 0, 0, 140)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("NEAT Flappy Bird")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Arial", 20)
font_mid = pygame.font.SysFont("Arial", 28)
font_large = pygame.font.SysFont("Arial", 42)
font_huge = pygame.font.SysFont("Arial", 56)

generation = 0
best_score = 0
gen_scores = []

bg_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
for y in range(WINDOW_HEIGHT):
    t = y / WINDOW_HEIGHT
    r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
    g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
    b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
    pygame.draw.line(bg_surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))

bird_surface = pygame.Surface((BIRD_RADIUS * 2 + 10, BIRD_RADIUS * 2 + 10), pygame.SRCALPHA)
bc = BIRD_RADIUS + 5
pygame.draw.circle(bird_surface, YELLOW, (bc, bc), BIRD_RADIUS)
pygame.draw.ellipse(bird_surface, YELLOW_DARK, (bc - BIRD_RADIUS + 5, bc - 3, BIRD_RADIUS - 3, BIRD_RADIUS // 2 + 1))
pygame.draw.circle(bird_surface, WHITE, (bc + 3, bc - 4), 5)
pygame.draw.circle(bird_surface, BLACK, (bc + 5, bc - 5), 2)
pygame.draw.line(bird_surface, (180, 130, 30), (bc, bc - 9), (bc + 11, bc - 8), 2)
beak = [(bc + BIRD_RADIUS - 2, bc - 2), (bc + BIRD_RADIUS + 8, bc + 3), (bc + BIRD_RADIUS - 2, bc + 6)]
pygame.draw.polygon(bird_surface, ORANGE, beak)
pygame.draw.line(bird_surface, BEAK_LINE, beak[0], beak[2], 2)
bird_mask = pygame.mask.from_surface(bird_surface)


class Bird:
    def __init__(self):
        self.x = 100
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.radius = BIRD_RADIUS
        self.best = False

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        screen.blit(bird_surface, (self.x - self.radius - 5, int(self.y) - self.radius - 5))
        if self.best:
            pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), self.radius + 6, 2)


class Cloud:
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(30, 280)
        self.speed = random.uniform(0.15, 0.4)
        a = random.randint(35, 65)
        w, h = random.randint(80, 140), random.randint(25, 45)
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        color = (*CLOUD_COLOR, a)
        cx, cy = w // 2, h // 2
        pygame.draw.ellipse(self.surface, color, (w * 0.08, h * 0.1, w * 0.8, h * 0.85))
        pygame.draw.ellipse(self.surface, color, (w * 0.2, 0, w * 0.55, h * 0.7))
        pygame.draw.ellipse(self.surface, color, (0, h * 0.2, w * 0.6, h * 0.7))
        pygame.draw.ellipse(self.surface, color, (w * 0.35, h * 0.15, w * 0.65, h * 0.7))

    def update(self):
        self.x -= self.speed
        if self.x + self.surface.get_width() < 0:
            self.x = WINDOW_WIDTH + random.randint(0, 150)
            self.y = random.randint(30, 280)

    def draw(self):
        screen.blit(self.surface, (int(self.x), int(self.y)))


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap = GAP_SIZE
        self.height = random.randint(200, 600)
        self.passed = False

        self.top_h = self.height - self.gap // 2
        self.bot_y = self.height + self.gap // 2
        self.bot_h = WINDOW_HEIGHT - GROUND_HEIGHT - self.bot_y

        self.top_surf = pygame.Surface((PIPE_WIDTH, self.top_h))
        self.top_surf.fill(GREEN_PIPE)
        self.top_mask = pygame.mask.from_surface(self.top_surf)

        self.bot_surf = pygame.Surface((PIPE_WIDTH, self.bot_h))
        self.bot_surf.fill(GREEN_PIPE)
        self.bot_mask = pygame.mask.from_surface(self.bot_surf)

        cap_w = PIPE_WIDTH + 10
        cap_h_t = min(22, self.top_h)
        self.top_cap = pygame.Surface((cap_w, cap_h_t))
        self.top_cap.fill(GREEN_CAP)
        pygame.draw.rect(self.top_cap, (30, 100, 30), (0, 0, cap_w, cap_h_t), 2)

        cap_h_b = min(22, self.bot_h)
        self.bot_cap = pygame.Surface((cap_w, cap_h_b))
        self.bot_cap.fill(GREEN_CAP)
        pygame.draw.rect(self.bot_cap, (30, 100, 30), (0, 0, cap_w, cap_h_b), 2)

    def update(self):
        self.x -= SCROLL_SPEED

    def draw(self):
        screen.blit(self.top_surf, (int(self.x), 0))
        screen.blit(self.bot_surf, (int(self.x), self.bot_y))
        cap_x = int(self.x) - 5
        screen.blit(self.top_cap, (cap_x, self.top_h - self.top_cap.get_height()))
        screen.blit(self.bot_cap, (cap_x, self.bot_y))

    def offscreen(self):
        return self.x + PIPE_WIDTH < 0

    def collide(self, bird):
        bx = bird.x - bird.radius - 5
        by = bird.y - bird.radius - 5
        bw = bird_mask.get_size()[0]
        bird_rect = pygame.Rect(bx, by, bw, bw)
        pipe_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, WINDOW_HEIGHT)
        if not bird_rect.colliderect(pipe_rect):
            return False
        ox = int(self.x - bx)
        oy_top = int(0 - by)
        if bird_mask.overlap(self.top_mask, (ox, oy_top)):
            return True
        oy_bot = int(self.bot_y - by)
        if bird_mask.overlap(self.bot_mask, (ox, oy_bot)):
            return True
        cap_w = PIPE_WIDTH + 10
        cap_rect_y = self.top_h - self.top_cap.get_height()
        cap_rect = pygame.Rect(self.x - 5, cap_rect_y, cap_w, self.top_cap.get_height())
        if bird_rect.colliderect(cap_rect):
            return True
        cap_rect2 = pygame.Rect(self.x - 5, self.bot_y, cap_w, self.bot_cap.get_height())
        if bird_rect.colliderect(cap_rect2):
            return True
        return False


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2
        self.life = PARTICLE_LIFETIME
        self.max_life = PARTICLE_LIFETIME
        self.color = random.choice([(255, 200, 50), (255, 150, 50), (255, 100, 50), (200, 50, 50)])
        self.radius = random.uniform(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self):
        t = self.life / self.max_life
        alpha = int(t * 200)
        r = int(self.radius * t + 0.5)
        if r < 1:
            r = 1
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        c = (*self.color, alpha)
        pygame.draw.circle(surf, c, (r, r), r)
        screen.blit(surf, (int(self.x) - r, int(self.y) - r))


clouds = [Cloud() for _ in range(5)]
particles = []


def spawn_particles(x, y, count=12):
    for _ in range(count):
        if len(particles) < MAX_PARTICLES:
            particles.append(Particle(x, y))


def draw_scene(birds, pipes):
    screen.blit(bg_surface, (0, 0))
    for c in clouds:
        c.draw()
    for p in pipes:
        p.draw()
    for bird in birds:
        bird.draw()
    for p in particles:
        p.draw()

    ground_rect = pygame.Rect(0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, GROUND_HEIGHT)
    pygame.draw.rect(screen, GRASS_TOP, (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, 8))
    pygame.draw.rect(screen, GROUND_BROWN, (0, WINDOW_HEIGHT - GROUND_HEIGHT + 8, WINDOW_WIDTH, GROUND_HEIGHT - 8))
    pygame.draw.rect(screen, GROUND_DARK, (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, 2))

    for gx in range(0, WINDOW_WIDTH, 40):
        gh = random.randint(3, 7)
        pygame.draw.line(screen, (60, 180, 40), (gx, WINDOW_HEIGHT - GROUND_HEIGHT), (gx, WINDOW_HEIGHT - GROUND_HEIGHT - gh), 2)


def draw_hud(score, alive, gen, best):
    panel = pygame.Surface((WINDOW_WIDTH, 95), pygame.SRCALPHA)
    pygame.draw.rect(panel, HUD_BG, (0, 0, WINDOW_WIDTH, 95))
    pygame.draw.line(panel, (255, 255, 255, 60), (0, 94), (WINDOW_WIDTH, 94))
    screen.blit(panel, (0, 0))

    texts = [
        (f"Score: {score}", 20),
        (f"Generation: {gen}  |  Alive: {alive}", 48),
        (f"Best Score: {best}", 72),
    ]
    for text, y in texts:
        surf = font_small.render(text, True, WHITE)
        screen.blit(surf, (15, y))


def show_transition(score, gen, best, pipes, frames_left):
    screen.blit(bg_surface, (0, 0))
    for c in clouds:
        c.draw()
    for p in pipes:
        p.draw()

    ground_rect = pygame.Rect(0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, GROUND_HEIGHT)
    pygame.draw.rect(screen, GRASS_TOP, (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, 8))
    pygame.draw.rect(screen, GROUND_BROWN, (0, WINDOW_HEIGHT - GROUND_HEIGHT + 8, WINDOW_WIDTH, GROUND_HEIGHT - 8))

    t = 1 - (frames_left / TRANSITION_FRAMES)
    if t < 0:
        t = 0
    if t > 1:
        t = 1

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    alpha = int(t * 160)
    pygame.draw.rect(overlay, (0, 0, 0, alpha), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(overlay, (0, 0))

    title = font_huge.render("Generation Complete", True, WHITE)
    title_shadow = font_huge.render("Generation Complete", True, BLACK)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
    screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title, title_rect)

    stats = f"Generation: {gen}  |  Score: {score}  |  Best: {best}"
    st = font_large.render(stats, True, WHITE)
    st_rect = st.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
    screen.blit(st, st_rect)

    if score >= best:
        record = font_mid.render("NEW BEST!", True, GOLD)
        rec_rect = record.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        screen.blit(record, rec_rect)

    wait = font_mid.render("Starting next generation...", True, (200, 200, 200))
    wait_rect = wait.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
    screen.blit(wait, wait_rect)

    pygame.display.update()


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
    best_fitness_this_gen = 0

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

            if ge[i].fitness > best_fitness_this_gen:
                best_fitness_this_gen = ge[i].fitness
            bird.best = (ge[i].fitness == best_fitness_this_gen)

        if frame_count % PIPE_SPAWN_INTERVAL == 0:
            pipes.append(Pipe(WINDOW_WIDTH))

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
                spawn_particles(bird.x, bird.y)
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)
                continue

            for pipe in pipes:
                if pipe.collide(bird):
                    spawn_particles(bird.x, bird.y)
                    birds.pop(i)
                    nets.pop(i)
                    ge.pop(i)
                    break

        for c in clouds:
            c.update()
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        draw_scene(birds, pipes)
        draw_hud(score, len(birds), generation, best_score)

        pygame.display.update()

    if score > best_score:
        best_score = score

    print(f"Generation: {generation} | Score: {score} | Best Score: {best_score}")

    for remaining in range(TRANSITION_FRAMES, 0, -1):
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        show_transition(score, generation, best_score, pipes, remaining)
    particles.clear()


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
