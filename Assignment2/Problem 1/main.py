"""
Complete A* pathfinding playground in one file.

Controls:
  - Left click: toggle wall
  - Right click: set start
  - Middle click: set goal
  - Space: run A*
  - C: toggle costs
  - ESC: quit
"""

import math
import sys
import heapq
import pygame

# --------------------------
# Frog class


class Frog:
    def __init__(self, start_cell):
        self.speed = 200  # pixels per second
        self.radius = 8

        self.pos = self.cell_center(start_cell)
        self.path = []
        self.index = 0

    def cell_center(self, cell):
        r, c = cell
        return pygame.Vector2(
            c * CELL_SIZE + CELL_SIZE / 2,
            r * CELL_SIZE + CELL_SIZE / 2
        )

    def set_path(self, path):
        if not path:
            self.path = []
            self.index = 0
            return

        self.path = [self.cell_center(c) for c in path]
        self.index = 0

    def update(self, dt):
        if self.index >= len(self.path):
            return

        target = self.path[self.index]
        direction = target - self.pos
        dist = direction.length()

        if dist < 2:
            self.index += 1
            return

        direction.normalize_ip()
        self.pos += direction * self.speed * dt

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            (60, 160, 60),
            self.pos,
            self.radius
        )


# --------------------------
# Grid and window settings
# --------------------------
ROWS = 30
COLS = 40
CELL_SIZE = 30

WINDOW_WIDTH = COLS * CELL_SIZE
WINDOW_HEIGHT = ROWS * CELL_SIZE

# --------------------------
# Colors (paper-white theme)
# --------------------------

COLOR_BG = (245, 245, 245)
COLOR_GRID = (200, 200, 200)
COLOR_WALL = (30, 30, 30)
COLOR_START = (80, 160, 255)
COLOR_GOAL = (60, 120, 220)
COLOR_OPEN = (120, 190, 210)   # cool cyan-blue
COLOR_CLOSED = (230, 90, 90)
COLOR_PATH = (80, 200, 120)  # soft green for path as requirement
COLOR_COST_TEXT = (40, 40, 40)
COLOR_COST_BG = (255, 255, 255)
COLOR_TEXT = (60, 60, 60)

# --------------------------
# Global A* state
# --------------------------

astar_generator = None
astar_running = False
show_costs = False
search_finished = False
draw_path_lines = False
debug_mode = False

path_length = 0
path_distance = 0.0
nodes_explored = 0

start = (5, 5)
goal = (20, 30)

frog = Frog(start)
walls = set()

current_path = None
current_closed = set()
current_open = set()

current_g = {}
current_h = {}
current_f = {}

# --------------------------
# Helper functions
# --------------------------


def interrupt_and_reset():
    global astar_generator, astar_running
    astar_generator = None
    astar_running = False
    frog.path = []
    frog.index = 0


def cell_from_mouse(pos):
    x, y = pos
    c = x // CELL_SIZE
    r = y // CELL_SIZE
    if 0 <= r < ROWS and 0 <= c < COLS:
        return (r, c)
    return None


