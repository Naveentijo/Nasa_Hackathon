import pygame
import sys
import math
import random

pygame.init()

# Screen
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Crew - Multi-Planet Gravity + Shuttle + Task")

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,150,255)
GRAY = (100,100,100)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
ORANGE = (255,165,0)
PURPLE = (180,0,255)

font = pygame.font.SysFont("Arial", 20)

# ================= OUTSIDE MODE (Space Travel) ==================
astronaut_x, astronaut_y = 1000.0, 1000.0   # world coords
astronaut_dx, astronaut_dy = 0.0, 0.0       # velocity
ASTRONAUT_SIZE = 40

# Celestial bodies (planets, stars, moons) - SPACED OUT
# Modify your celestial_bodies list like this (added orbit_center & orbit_radius for moons/planets):

celestial_bodies = [
    {"name": "Sun",     "pos": (3000, 2000),  "radius": 120,"color": YELLOW, "g": 2.5, "influence": 800},
    {"name": "Earth",   "pos": (5000, 2000),  "radius": 60, "color": BLUE,   "g": 1.0, "influence": 500, "orbit_center": (3000,2000), "orbit_radius": 2000},
    {"name": "Moon",    "pos": (5200, 2100),  "radius": 20, "color": GRAY,   "g": 0.4, "influence": 200, "orbit_center": (5000,2000), "orbit_radius": 250},
    {"name": "Jupiter", "pos": (9000, 2500),  "radius": 100,"color": ORANGE, "g": 1.8, "influence": 700, "orbit_center": (3000,2000), "orbit_radius": 6000},
    {"name": "Europa",  "pos": (9300, 2600),  "radius": 25, "color": WHITE,  "g": 0.3, "influence": 200, "orbit_center": (9000,2500), "orbit_radius": 400},
    {"name": "Neptune", "pos": (15000, 3500), "radius": 70, "color": PURPLE, "g": 1.2, "influence": 600, "orbit_center": (3000,2000), "orbit_radius": 12000},
]


# Tuning parameters
OUTSIDE_THRUST = 0.08
OUTSIDE_FRICTION = 0.998
INSIDE_GRAVITY_SCALE = 0.45
INSIDE_MANUAL_MULT = 1.0
MIN_DIST = 10.0

# ================= INSIDE MODE (Shuttle Rooms) ==================
astronaut_inside = pygame.Rect(150, 150, 40, 40)
astronaut_inside_x = float(astronaut_inside.x)
astronaut_inside_y = float(astronaut_inside.y)
astronaut_speed_inside = 4

walls = [
    pygame.Rect(0, 0, WIDTH, 10),
    pygame.Rect(0, HEIGHT-10, WIDTH, 10),
    pygame.Rect(0, 0, 10, HEIGHT),
    pygame.Rect(WIDTH-10, 0, 10, HEIGHT),
    pygame.Rect(300, 0, 10, 300),
    pygame.Rect(0, 300, WIDTH, 10),
]

doors = [
    pygame.Rect(280, 140, 40, 40),
    pygame.Rect(430, 290, 40, 40),
]

task_terminal = pygame.Rect(600, 150, 40, 40)

def draw_shuttle():
    for wall in walls:
        pygame.draw.rect(screen, GRAY, wall)
    for door in doors:
        pygame.draw.rect(screen, GREEN, door)
    pygame.draw.rect(screen, RED, task_terminal)
    cockpit = font.render("Cockpit", True, WHITE)
    control = font.render("Control Room", True, WHITE)
    engine = font.render("Engine Room", True, WHITE)
    screen.blit(cockpit, (100, 50))
    screen.blit(control, (500, 50))
    screen.blit(engine, (400, 400))

def check_collision(rect, move_x, move_y):
    future_rect = rect.move(move_x, move_y)
    for wall in walls:
        if future_rect.colliderect(wall):
            allowed = False
            for door in doors:
                if future_rect.colliderect(door):
                    allowed = True
            if not allowed:
                return False
    return True

