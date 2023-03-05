from GamePole import * # знаю что импорт через звездочку это плохо) но делаю именно так т.к. точно знаю что у меня
                       # импортируется через эту звездочку


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
        print('human pole', 'machine pole', sep='                    ', end='\n\n')
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
try:
    battle.main()
except AttributeError:
    print(f'around = {battle.around}, along = {battle.along}, front = {battle.front}', sep='\n')

