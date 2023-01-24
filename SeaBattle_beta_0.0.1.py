from random import randint as rnt, choice
from copy import deepcopy as dc


class DefenderShipError(Exception):
    pass


class Descriptor:
    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        setattr(instance, self.name, value)


class Ship:
    x = Descriptor()
    y = Descriptor()
    length = Descriptor()
    tp = Descriptor()
    is_move = Descriptor()
    cells = Descriptor()

    def __init__(self, length, tp=1, x=None, y=None):
        self.length = length
        self.tp = tp
        self.x = x
        self.y = y
        self.is_move = True
        self.cells = {}

    def set_cells(self):
        if self.tp == 1:
            coords = [(x, self.y) for x in range(self.x, self.x + self.length)]
        else:
            coords = [(self.x, y) for y in range(self.y, self.y + self.length)]
        self.cells = {coord: True for coord in coords}

    def set_start_coords(self, x, y):
        self.x = x
        self.y = y

    def get_start_coords(self):
        return self.x, self.y

    def move(self, go):
        if not self.is_move:
            return None
        if self.tp == 1:
            self.x += go
        else:
            self.y += go

    def is_collide(self, ship):
        if ship.x is None:
            return False

        params = ('x', 'y', 'width', 'height')
        rect1 = dict(zip(params, self.get_rect_params(self)))
        rect2 = dict(zip(params, self.get_rect_params(ship, False)))

        cross_y = (rect1['y'] - 1 + rect1['height'] >= rect2['y']) if rect1['y'] <= rect2['y'] else \
            rect2['y'] - 1 + rect2['height'] >= rect1['y']

        cross_x = (rect1['x'] - 1 + rect1['width'] >= rect2['x']) if rect1['x'] <= rect2['x'] else \
            rect2['x'] - 1 + rect2['width'] >= rect1['x']

        return all((cross_x, cross_y))

    @staticmethod
    def get_rect_params(ship, rect=True):
        if rect:
            x = ship.x - 1
            y = ship.y - 1
            width = 3 if ship.tp == 2 else ship.length + 2
            height = 3 if ship.tp == 1 else ship.length + 2
            return x, y, width, height
        x = ship.x
        y = ship.y
        width = 1 if ship.tp == 2 else ship.length
        height = 1 if ship.tp == 1 else ship.length
        return x, y, width, height

    def is_out_pole(self, size):
        a = self.x >= 0
        b = self.y >= 0
        count_top = self.x if self.tp == 1 else self.y
        c = count_top + self.length - 1 <= size - 1
        res = all((a, b, c))
        return not res

    def check_index(self, indx):
        if indx not in range(self.length):
            raise IndexError('неверный индекс палубы')
        return self.cells[indx]

    def __getitem__(self, item):
        return self.check_index(item)

    def __setitem__(self, key, value):
        self.check_index(key)
        self.cells[key] = value

    def __repr__(self):
        return f'{"горизонтально" if self.tp == 1 else "вертикально"} x={self.x}, y={self.y}, length={self.length}'

    def __iter__(self):
        yield from self.cells


class GamePole:
    size = Descriptor()
    ships = Descriptor()

    def __init__(self, size):
        self.open_cells = []
        self.killed_ships = []
        self.closed_cells = set()
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


