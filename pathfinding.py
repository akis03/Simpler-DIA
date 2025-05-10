# pathfinding.py

from collections import deque
import heapq
from typing import Tuple, List

Position = Tuple[int, int]

def bfs(start: Position, goal: Position, grid) -> List[Position]:
    """
    Breadth-first search on a 2D grid.
    Allows stepping onto goal even if it's marked as a shelf.
    Returns a list of positions from start to goal (inclusive), or [] if no path.
    """
    queue = deque([(start, [start])])
    visited = {start}
    h, w = len(grid), len(grid[0])
    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path
        y, x = current
        for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
            ny, nx = y + dy, x + dx
            neighbor = (ny, nx)
            # bounds check
            if not (0 <= ny < h and 0 <= nx < w):
                continue
            # obstacle check: shelves (1), allow goal
            if grid[ny][nx] == 1 and neighbor != goal:
                continue
            if neighbor in visited:
                continue
            visited.add(neighbor)
            queue.append((neighbor, path + [neighbor]))
    return []


def astar(start: Position, goal: Position, grid) -> List[Position]:
    """
    A* pathfinding using Manhattan heuristic.
    Allows stepping onto goal even if it's a shelf.
    Returns a list of positions from start to goal (inclusive), or [] if no path.
    """
    def heuristic(a: Position, b: Position) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    h, w = len(grid), len(grid[0])
    open_set = []  # heap of tuples (f_score, g_score, position, path)
    heapq.heappush(open_set, (heuristic(start, goal), 0, start, [start]))
    closed = set()

    while open_set:
        f_score, g_score, current, path = heapq.heappop(open_set)
        if current == goal:
            return path
        if current in closed:
            continue
        closed.add(current)

        y, x = current
        for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
            ny, nx = y + dy, x + dx
            neighbor = (ny, nx)
            # bounds check
            if not (0 <= ny < h and 0 <= nx < w):
                continue
            # obstacle check
            if grid[ny][nx] == 1 and neighbor != goal:
                continue
            if neighbor in closed:
                continue
            new_g = g_score + 1
            new_f = new_g + heuristic(neighbor, goal)
            heapq.heappush(open_set, (new_f, new_g, neighbor, path + [neighbor]))
    return []


def greedy(start: Position, goal: Position, grid) -> List[Position]:
    """
    Greedy best-first search with Manhattan heuristic.
    Chooses at each step the neighbor closest to goal.
    Not guaranteed optimal.
    """
    def heuristic(a: Position, b: Position) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    h, w = len(grid), len(grid[0])
    current = start
    path = [current]
    visited = {current}

    while current != goal:
        y, x = current
        neighbors = []
        for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
            ny, nx = y + dy, x + dx
            neighbor = (ny, nx)
            # bounds and obstacle check
            if not (0 <= ny < h and 0 <= nx < w):
                continue
            if grid[ny][nx] == 1 and neighbor != goal:
                continue
            if neighbor in visited:
                continue
            neighbors.append(neighbor)
        if not neighbors:
            return []
        # choose neighbor with smallest heuristic
        current = min(neighbors, key=lambda n: heuristic(n, goal))
        visited.add(current)
        path.append(current)
    return path