# ================= MINI-GAME (Asteroid Shooting) ==================
class Asteroid:
    def _init_(self):
        self.rect = pygame.Rect(random.randint(50, WIDTH-50), -20, 30, 30)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = -20
            self.rect.x = random.randint(50, WIDTH-50)

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)

class Bullet:
    def _init_(self, x, y):
        self.rect = pygame.Rect(x, y, 5, 10)

    def update(self):
        self.rect.y -= 10

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

def asteroid_mini_game():
    bullets = []
    asteroids = [Asteroid() for _ in range(5)]
    player = pygame.Rect(WIDTH//2, HEIGHT-60, 40, 40)
    score = 0

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= 5
        if keys[pygame.K_RIGHT]:
            player.x += 5
        if keys[pygame.K_SPACE]:
            if len(bullets) < 5:
                bullets.append(Bullet(player.centerx, player.top))
        if keys[pygame.K_ESCAPE]:
            running = False

        for bullet in bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)

        for asteroid in asteroids:
            asteroid.update()
            for bullet in bullets[:]:
                if asteroid.rect.colliderect(bullet.rect):
                    bullets.remove(bullet)
                    score += 1
                    asteroid.rect.y = -20
                    asteroid.rect.x = random.randint(50, WIDTH-50)

        pygame.draw.rect(screen, BLUE, player)
        for bullet in bullets:
            bullet.draw()
        for asteroid in asteroids:
            asteroid.draw()

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        exit_text = font.render("Press ESC to return", True, WHITE)
        screen.blit(exit_text, (WIDTH//2 - 100, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)

# ================= GAME STATE ==================
game_mode = "outside"  # outside, inside, or task
clock = pygame.time.Clock()

def compute_net_gravity_at_point(x, y):
    net_x, net_y = 0.0, 0.0
    for body in celestial_bodies:
        bx, by = body["pos"]
        dx = bx - x
        dy = by - y
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            dist = MIN_DIST
        if dist < body["influence"]:
            nx = dx / dist
            ny = dy / dist
            factor = body["g"] * (1.0 - (dist / body["influence"]))
            net_x += nx * factor
            net_y += ny * factor
    return net_x, net_y

# --- Add this function before the main loop ---
def draw_radar(player_x, player_y, radar_center=(WIDTH-120, 120), radar_radius=100, radar_range=2500):
    # Radar background
    pygame.draw.circle(screen, (30,30,30), radar_center, radar_radius)
    pygame.draw.circle(screen, WHITE, radar_center, radar_radius, 2)

    # Draw orbit lines
    for body in celestial_bodies:
        if "orbit_center" in body and "orbit_radius" in body:
            cx, cy = body["orbit_center"]
            screen_x = cx - camera_x
            screen_y = cy - camera_y
            pygame.draw.circle(screen, (80,80,80), (int(screen_x), int(screen_y)), body["orbit_radius"], 1)

    
    # Draw celestial bodies
    for body in celestial_bodies:
        bx, by = body["pos"]
        dx, dy = bx - player_x, by - player_y
        dist = math.hypot(dx, dy)
        if dist < radar_range:
            # Scale into radar
            rx = radar_center[0] + int(dx / radar_range * radar_radius)
            ry = radar_center[1] + int(dy / radar_range * radar_radius)
            pygame.draw.circle(screen, body["color"], (rx, ry), 4)

    # Player marker (astronaut)
    pygame.draw.circle(screen, YELLOW, radar_center, 5)


# ================= MAIN LOOP ==================
while True:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if game_mode == "outside":
        # Movement controls
        if keys[pygame.K_LEFT]:
            astronaut_dx -= OUTSIDE_THRUST
        if keys[pygame.K_RIGHT]:
            astronaut_dx += OUTSIDE_THRUST
        if keys[pygame.K_UP]:
            astronaut_dy -= OUTSIDE_THRUST
        if keys[pygame.K_DOWN]:
            astronaut_dy += OUTSIDE_THRUST

        # Apply gravity
        g_x, g_y = compute_net_gravity_at_point(astronaut_x, astronaut_y)
        astronaut_dx += g_x
        astronaut_dy += g_y

        # Update position
        astronaut_x += astronaut_dx
        astronaut_y += astronaut_dy

        astronaut_dx *= OUTSIDE_FRICTION
        astronaut_dy *= OUTSIDE_FRICTION

        # Camera follows astronaut
        camera_x = astronaut_x - WIDTH // 2
        camera_y = astronaut_y - HEIGHT // 2

        # Draw celestial bodies
        near_body = None
        min_d = float("inf")
        for body in celestial_bodies:
            bx, by = body["pos"]
            screen_x = bx - camera_x
            screen_y = by - camera_y
            pygame.draw.circle(screen, body["color"], (int(screen_x), int(screen_y)), body["radius"])
            text = font.render(body["name"], True, WHITE)
            screen.blit(text, (screen_x-20, screen_y-body["radius"]-20))

            d = math.hypot(bx - astronaut_x, by - astronaut_y)
            if d < body["influence"] and d < min_d:
                min_d = d
                near_body = body

        # Draw astronaut
        astronaut_rect = pygame.Rect(0, 0, ASTRONAUT_SIZE, ASTRONAUT_SIZE)
        astronaut_rect.center = (astronaut_x - camera_x, astronaut_y - camera_y)
        pygame.draw.rect(screen, BLUE, astronaut_rect)

        if near_body:
            msg = font.render(f"Press E to enter shuttle orbiting {near_body['name']}", True, WHITE)
            screen.blit(msg, (300, 750))
            if keys[pygame.K_e]:
                game_mode = "inside"
                astronaut_inside.center = (150, 150)

        # --- Draw radar here ---
        draw_radar(astronaut_x, astronaut_y)

    elif game_mode == "inside":
        move_x, move_y = 0.0, 0.0
        if keys[pygame.K_LEFT]:
            move_x = -astronaut_speed_inside * INSIDE_MANUAL_MULT
        if keys[pygame.K_RIGHT]:
            move_x = astronaut_speed_inside * INSIDE_MANUAL_MULT
        if keys[pygame.K_UP]:
            move_y = -astronaut_speed_inside * INSIDE_MANUAL_MULT
        if keys[pygame.K_DOWN]:
            move_y = astronaut_speed_inside * INSIDE_MANUAL_MULT

        net_gx, net_gy = compute_net_gravity_at_point(astronaut_x, astronaut_y)
        gravity_move_x = net_gx * INSIDE_GRAVITY_SCALE
        gravity_move_y = net_gy * INSIDE_GRAVITY_SCALE

        if check_collision(astronaut_inside, int(move_x), 0):
            astronaut_inside_x += move_x
        if check_collision(astronaut_inside, 0, int(move_y)):
            astronaut_inside_y += move_y

        astronaut_inside.x = int(round(astronaut_inside_x + gravity_move_x))
        astronaut_inside.y = int(round(astronaut_inside_y + gravity_move_y))

        draw_shuttle()
        pygame.draw.rect(screen, BLUE, astronaut_inside)

        if astronaut_inside.colliderect(task_terminal):
            msg = font.render("Press E to start Asteroid Defense Task", True, WHITE)
            screen.blit(msg, (400, 760))
            if keys[pygame.K_e]:
                game_mode = "task"
                asteroid_mini_game()
                game_mode = "inside"

        msg = font.render("Press Q to go back outside", True, WHITE)
        screen.blit(msg, (500, 770))
        if keys[pygame.K_q]:
            game_mode = "outside"
            astronaut_dx = astronaut_dy = 0.0

    pygame.display.flip()
    clock.tick(60)