class SeaBattle:
    def __init__(self, size):
        self.around = False
        self.along = False
        self.front = True
        self.win = False
        self.size = size
        self.human_turn = choice((True, False))
        self.player1_pole = GamePole(size)
        self.player2_pole = GamePole(size)
        self.coords_to_find_ship = (0, 0)
        self.player1_pole.init()
        self.player2_pole.init()

    def human_move(self):
        x, y = map(int, input().split())
        if (x, y) in self.player2_pole.closed_cells:
            print('В эту клетку нельзя бить, выберите другую')
            return
        res = self.get_shoot(self.player2_pole, x, y)

        self.player2_pole.closed_cells.add((x, y))
        if not res:
            self.player2_pole.open_cells.append((x, y))

        self.human_turn = bool(res)
        if res == 1:
            self.killed_ship_handler(x, y, self.player2_pole)

    def random_shoot(self):
        x, y = rnt(0, self.size - 1), rnt(0, self.size - 1)
        while (x, y) in self.player1_pole.closed_cells:
            x, y = rnt(0, self.size - 1), rnt(0, self.size - 1)
        res = self.get_shoot(self.player1_pole, x, y)
        if not res:
            self.player1_pole.closed_cells.add((x, y))

        self.human_turn = not bool(res)
        self.player1_pole.closed_cells.add((x, y))

        if not res:
            self.player1_pole.open_cells.append((x, y))

        if res == 2:
            self.start_cell = [x, y]
            self.current_cell = [x, y]
            vector_x = range(max(0, x - 1), min(self.size, x + 2))
            vector_y = range(max(0, y - 1), min(self.size, y + 2))
            x_cells = [(i, y) for i in vector_x if i != x]
            y_cells = [(x, i) for i in vector_y if i != y]
            cells_to_shoot = x_cells + y_cells
            self.cells_to_shoot = list(filter(lambda cell: cell not in self.player1_pole.closed_cells, cells_to_shoot))
            self.around = True
            self.coords_to_find_ship = (x, y)
        if res == 1:
            self.killed_ship_handler(x, y, self.player1_pole)

    def find_around(self):
        x1, y1 = self.cells_to_shoot.pop(rnt(0, len(self.cells_to_shoot) - 1))
        res = self.get_shoot(self.player1_pole, x1, y1)

        self.player1_pole.closed_cells.add((x1, y1))
        if not res:
            self.player1_pole.open_cells.append((x1, y1))
            self.human_turn = True

        if res == 1:
            self.killed_ship_handler(x1, y1, self.player1_pole)
            self.around = False

        if res == 2:
            self.main_axis = 'x' if x1 == self.start_cell[0] else 'y'
            self.current_cell = (x1, y1)
            self.around = False
            self.along = True
            if x1 < self.start_cell[0] or y1 < self.start_cell[1]:
                self.front = False

    def find_along(self):
        coords = self.next_coords()
        x1, y1 = coords if coords else self.next_coords()
        res = self.get_shoot(self.player1_pole, x1, y1)

        self.player1_pole.closed_cells.add((x1, y1))

        if not res:
            self.player1_pole.open_cells.append((x1, y1))
            self.front = False
            self.human_turn = True
            self.current_cell = self.start_cell

        if res == 1:
            self.killed_ship_handler(x1, y1, self.player1_pole)
            self.front = True
            self.along = False

        if res == 2:
            self.current_cell = [x1, y1]

    def killed_ship_handler(self, x, y, pole):
        ship = self.get_ship(pole, y, x)
        pole.killed_ships.append(ship)
        self.win = self.check_win()

    def computer_move(self):
        if self.around:
            self.find_around()

        elif self.along:
            self.find_along()

        else:
            self.random_shoot()

    def get_shoot(self, pole, x, y):
        cell = pole.get_pole()[y][x]
        if not cell:
            return 0
        ship = self.get_ship(pole, y, x)
        ship.cells[(x, y)] = False
        if not any(ship.cells.values()):
            return 1
        return 2

    def get_ship(self, pole, y, x):
        for ship in pole.ships:
            if (x, y) in ship:
                return ship

    def check_win(self):
        return not all((self.player1_pole.has_ships(), self.player2_pole.has_ships()))

    def next_coords(self):
        x1, y1 = self.current_cell

        if self.main_axis != 'x':
            if x1 < self.size - 1 and self.front is True:
                x1 = x1 + 1 if x1 > self.start_cell[0] else self.start_cell[0] + 1
            else:
                x1 = x1 - 1 if x1 < self.start_cell[0] else self.start_cell[0] - 1
        else:
            if y1 < self.size - 1 and self.front is True:
                y1 = y1 + 1 if y1 > self.start_cell[1] else self.start_cell[1] + 1
            else:
                y1 = y1 - 1 if y1 < self.start_cell[1] else self.start_cell[1] - 1

        if (x1, y1) in self.player1_pole.closed_cells or (x1, y1) in self.player1_pole.open_cells:
            self.front = not self.front
            self.current_cell = self.start_cell
            return False
        return x1, y1

    def show_poles(self):
        lines1 = self.player1_pole.get_pole()
        lines2 = self.player2_pole.get_pole(closed=True)
        print('human pole', 'machine pole', sep='                    ')
        print()
        for i in range(self.size):
            print(*lines1[i], end="     |     ")
            print(*lines2[i])
        print()

    def main(self):
        print('                 start game')
        self.show_poles()
        while not self.win:
            print(f'{["                              machine", "human"][self.human_turn]} turn')

            if self.human_turn:
                self.human_move()
            else:
                self.computer_move()

            self.show_poles()
        print()
        print(f'{["                              machine", "human"][self.human_turn]} win!')


battle = SeaBattle(10)
battle.main()
