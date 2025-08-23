import pygame
import sys
import random
import math
from settings import *

# Task completion status
task_status = {
    "gas_mix": False,
    "overheating": False,
    "leak_repair": False
}

def gas_mix_mini_game():
    def reset_task():
        return {
            "o2_knob_y": 300,
            "n2_knob_y": 300,
            "dragging_o2": False,
            "dragging_n2": False,
            "success": False,
            "confirmed": False,
            "msg": ""
        }

    state = reset_task()
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not state["confirmed"]:
                    if pygame.Rect(200, 200, 20, 200).collidepoint(event.pos):
                        state["dragging_o2"] = True
                    elif pygame.Rect(400, 200, 20, 200).collidepoint(event.pos):
                        state["dragging_n2"] = True
            if event.type == pygame.MOUSEBUTTONUP:
                state["dragging_o2"] = False
                state["dragging_n2"] = False
            if event.type == pygame.MOUSEMOTION:
                if state["dragging_o2"]:
                    state["o2_knob_y"] = max(200, min(400, event.pos[1]))
                if state["dragging_n2"]:
                    state["n2_knob_y"] = max(200, min(400, event.pos[1]))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_RETURN and not state["confirmed"]:
                    o2_level = 100 - (state["o2_knob_y"] - 200) / 2
                    n2_level = 100 - (state["n2_knob_y"] - 200) / 2
                    total = o2_level + n2_level
                    if abs(total - 100) > 5:
                        state["msg"] = "Gases must add up to ~100%!"
                    elif o2_level > 25:
                        state["msg"] = "Too much oxygen! Fire risk!"
                    elif 20 <= o2_level <= 22 and 78 <= n2_level <= 80:
                        state["success"] = True
                        state["msg"] = "Success! Correct ratio."
                    else:
                        state["msg"] = "Failure: Incorrect ratio."
                    state["confirmed"] = True
                    print(f"Gas Mix: Confirmed, success={state['success']}, o2={o2_level:.1f}%, n2={n2_level:.1f}%")
                    pygame.time.wait(2000)
                if event.key == pygame.K_SPACE and state["confirmed"] and not state["success"]:
                    state = reset_task()
                    print("Gas Mix: Retrying")

        # Calculate levels for display
        o2_level = 100 - (state["o2_knob_y"] - 200) / 2
        n2_level = 100 - (state["n2_knob_y"] - 200) / 2
        total = o2_level + n2_level

        # Draw sliders (no green target indicators)
        pygame.draw.rect(screen, GRAY, (200, 200, 20, 200))
        pygame.draw.rect(screen, GRAY, (400, 200, 20, 200))
        pygame.draw.rect(screen, BLUE, (200, state["o2_knob_y"] - 10, 20, 20))
        pygame.draw.rect(screen, GREEN, (400, state["n2_knob_y"] - 10, 20, 20))

        # Labels and values
        try:
            screen.blit(font.render("O2 Slider", True, WHITE), (180, 150))
            screen.blit(font.render(f"{o2_level:.1f}%", True, WHITE), (180, 420))
            screen.blit(font.render("N2 Slider", True, WHITE), (380, 150))
            screen.blit(font.render(f"{n2_level:.1f}%", True, WHITE), (380, 420))
            screen.blit(font.render(f"Total: {total:.1f}%", True, WHITE), (300, 450))
            screen.blit(font.render("Adjust to 21% O2 / 79% N2", True, WHITE), (200, 50))
            screen.blit(font.render("Press ENTER to confirm, ESC to exit", True, WHITE), (200, 500))

            if state["confirmed"]:
                final_msg = "Success!" if state["success"] else "Failure!"
                final_color = GREEN if state["success"] else RED
                screen.blit(font.render(final_msg, True, final_color), (200, 600))
                if state["success"]:
                    screen.blit(font.render("Press ESC to exit", True, WHITE), (200, 650))
                else:
                    screen.blit(font.render("Press SPACE to try again, ESC to exit", True, WHITE), (200, 650))
            else:
                color = GREEN if state["success"] else RED
                screen.blit(font.render(state["msg"], True, color), (200, 470))
        except pygame.error as e:
            print(f"Font rendering error in gas_mix_mini_game: {e}")
            running = False

        if state["confirmed"] and state["success"]:
            running = False

        pygame.display.flip()
        clock.tick(60)

    if state["success"]:
        task_status["gas_mix"] = True
        print("Gas Mix: Task completed successfully")
    return state["success"]

