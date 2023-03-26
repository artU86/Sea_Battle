from random import randint as rnt, choice
from copy import deepcopy as dc
from Ship import Ship, Descriptor


class DefenderShipError(Exception):
    pass


class GamePole:
    size = Descriptor()
    ships = Descriptor()

    def __init__(self, size):
        self.open_cells = []
        self.killed_ships = []
        self.closed_cells = set()  #TODO почему тут множество?
        self.size = size
        self.ships = []

    def init(self):
        self.ships = (Ship(4, rnt(1, 2)),
                      *(Ship(3, rnt(1, 2)) for i in range(2)),
                      *(Ship(2, rnt(1, 2)) for i in range(3)),
                      *(Ship(1, rnt(1, 2)) for i in range(4)))

        for ship in self.ships:
            flag = False
            with DefenderShip(ship) as def_ship:
                while not flag:
                    try:
                        x, y = rnt(0, self.size - 1), rnt(0, self.size - 1)
                        def_ship.set_start_coords(x, y)
                        self.check_ship(ship, def_ship)
                        flag = True
                    except DefenderShipError:
                        continue

        for ship in self.ships:
            ship.set_cells()

    def show_pole(self):
        [print(*line, sep=' ') for line in self.get_pole()]

    def get_ships(self):
        return self.ships

    def get_pole(self, closed=False):
        pole = [[0 for i in range(self.size)] for j in range(self.size)]

        for ship in self.ships:
            for cell in ship:
                x, y = cell
                pole[y][x] = (0 if closed else 1) if ship.cells[(x, y)] else 'x'

        for ship in self.killed_ships:
            cells = list(ship.cells)
            x_min, y_min = cells[0]
            x_max, y_max = cells[-1]
            res = [(p, q) for p in range(max(0, x_min - 1), min(self.size, x_max + 2))
                   for q in range(max(0, y_min - 1), min(self.size, y_max + 2))
                   ]
            for cell in res:
                x, y = cell
                if cell not in ship:
                    pole[y][x] = '*'
                    self.closed_cells.add((x, y))

        for cell in self.open_cells:
            x, y = cell
            pole[y][x] = '*'

        return pole

    def move_ships(self):
        for ship in self.ships:
            step = choice((-1, 1))
            with DefenderShip(ship) as def_ship:
                try:
                    def_ship.move(step)
                    self.check_ship(ship, def_ship)
                except DefenderShipError:
                    try:
                        def_ship.move(-step)
                        self.check_ship(ship, def_ship)
                    except DefenderShipError:
                        continue

    def check_ship(self, ship, def_ship):
        for other_ship in self.ships:
            if ship is other_ship:
                continue
            if def_ship.is_collide(other_ship):
                raise DefenderShipError
            if def_ship.is_out_pole(self.size):
                raise DefenderShipError

    def has_ships(self):
        return any(map(lambda x: any(x.cells.values()), self))

    def __iter__(self):
        yield from self.ships


class DefenderShip:
    def __init__(self, ship):
        self.ship = ship

    def __enter__(self):
        self.def_ship = dc(self.ship)
        return self.def_ship

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.ship.x, self.ship.y = self.def_ship.get_start_coords()
        return False
