class Field:
    def __init__(self, x=None, y=None, visited=False, knight_on=False):
        self.x = x
        self.y = y
        self.visited = visited
        self.knight_on = knight_on
        self.num_of_possibilities = 0
        self.path_position = 0

    def visit(self):
        self.visited = True

    def place_knight(self):
        self.knight_on = True

    def remove_knight(self):
        self.knight_on = False

    @classmethod
    def copy(cls, field):
        return cls(field.x, field.y, field.visited, field.knight_on)

    def __str__(self):
        return "X" if self.knight_on else "_"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Game:
    def __init__(self, no_rows=8, no_cols=8, start_pos=None):
        self.rows = no_rows
        self.cols = no_cols
        self.start_pos = start_pos
        self.placeholder = None
        self.board = None
        self.knight_pos = None
        self.possible_moves = None
        self.path = []

    def set_board(self):
        cols, rows = [int(num.strip(" ,")) for num in input("Enter your board dimensions: ").split()]
        if cols <= 0 or rows <= 0:
            raise ValueError
        self.cols = cols
        self.rows = rows
        self.board = [[Field(i, j + 1) for j in range(cols)] for i in range(rows, 0, -1)]
        self.placeholder = "_" * len(str(cols * rows))

    def set_start_position(self, x=None, y=None):
        if not (x and y):
            y, x = [int(num.strip(" ,")) for num in input("Enter the knight's starting position: ").split()]
        if not 1 <= x <= self.rows or not 1 <= y <= self.cols:
            raise ValueError
        self.start_pos = self.board[self.rows - x][y - 1]
        self.place_knight(self.start_pos)

    def place_knight(self, field):
        if self.knight_pos:
            self.knight_pos.remove_knight()
        field.visit()
        field.place_knight()
        field.path_position = len(self.path) + 1
        self.path.append(field)
        self.knight_pos = field
        self.possible_moves = self.find_possible_moves(self.knight_pos)

    def possible_field(self, row, column):
        return 0 <= row < self.rows and 0 <= column < self.cols and not self.board[row][column].visited

    def find_possible_moves(self, for_field, stop=False):
        possibilities = []
        for a in [2, -2]:
            for b in [1, -1]:
                for pair in [(a, b), (b, a)]:
                    row = self.rows - (for_field.x + pair[0])
                    column = for_field.y + pair[1] - 1
                    if self.possible_field(row, column):
                        field = self.board[row][column]
                        if not stop:
                            field.num_of_possibilities = len(self.find_possible_moves(field, stop=True))
                        possibilities.append(field)
        return possibilities

    def play(self):
        while True:
            try:
                self.set_board()
                break
            except ValueError:
                print("Invalid dimensions!")
        while True:
            try:
                self.set_start_position()
                break
            except ValueError:
                print("Invalid dimensions!")
        while True:
            answer = input("Do you want to try the puzzle? (y/n): ")
            if answer not in "yn":
                print("Invalid option!")
                continue
            if not self.find_solution():
                print("No solution exists!")
                return
            if answer == "y":
                self.restart_board()
                print(self)
                moves = 1
                while bool(self.possible_moves):
                    try:
                        self.make_a_move()
                        print(self)
                        moves += 1
                    except ValueError:
                        print("Invalid move!", end=" ")
                if self.all_visited():
                    print("What a great tour! Congratulations!")
                else:
                    print("No more possible moves!")
                    print(f"Your knight visited {moves} squares!")
            elif answer == "n":
                self.print_positions()
            break

    def make_a_move(self):
        y, x = [int(num.strip(" ,")) for num in input("Enter your next move: ").split()]
        row = self.rows - x
        column = y - 1
        if not self.possible_field(row, column):
            raise ValueError
        next_field = self.board[row][column]
        if next_field not in self.possible_moves:
            raise ValueError
        self.place_knight(next_field)

    def restart_board(self):
        self.board = [[Field(i, j + 1) for j in range(self.cols)] for i in range(self.rows, 0, -1)]
        self.set_start_position(x=self.start_pos.x, y=self.start_pos.y)

    def all_visited(self):
        for row in self.board:
            for f in row:
                if not f.visited:
                    return False
        return True

    def find_solution(self, start=0):
        if not self.possible_moves:
            if self.all_visited():
                return True
            else:
                return 0
        if start >= len(self.possible_moves):
            return None

        next_field = sorted(self.possible_moves, key=lambda x: x.num_of_possibilities)[start]
        self.place_knight(next_field)
        result = self.find_solution()
        if result == 0:
            self.knight_pos.visited = False
            self.path.pop()
            self.place_knight(self.path[-1])
            self.find_solution(start+1)
        else:
            return result

    def print_positions(self):
        board_str = "\nHere's the solution!\n"
        board_str += f" {'-' * (self.cols * (len(self.placeholder) + 1) + 3)}\n"
        for i, row in zip(range(self.rows, 0, -1), self.board):
            board_str += f"{i}| "
            for f in row:
                f_str = f"{(len(self.placeholder) - len(str(f.path_position))) * ' '}{f.path_position} "
                board_str += f_str
            board_str += "|\n"
        board_str += f" {'-' * (self.cols * (len(self.placeholder) + 1) + 3)}\n"
        board_str += f"   {' '.join([self.placeholder[:-1].replace('_', ' ') + str(col) for col in range(1, self.cols + 1)])}"
        print(board_str)

    def __str__(self):
        board_str = f" {'-' * (self.cols * (len(self.placeholder) + 1) + 3)}\n"
        for i, row in zip(range(self.rows, 0, -1), self.board):
            board_str += f"{i}| "
            for f in row:
                f_str = self.placeholder[:-1].replace("_", " ")
                if f.knight_on:
                    f_str += "X "
                elif f in self.possible_moves:
                    f_str += f"{f.num_of_possibilities} "
                elif f.visited:
                    f_str += "* "
                else:
                    f_str = self.placeholder + " "
                board_str += f_str
            board_str += "|\n"
        board_str += f" {'-' * (self.cols * (len(self.placeholder) + 1) + 3)}\n"
        board_str += f"   {' '.join([self.placeholder[:-1].replace('_', ' ') + str(col) for col in range(1, self.cols + 1)])}"
        return board_str + "\n"


def main():
    game = Game()
    game.play()


if __name__ == "__main__":
    main()
