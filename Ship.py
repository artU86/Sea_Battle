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