def overheating_mini_game():
    def reset_task():
        return {
            "zones": [random.randint(100, 500) for _ in range(5)],
            "current_round": 0,
            "indicator_x": 0,
            "success": False,
            "completed": False,
            "hits": 0,
            "round_results": [],
            "space_pressed": False
        }

    state = reset_task()
    speed = 5
    green_width = 50
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not state["completed"] and event.key == pygame.K_SPACE and not state["space_pressed"]:
                    state["space_pressed"] = True
                    green_start = state["zones"][state["current_round"]]
                    if green_start <= state["indicator_x"] <= green_start + green_width:
                        state["hits"] += 1
                        state["round_results"].append("Hit!")
                        print(f"Overheating: Hit! Total hits: {state['hits']}")
                    else:
                        state["round_results"].append("Miss!")
                        print("Overheating: Miss!")
                    state["current_round"] += 1
                    state["indicator_x"] = 0
                    if state["current_round"] >= 5:
                        state["completed"] = True
                        state["success"] = state["hits"] >= 5
                        print(f"Overheating: Completed, hits={state['hits']}, success={state['success']}")
                        if state["success"]:
                            pygame.time.wait(2000)  # 2-second delay for "Issue Resolved"
                if event.key == pygame.K_SPACE and state["completed"] and not state["success"]:
                    state = reset_task()
                    print("Overheating: Retrying")
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    state["space_pressed"] = False

        if not state["completed"]:
            state["indicator_x"] += speed
            if state["indicator_x"] > WIDTH:
                state["indicator_x"] = 0
                if not state["space_pressed"]:
                    state["round_results"].append("Miss!")
                    print("Overheating: Miss (timeout)!")
                state["space_pressed"] = False
                state["current_round"] += 1
                if state["current_round"] >= 5:
                    state["completed"] = True
                    state["success"] = state["hits"] >= 5
                    print(f"Overheating: Completed, hits={state['hits']}, success={state['success']}")
                    if state["success"]:
                        pygame.time.wait(2000)  # 2-second delay for "Issue Resolved"

        # Draw progress bar
        pygame.draw.rect(screen, GRAY, (200, 150, 200, 20))
        progress_width = (state["hits"] / 5) * 200
        pygame.draw.rect(screen, GREEN, (200, 150, progress_width, 20))

        # Draw timing bar
        pygame.draw.rect(screen, GRAY, (50, 300, WIDTH-100, 20))
        if not state["completed"] and state["current_round"] < 5:
            green_start = state["zones"][state["current_round"]]
            pygame.draw.rect(screen, GREEN, (50 + green_start, 300, green_width, 20))
        pygame.draw.circle(screen, WHITE, (50 + state["indicator_x"], 310), 10)

        # Labels
        try:
            screen.blit(font.render(f"Round {state['current_round']+1}/5 | Hits: {state['hits']}", True, WHITE), (200, 200))
            screen.blit(font.render("Press SPACE when in green zone", True, WHITE), (200, 100))
            screen.blit(font.render("ESC to exit", True, WHITE), (200, 400))

            for i, result in enumerate(state["round_results"]):
                color = GREEN if result == "Hit!" else RED
                screen.blit(font.render(f"Round {i+1}: {result}", True, color), (200, 450 + i*30))

            if state["completed"]:
                if state["hits"] == 0:
                    final_msg = "Failed"
                elif state["hits"] in [1, 2]:
                    final_msg = "Try harder"
                elif state["hits"] in [3, 4]:
                    final_msg = "Almost there, try again"
                else:  # 5 hits
                    final_msg = "Issue Resolved"
                final_color = GREEN if state["success"] else RED
                screen.blit(font.render(final_msg, True, final_color), (200, 600))
                if not state["success"]:
                    screen.blit(font.render("Press SPACE to try again, ESC to exit", True, WHITE), (200, 650))
        except pygame.error as e:
            print(f"Font rendering error in overheating_mini_game: {e}")
            running = False

        if state["completed"] and state["success"]:
            running = False

        pygame.display.flip()
        clock.tick(60)

    if state["success"]:
        task_status["overheating"] = True
        print("Overheating: Task completed successfully")
    return state["success"]

