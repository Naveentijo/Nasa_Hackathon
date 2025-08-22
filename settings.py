import pygame
import sys
import math
import random

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
astronaut_x, astronaut_y = 1000.0, 1000.0
astronaut_dx, astronaut_dy = 0.0, 0.0
ASTRONAUT_SIZE = 40

# Thruster system
manual_thrust = 0.15   # manual nudge power
boost_thrust = 0.4     # thrust when auto/space engaged

# Celestial bodies
celestial_bodies = [
    {"name": "Sun",     "pos": (3000, 2000),  "radius": 120,"color": YELLOW, "g": 2.5, "influence": 800},
    {"name": "Earth",   "pos": (5000, 2000),  "radius": 60, "color": BLUE,   "g": 1.0, "influence": 500, "orbit_center": (3000,2000), "orbit_radius": 2000},
    {"name": "Moon",    "pos": (5200, 2100),  "radius": 20, "color": GRAY,   "g": 0.4, "influence": 200, "orbit_center": (5000,2000), "orbit_radius": 250},
    {"name": "Jupiter", "pos": (9000, 2500),  "radius": 100,"color": ORANGE, "g": 1.8, "influence": 700, "orbit_center": (3000,2000), "orbit_radius": 6000},
    {"name": "Europa",  "pos": (9300, 2600),  "radius": 25, "color": WHITE,  "g": 0.3, "influence": 200, "orbit_center": (9000,2500), "orbit_radius": 400},
    {"name": "Neptune", "pos": (15000, 3500), "radius": 70, "color": PURPLE, "g": 1.2, "influence": 600, "orbit_center": (3000,2000), "orbit_radius": 12000},
]

# Tuning parameters
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
