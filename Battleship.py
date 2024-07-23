from random import randint


# Исключения

class GameException(Exception):
    pass


class BoardOutException(GameException):
    def __str__(self):
        return 'Эти координаты отсутствуют на поле! Попробуйте снова.'


class BoardUsedException(GameException):
    def __str__(self):
        return 'Вы уже стреляли по этим координатам! Попробуйте снова.'


class BoardWrongShipException(GameException):
    pass


# Внутренняя логика

class Dot:
    empty = 'О'
    ship = '■'
    damage = 'X'
    missed = 'T'

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, bow_dot, size, direction):
        self.size = size
        self.hp = size
        self.bow_dot = bow_dot
        self.direction = direction

    HORIZONTAL = 0
    VERTICAL = 1

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.size):
            ship_x = self.bow_dot.x
            ship_y = self.bow_dot.y
            if self.direction == 0:
                ship_x += i
            elif self.direction == 1:
                ship_y += i
            ship_dots.append(Dot(ship_x, ship_y))
        return ship_dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [[Dot.empty] * size for _ in range(size)]
        self.busy_cells = []
        self.ships = []

    def __str__(self):
        coordinates = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            coordinates += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hid:
            coordinates = coordinates.replace(Dot.ship, Dot.empty)
        return coordinates

    def out(self, point):
        return not ((0 <= point.x < self.size) and (0 <= point.y < self.size))

    def contour(self, ship, verb=False):
        perimeter = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1), (0, 0), (0, 1),
                     (1, -1), (1, 0), (1, 1)]
        for i in ship.dots:
            for i_x, i_y in perimeter:
                cur = Dot(i.x + i_x, i.y + i_y)
                if not (self.out(cur)) and cur not in self.busy_cells:
                    if verb:
                        self.field[cur.x][cur.y] = Dot.missed
                    self.busy_cells.append(cur)

    def add_ship(self, ship):
        for point in ship.dots:
            if self.out(point) or point in self.busy_cells:
                raise BoardWrongShipException()
        for point in ship.dots:
            self.field[point.x][point.y] = Dot.ship
            self.busy_cells.append(point)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, point):
        if self.out(point):
            raise BoardOutException()
        if point in self.busy_cells:
            raise BoardUsedException()
        self.busy_cells.append(point)

        for ship in self.ships:
            if point in ship.dots:
                ship.hp -= 1
                self.field[point.x][point.y] = Dot.damage
                if ship.hp == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен!')
                    return True

        self.field[point.x][point.y] = Dot.missed
        print('Промах!')
        return False

    def begin(self):
        self.busy_cells = []


# ВНЕШНЯЯ ЛОГИКА ИГРЫ

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except GameException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход ИИ: {d.x+1} {d.y+1}')
        return d


class User(Player):
    def ask(self):
        while True:
            x_shot = input('Введите номер строки: ')
            y_shot = input('Введите номер столбца: ')

            if not (x_shot.isdigit()) or not (y_shot.isdigit()):
                print('Неверное значение! Введите число от 1 до 6.')
                continue

            x, y = int(x_shot), int(y_shot)

            return Dot(x - 1, y - 1)


class Game:

    def random_board(self):
        ship_types = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        try_counts = 0
        for i in ship_types:
            while True:
                try_counts += 1
                if try_counts > 3000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def new_board(self):
        board = None
        while board is None:
            board = self.random_board()
        return board

    def __init__(self, size=6):
        self.size = size
        user = self.new_board()
        ai = self.new_board()
        ai.hid = True

        self.ai = AI(ai, user)
        self.user = User(user, ai)

    def greet(self):
        print('Приветствую! Перед вами игра "Морской Бой"!')
        print()
        print('Это игра для одного игрока, в которой он соревнуется с компьютером!')
        print('В начале игры на поле случайным образом расставляются корабли.')
        print('Цель игры: потопить вражеские корабли раньше, чем это сделает противник.')
        print('Чтобы совершить выстрел, игрок должен ввести сначала номер строки, затем номер столбца.')
        print('Значения вводятся от 1 до 6.')
        print()
        print('Удачи, капитан!')

    def print_boards(self):
        print('-' * 27)
        print('Ваша доска:')
        print(self.user.board)
        print('-' * 27)
        print('Доска ИИ:')
        print(self.ai.board)
        print('-' * 27)

    def loop(self):
        turn_count = 0
        while True:
            self.print_boards()
            if turn_count % 2 == 0:
                print('Ваш ход!')
                repeat = self.user.move()
            else:
                print('Ходит ИИ!')
                repeat = self.ai.move()
            if repeat:
                turn_count -= 1

            if self.ai.board.count == 7:
                self.print_boards()
                print('-' * 27)
                print('Вы выиграли!')
                break

            if self.user.board.count == 7:
                self.print_boards()
                print('-' * 27)
                print('ИИ выиграл!')
                break
            turn_count += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
