import pygame
pygame.font.init()
from settings import *
from entities import *
from tasks import asteroid_mini_game
from navigation import handle_navigation
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Crew - Multi-Planet Gravity + Shuttle + Task")

# ================= GAME STATE ==================
game_mode = "outside"
clock = pygame.time.Clock()
path_history = []  # Track spacecraft path
closest_body = None  # Track closest planet
show_path = False  # Toggle path display
frame_counter = 0  # For sampling path history

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

def draw_radar(player_x, player_y, radar_center=(WIDTH-120, 120), radar_radius=100, radar_range=2500):
    pygame.draw.circle(screen, (30,30,30), radar_center, radar_radius)
    pygame.draw.circle(screen, WHITE, radar_center, radar_radius, 2)

    for body in celestial_bodies:
        if "orbit_center" in body and "orbit_radius" in body:
            cx, cy = body["orbit_center"]
            screen_x = cx - camera_x
            screen_y = cy - camera_y
            pygame.draw.circle(screen, (80,80,80), (int(screen_x), int(screen_y)), body["orbit_radius"], 1)

    for body in celestial_bodies:
        bx, by = body["pos"]
        dx, dy = bx - player_x, by - player_y
        dist = math.hypot(dx, dy)
        if dist < radar_range:
            rx = radar_center[0] + int(dx / radar_range * radar_radius)
            ry = radar_center[1] + int(dy / radar_range * radar_radius)
            pygame.draw.circle(screen, body["color"], (rx, ry), 4)

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
        # Gravity
        g_x, g_y = compute_net_gravity_at_point(astronaut_x, astronaut_y)

        # Check if near a celestial body
        in_gravity_zone = (abs(g_x) > 0.0001 or abs(g_y) > 0.0001)

        # Movement input
        thrust_dx, thrust_dy = 0.0, 0.0
        if keys[pygame.K_UP]:
            thrust_dy -= manual_thrust
        if keys[pygame.K_DOWN]:
            thrust_dy += manual_thrust
        if keys[pygame.K_LEFT]:
            thrust_dx -= manual_thrust
        if keys[pygame.K_RIGHT]:
            thrust_dx += manual_thrust

        # Boost
        if in_gravity_zone or keys[pygame.K_SPACE]:
            if keys[pygame.K_UP]:
                thrust_dy -= boost_thrust
            if keys[pygame.K_DOWN]:
                thrust_dy += boost_thrust
            if keys[pygame.K_LEFT]:
                thrust_dx -= boost_thrust
            if keys[pygame.K_RIGHT]:
                thrust_dx += boost_thrust

        astronaut_dx += thrust_dx
        astronaut_dy += thrust_dy

        # Apply gravity
        astronaut_dx += g_x
        astronaut_dy += g_y

        # Update position
        astronaut_x += astronaut_dx
        astronaut_y += astronaut_dy
        astronaut_dx *= OUTSIDE_FRICTION
        astronaut_dy *= OUTSIDE_FRICTION

        # Record path history every 5 frames
        frame_counter += 1
        if frame_counter % 5 == 0:
            path_history.append((astronaut_x, astronaut_y))
            if len(path_history) > 1000:
                path_history.pop(0)

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

        # Draw flame when boosting
        if (in_gravity_zone or keys[pygame.K_SPACE]) and (keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            flame_length = 15
            flame_color = (255, 120, 0)
            fx = astronaut_rect.centerx - int(thrust_dx * 20)
            fy = astronaut_rect.centery - int(thrust_dy * 20)
            pygame.draw.line(screen, flame_color, (astronaut_rect.centerx, astronaut_rect.centery), (fx, fy), 4)

        # Radar
        draw_radar(astronaut_x, astronaut_y)

        # Enter shuttle prompt
        if near_body:
            msg = font.render(f"Press E to enter shuttle orbiting {near_body['name']}", True, WHITE)
            screen.blit(msg, (300, 750))
            if keys[pygame.K_e]:
                game_mode = "inside"
                astronaut_inside.center = (150, 150)

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

        if astronaut_inside.colliderect(navigation_terminal):
            msg = font.render("Press E to open Navigation System", True, WHITE)
            screen.blit(msg, (800, 760))
            if keys[pygame.K_e]:
                game_mode = "navigation"
                closest_body = None
                show_path = False

        msg = font.render("Press Q to go back outside", True, WHITE)
        screen.blit(msg, (500, 770))
        if keys[pygame.K_q]:
            game_mode = "outside"
            astronaut_dx = astronaut_dy = 0.0

    elif game_mode == "navigation":
        closest_body, show_path, game_mode = handle_navigation(screen, astronaut_x, astronaut_y, path_history, closest_body, show_path, keys)

    pygame.display.flip()
    clock.tick(60)