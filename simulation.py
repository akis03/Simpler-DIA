import random
import time
from environment import WarehouseEnvironment, EMPTY, SHELF, DELIVERY
from pathfinding import astar, bfs, greedy

#CONFIG
ALGO = bfs                                          #algorithm options to pick from- astar, bfs, greedy
NUM_AGENTS = 4                                      #number of agents during spawn
NUM_PACKAGES = 50                                   #needs to be <60 since the the total shelf quantity is 60
MAX_TICKS = 500
TICK_DELAY = 0.2                                    #how many seconds per tick
SHELF_CAP_SMALL = 10 
SHELF_CAP_LARGE = 5



def display(env, agents):
    #ascii print of warehouse
    for y in range(env.height):
        row = ""
        for x in range(env.width):
            if (y, x) == env.delivery_zone:
                row += "D"
            elif any(a["pos"] == (y, x) for a in agents):
                row += str(next(a["id"] for a in agents if a["pos"] == (y, x)))
            elif (y, x) in env.shelf_locations:
                row += "S"
            else:
                row += "."
        print(row)
    print()


def run():
    env = WarehouseEnvironment()
    assignment_tick = {}
    completion_tick = {}
    total_distance = 0
    delivered = 0
    delivered_by_size = {"S": 0, "L": 0}

    shelf_caps = {loc: {"S": SHELF_CAP_SMALL, "L": SHELF_CAP_LARGE}
                  for loc in env.shelf_locations}
    shelf_delivered = {loc: {"S": 0, "L": 0} for loc in env.shelf_locations}

    packages = [
        {"id": i, "loc": env.delivery_zone,
         "size": random.choice(["S", "L"]) }
        for i in range(NUM_PACKAGES)
    ]
    pending = packages.copy()

    agents = []
    for aid in range(NUM_AGENTS):
        while True:
            y = random.randrange(env.height)
            x = random.randrange(env.width)
            if env.grid[y, x] == EMPTY and (y, x) != env.delivery_zone:
                agents.append({"id": aid, "pos": (y, x), "state": "idle", "path": []})
                break

    for tick in range(MAX_TICKS):
        progress = False
        for a in agents:
            if a["state"] == "idle" and pending and delivered < NUM_PACKAGES:
                pkg = pending.pop(0)
                path1 = ALGO(a["pos"], pkg["loc"], env.grid)
                best_len = float('inf')
                best_shelf = None
                best_path2 = []
                for shelf in env.shelf_locations:
                    if shelf_caps[shelf][pkg["size"]] > 0:
                        path2 = ALGO(pkg["loc"], shelf, env.grid)
                        if path2 and len(path2) < best_len:
                            best_len = len(path2)
                            best_shelf = shelf
                            best_path2 = path2
                if path1 and best_path2:
                    a["path"] = path1 + best_path2[1:]
                    a["state"] = "moving"
                    a["pkg_id"] = pkg["id"]
                    a["pkg_size"] = pkg["size"]
                    a["shelf"] = best_shelf
                    shelf_caps[best_shelf][pkg["size"]] -= 1
                    assignment_tick[pkg["id"]] = tick
                    progress = True

        for a in agents:
            if a["state"] == "moving":
                new_pos = a["path"].pop(0)
                if new_pos != a["pos"]:
                    total_distance += 1
                a["pos"] = new_pos
                progress = True
                if not a["path"]:
                    a["state"] = "idle"
                    completion_tick[a["pkg_id"]] = tick
                    delivered += 1
                    delivered_by_size[a["pkg_size"]] += 1
                    shelf_delivered[a["shelf"]][a["pkg_size"]] += 1

        print(f"Tick {tick}: delivered {delivered}/{NUM_PACKAGES}, dist={total_distance}")
        display(env, agents)
        time.sleep(TICK_DELAY)

        if delivered >= NUM_PACKAGES:
            print("All packages delivered!")
            break
        if not progress:
            print("Stalled: no further progress possible.")
            break

    initial_small = sum(1 for pkg in packages if pkg["size"] == "S")
    initial_large = sum(1 for pkg in packages if pkg["size"] == "L")

    if completion_tick:
        avg_time = sum(
            completion_tick[i] - assignment_tick[i]
            for i in completion_tick
        ) / len(completion_tick)
    else:
        avg_time = 0

    summary = {
        'initial_small': initial_small,
        'initial_large': initial_large,
        'tasks_completed': delivered,
        'total_distance': total_distance,
        'average_putaway_time': avg_time,
        'small_delivered': delivered_by_size['S'],
        'large_delivered': delivered_by_size['L']
    }
    print("Final metrics:", summary)

    #TLS: Top Left Shelf, TRS: Top Right Shelf, BLS: Bottom Left Shelf, BRS: Bottom Right Shelf.
    labels = ['TLS', 'TRS', 'BLS', 'BRS']
    tls, trs, bls, brs = env.shelf_locations
    metrics = {
        'TLS': shelf_delivered[tls],
        'TRS': shelf_delivered[trs],
        'BLS': shelf_delivered[bls],
        'BRS': shelf_delivered[brs],
    }
    
    print(f"{labels[0]} - L:{metrics['TLS']['L']}/{SHELF_CAP_LARGE} | S:{metrics['TLS']['S']}/{SHELF_CAP_SMALL}   "
          f"{labels[1]} - L:{metrics['TRS']['L']}/{SHELF_CAP_LARGE} | S:{metrics['TRS']['S']}/{SHELF_CAP_SMALL}")
    
    print(f"{labels[2]} - L:{metrics['BLS']['L']}/{SHELF_CAP_LARGE} | S:{metrics['BLS']['S']}/{SHELF_CAP_SMALL}   "
          f"{labels[3]} - L:{metrics['BRS']['L']}/{SHELF_CAP_LARGE} | S:{metrics['BRS']['S']}/{SHELF_CAP_SMALL}")

if __name__ == "__main__":
    run()