def leak_repair_mini_game(cracks=None):
    def reset_task(cracks=None):
        if cracks is None:
            cracks = []
            for _ in range(5):
                start_x, start_y = random.randint(100, 1100), random.randint(100, 700)
                end_x, end_y = start_x + random.randint(-100, 100), start_y + random.randint(-100, 100)
                cracks.append(((start_x, start_y), (end_x, end_y)))
        return {
            "cracks": cracks,
            "player_paths": [],
            "current_path": [],
            "drawing": False,
            "success": False,
            "filled_cracks": 0,
            "current_crack": 0
        }

    state = reset_task(cracks)
    clock = pygame.time.Clock()
    running = True
    pygame.mouse.set_visible(False)

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not state["success"]:
                    state["drawing"] = True
                    state["current_path"] = [event.pos]
                    state["player_paths"].append(state["current_path"])
                    print("Leak Repair: Started drawing path")
            if event.type == pygame.MOUSEBUTTONUP:
                if not state["success"]:
                    state["drawing"] = False
                    crack_start, crack_end = state["cracks"][state["current_crack"]]
                    crack_covered = True
                    for t in range(0, 101, 10):
                        px = crack_start[0] + t/100 * (crack_end[0] - crack_start[0])
                        py = crack_start[1] + t/100 * (crack_end[1] - crack_start[1])
                        min_dist = float('inf')
                        for path in state["player_paths"]:
                            for p in path:
                                dist = math.hypot(px - p[0], py - p[1])
                                if dist < min_dist:
                                    min_dist = dist
                        if min_dist > 10:
                            crack_covered = False
                            break
                    if crack_covered:
                        state["filled_cracks"] += 1
                        state["current_crack"] += 1
                        print(f"Leak Repair: Crack covered, filled_cracks={state['filled_cracks']}")
                        if state["filled_cracks"] >= len(state["cracks"]):
                            state["success"] = True
                            print("Leak Repair: Success! All cracks filled")
                            pygame.time.wait(2000)
            if event.type == pygame.MOUSEMOTION:
                if state["drawing"] and not state["success"]:
                    state["current_path"].append(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE and not state["success"]:
                    state = reset_task(state["cracks"])
                    print("Leak Repair: Retrying with same cracks")

        # Draw cracks
        for i, (start, end) in enumerate(state["cracks"]):
            if i < state["filled_cracks"]:
                color = GREEN
            elif i == state["current_crack"]:
                color = RED
            else:
                color = (100, 0, 0)
            pygame.draw.line(screen, color, start, end, 3)

        # Draw player paths
        for path in state["player_paths"]:
            if len(path) > 1:
                pygame.draw.lines(screen, GREEN, False, path, 10)

        # Draw cellotape tool
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(screen, ORANGE, mouse_pos, 15)
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            dx = math.cos(rad) * 10
            dy = math.sin(rad) * 10
            pygame.draw.line(screen, BLACK, (mouse_pos[0] - dx, mouse_pos[1] - dy), (mouse_pos[0] + dx, mouse_pos[1] + dy), 2)

        # Labels
        try:
            screen.blit(font.render("TAPE", True, BLACK), (mouse_pos[0] - 10, mouse_pos[1] - 10))
            screen.blit(font.render(f"{state['filled_cracks']}/5", True, WHITE), (200, 50))
            screen.blit(font.render("Hold mouse button to apply tape, release to check, SPACE to retry, ESC to exit", True, WHITE), (200, 100))

            if state["success"]:
                screen.blit(font.render("Success! All leaks repaired.", True, GREEN), (200, 150))
                screen.blit(font.render("Press ESC to exit", True, WHITE), (200, 200))
        except pygame.error as e:
            print(f"Font rendering error in leak_repair_mini_game: {e}")
            running = False

        if state["success"]:
            running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.mouse.set_visible(True)
    if state["success"]:
        task_status["leak_repair"] = True
        return True, reset_task()  # New cracks for next run
    return False, state["cracks"]

def task_selection_screen():
    clock = pygame.time.Clock()
    running = True

    tasks = [
        ("Gas Mix", gas_mix_mini_game, pygame.Rect(300, 200, 200, 40)),
        ("Overheating", overheating_mini_game, pygame.Rect(300, 300, 200, 40)),
        ("Leak Repair", leak_repair_mini_game, pygame.Rect(300, 400, 200, 40))
    ]
    current_cracks = None

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for task_name, task_func, rect in tasks:
                    if rect.collidepoint(event.pos):
                        print(f"Starting task: {task_name}")
                        if task_name == "Leak Repair":
                            success, cracks = task_func() if current_cracks is None else task_func(current_cracks)
                            if not success:
                                current_cracks = cracks
                            else:
                                current_cracks = None
                        else:
                            success = task_func()
                            if success:
                                task_status[task_name.lower().replace(" ", "_")] = True
                        print(f"Task status: {task_status}")

        try:
            screen.blit(font.render("Oxygen System Tasks", True, WHITE), (300, 100))
            for i, (task_name, _, rect) in enumerate(tasks):
                checkbox_rect = pygame.Rect(250, 200 + i * 100, 30, 30)
                pygame.draw.rect(screen, WHITE, checkbox_rect, 2)
                if task_status[task_name.lower().replace(" ", "_")]:
                    pygame.draw.rect(screen, GREEN, (checkbox_rect.x + 5, checkbox_rect.y + 5, 20, 20))
                screen.blit(font.render(task_name, True, WHITE), (rect.x, rect.y))
            screen.blit(font.render("Click a task to start, ESC to exit", True, WHITE), (300, 500))
        except pygame.error as e:
            print(f"Font rendering error in task_selection_screen: {e}")
            running = False

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    task_selection_screen()