def draw_grid(surface):
    # Base cells
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(
                c * CELL_SIZE,
                r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            pygame.draw.rect(surface, COLOR_BG, rect)

            if (r, c) in walls:
                pygame.draw.rect(surface, COLOR_WALL, rect)

    # Closed set
    for (r, c) in current_closed:
        rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, COLOR_CLOSED, rect)

    # Open set (outline)
    for (r, c) in current_open:
        rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, COLOR_OPEN, rect)
        pygame.draw.rect(surface, COLOR_GRID, rect, 1)

    # Path
    if current_path:
        if draw_path_lines:
            points = []
            for (r, c) in current_path:
                points.append((
                    c * CELL_SIZE + CELL_SIZE // 2,
                    r * CELL_SIZE + CELL_SIZE // 2
                ))

            if len(points) >= 2:
                pygame.draw.lines(
                    surface,
                    COLOR_PATH,
                    False,
                    points,
                    4
                )
        else:
            for (r, c) in current_path:
                rect = pygame.Rect(
                    c * CELL_SIZE,
                    r * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(surface, COLOR_PATH, rect)

    # Start & Goal
    sr, sc = start
    gr, gc = goal

    pygame.draw.rect(
        surface,
        COLOR_START,
        pygame.Rect(sc * CELL_SIZE, sr * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )

    pygame.draw.rect(
        surface,
        COLOR_GOAL,
        pygame.Rect(gc * CELL_SIZE, gr * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )

    # Costs
    if show_costs:
        for (r, c), f in current_f.items():
            if (r, c) in walls or (r, c) in (start, goal):
                continue

            text = cost_font.render(f"{f:.1f}", True, COLOR_COST_TEXT)
            rect = text.get_rect(
                center=(c * CELL_SIZE + CELL_SIZE // 2,
                        r * CELL_SIZE + CELL_SIZE // 2)
            )

            bg = rect.inflate(6, 4)
            pygame.draw.rect(surface, COLOR_COST_BG, bg, border_radius=4)
            surface.blit(text, rect)

    # Grid lines (always last)
    for c in range(COLS + 1):
        x = c * CELL_SIZE
        pygame.draw.line(
            surface,
            COLOR_GRID,
            (x, 0),
            (x, ROWS * CELL_SIZE)
        )

    for r in range(ROWS + 1):
        y = r * CELL_SIZE
        pygame.draw.line(
            surface,
            COLOR_GRID,
            (0, y),
            (COLS * CELL_SIZE, y)
        )


# --------------------------
# A* helpers
# --------------------------

def heuristic(a, b):
    r1, c1 = a
    r2, c2 = b

    dx = abs(c1 - c2)
    dy = abs(r1 - r2)

    # return dx + dy  # Manhattan distance
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy) # Octile distance
    # return math.hypot(c1 - c2, r1 - r2)  # Euclidean distance


def get_neighbors(cell):
    r, c = cell
    neighbors = []

    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (1, -1), (-1, 1), (-1, -1), (1, 1)
    ]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            if (nr, nc) not in walls:
                cost = 1 if dr == 0 or dc == 0 else math.sqrt(2)
                neighbors.append(((nr, nc), cost))

    return neighbors


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def astar_stepper():
    global current_path, current_closed, current_open
    global current_g, current_h, current_f
    global search_finished, path_length, path_distance, nodes_explored

    if start in walls or goal in walls:
        return

    open_heap = []
    heapq.heappush(open_heap, (0, start))

    open_set = {start}
    closed_set = set()

    g_score = {start: 0} # Cost from start to current
    h_score = {start: heuristic(start, goal)} # Heuristic cost to goal
    f_score = {start: h_score[start]} # Total cost

    current_g = g_score.copy()
    current_h = h_score.copy()
    current_f = f_score.copy()
    current_open = {start}

    came_from = {}

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current not in open_set:
            continue

        open_set.remove(current)
        current_open.discard(current)
        closed_set.add(current)
        current_closed = closed_set.copy()

        if current == goal:
            current_path = reconstruct_path(came_from, current)

            frog.pos = frog.cell_center(start)
            frog.set_path(current_path)

            search_finished = True
            path_length = len(current_path)
            path_distance = g_score[current]
            nodes_explored = len(closed_set)
            return

        for neighbor, cost in get_neighbors(current):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + cost
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                h = heuristic(neighbor, goal)
                f = tentative_g + h

                current_g[neighbor] = tentative_g
                current_h[neighbor] = h
                current_f[neighbor] = f

                if neighbor not in open_set:
                    heapq.heappush(open_heap, (f, neighbor))
                    open_set.add(neighbor)
                    current_open.add(neighbor)

        yield

    search_finished = True


# --------------------------
# Main loop
# --------------------------

def main():
    global astar_generator, astar_running, show_costs, cost_font
    global start, goal, frog, walls, draw_path_lines, current_path, debug_mode

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("A* Pathfinding")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    cost_font = pygame.font.SysFont("consolas", 10, bold=True)

    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE and debug_mode:
                    astar_generator = astar_stepper()
                    astar_running = True
                if event.key == pygame.K_c:
                    show_costs = not show_costs
                if event.key == pygame.K_p:
                    draw_path_lines = not draw_path_lines
                if event.key == pygame.K_d:
                    debug_mode = not debug_mode 

            if event.type == pygame.MOUSEBUTTONDOWN:
                cell = cell_from_mouse(pygame.mouse.get_pos())
                if not cell:
                    continue

                if event.button == 1 and cell not in (start, goal):
                    walls.symmetric_difference_update({cell})
                    reset_search()

                elif event.button == 3 and cell != goal:
                    goal = cell

                    interrupt_and_reset()
                    reset_search()

                    if not debug_mode:
                        astar_generator = astar_stepper()
                        astar_running = True

                elif event.button == 2:
                    start = cell

                    interrupt_and_reset()
                    reset_search()

                    frog.pos = frog.cell_center(start)


        if astar_running and astar_generator:
            try:
                next(astar_generator)
            except StopIteration:
                astar_running = False

        frog.update(dt)

        screen.fill(COLOR_BG)
        draw_grid(screen)
        frog.draw(screen)

        help_text = (
            "leftClick:wall |rightClick:goal |middleClick:start |D:Switch mode  "
            "SPACE:run A* |P: show path |C: costs |ESC: quit"
        )
        screen.blit(font.render(help_text, True, COLOR_TEXT),
                    (10, WINDOW_HEIGHT - 24))

        mode_text = "DEBUG MODE" if debug_mode else "NORMAL MODE"
        screen.blit(font.render(mode_text, True, COLOR_TEXT), (10, 10))

        if search_finished and current_path:
            result_text = (
                f"Nodes expanded: {nodes_explored}   "
                f"Path length: {path_length}   "
                f"Path cost: {path_distance:.2f}"
            )

            screen.blit(
                font.render(result_text, True, COLOR_TEXT),
                (10, WINDOW_HEIGHT - 48)
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def reset_search():
    global current_path, current_closed, current_open
    global current_g, current_h, current_f
    global search_finished, astar_running, astar_generator
    global path_length, path_distance, nodes_explored

    path_length = 0
    path_distance = 0.0
    nodes_explored = 0

    search_finished = False
    astar_running = False
    astar_generator = None

    current_path = None
    current_closed.clear()
    current_open.clear()
    current_g.clear()
    current_h.clear()
    current_f.clear()


if __name__ == "__main__":
    main()
