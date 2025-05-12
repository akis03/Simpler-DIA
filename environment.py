import numpy as np
EMPTY, SHELF, DELIVERY = 0, 1, 2

class WarehouseEnvironment:
    def __init__(self,
                 width: int = 10,
                 height: int = 10,
                 shelf_locations: list[tuple[int,int]] = None,
                 delivery_zone: tuple[int,int] = (0, 0)):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)

        self.shelf_locations = shelf_locations or [(2,2), (2,7), (7,2), (7,7)]
        for (y, x) in self.shelf_locations:
            self.grid[y, x] = SHELF

        self.delivery_zone = delivery_zone
        self.grid[delivery_zone] = DELIVERY

    def display_ascii(self):
        symbol = {EMPTY: '.', SHELF: 'S', DELIVERY: 'D'}
        for y in range(self.height):
            print(' '.join(symbol[self.grid[y, x]] for x in range(self.width)))
        print()

#test run main
if __name__ == '__main__':
    env = WarehouseEnvironment()
    print("Warehouse layout:")
    env.display_ascii()
