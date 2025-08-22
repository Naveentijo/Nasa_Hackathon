import pygame
import math
from settings import celestial_bodies, font, WIDTH, HEIGHT, PURPLE

def handle_navigation(screen, astronaut_x, astronaut_y, path_history, closest_body, show_path, keys):
    # Scaling and centering for map (Sun at left with margin)
    map_scale = 0.08
    sun_pos = (3000, 2000)
    map_sun_x = 200
    map_sun_y = HEIGHT // 2

    # Draw black background
    screen.fill((0, 0, 0))

    # Draw orbits
    for body in celestial_bodies:
        if "orbit_center" in body and "orbit_radius" in body:
            cx, cy = body["orbit_center"]
            orbit_x = map_sun_x + (cx - sun_pos[0]) * map_scale
            orbit_y = map_sun_y + (cy - sun_pos[1]) * map_scale
            pygame.draw.circle(screen, (80, 80, 80), (int(orbit_x), int(orbit_y)), int(body["orbit_radius"] * map_scale), 1)

    # Draw celestial bodies
    for body in celestial_bodies:
        bx, by = body["pos"]
        map_x = map_sun_x + (bx - sun_pos[0]) * map_scale
        map_y = map_sun_y + (by - sun_pos[1]) * map_scale
        radius = 10 if body == closest_body else 5
        color = (0, 255, 0) if body == closest_body else body["color"]
        pygame.draw.circle(screen, color, (int(map_x), int(map_y)), radius)
        text = font.render(body["name"], True, (255, 255, 255))
        screen.blit(text, (map_x - 20, map_y - 20))

    # Draw spacecraft
    map_player_x = map_sun_x + (astronaut_x - sun_pos[0]) * map_scale
    map_player_y = map_sun_y + (astronaut_y - sun_pos[1]) * map_scale
    pygame.draw.rect(screen, (50, 150, 255), (map_player_x - 5, map_player_y - 5, 10, 10))

    # Draw path if toggled
    if show_path and len(path_history) > 1:
        for i in range(1, len(path_history)):
            prev_x, prev_y = path_history[i-1]
            curr_x, curr_y = path_history[i]
            line_start_x = map_sun_x + (prev_x - sun_pos[0]) * map_scale
            line_start_y = map_sun_y + (prev_y - sun_pos[1]) * map_scale
            line_end_x = map_sun_x + (curr_x - sun_pos[0]) * map_scale
            line_end_y = map_sun_y + (curr_y - sun_pos[1]) * map_scale
            pygame.draw.line(screen, (255, 255, 0), (line_start_x, line_start_y), (line_end_x, line_end_y), 2)

    # Handle inputs
    new_closest_body = closest_body
    new_show_path = show_path
    new_game_mode = "navigation"
    if keys[pygame.K_m]:
        pass  # Map is already shown
    if keys[pygame.K_c]:
        min_dist = float("inf")
        new_closest_body = None
        for body in celestial_bodies:
            if "orbit_center" in body:  # Exclude Sun
                dist = math.hypot(body["pos"][0] - astronaut_x, body["pos"][1] - astronaut_y)
                if dist < min_dist:
                    min_dist = dist
                    new_closest_body = body
    if keys[pygame.K_p]:
        new_show_path = not show_path
    if keys[pygame.K_ESCAPE]:
        new_game_mode = "inside"

    # Draw instructions
    instr1 = font.render("M: Refresh Map | C: Find Closest Planet | P: Toggle Path | ESC: Exit", True, (255, 255, 255))
    screen.blit(instr1, (20, 20))
    if new_closest_body:
        closest_msg = font.render(f"Closest: {new_closest_body['name']} (highlighted green)", True, (255, 255, 255))
        screen.blit(closest_msg, (20, 50))

    return new_closest_body, new_show_path, new_game_mode