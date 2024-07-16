class Color:
    WHITE = 'white'
    BLACK = 'black'

class Square:
    columns = 'abcdefgh'

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.piece = None

    def __repr__(self):
        return f"{Square.columns[self.x]}{self.y + 1}"

class Piece:
    def __init__(self, color, board=None):
        self.color = color
        self.board = board
        self.has_moved = False  # Indicates if the piece has moved

    def is_valid_move(self, start_square, end_square):
        raise NotImplementedError("Must be implemented by subclass")

class Pawn(Piece):
    def __str__(self):
        return '♙' if self.color == Color.WHITE else '♟'

    def is_valid_move(self, start_square, end_square):
        direction = 1 if self.color == Color.WHITE else -1
        start_x, start_y = start_square.x, start_square.y
        end_x, end_y = end_square.x, end_square.y

        # Forward move
        if start_x == end_x and end_y == start_y + direction and end_square.piece is None:
            return True

        # First move can be two squares forward
        if start_x == end_x and end_y == start_y + 2 * direction and start_y in (1, 6) and end_square.piece is None:
            return True

        # Capturing move
        if abs(start_x - end_x) == 1 and end_y == start_y + direction and end_square.piece and end_square.piece.color != self.color:
            return True

        return False

class Rook(Piece):
    def __str__(self):
        return '♖' if self.color == Color.WHITE else '♜'

    def is_valid_move(self, start_square, end_square):
        start_x, start_y = start_square.x, start_square.y
        end_x, end_y = end_square.x, end_square.y

        if start_x != end_x and start_y != end_y:
            return False

        if self.board.is_path_clear(start_square, end_square):
            return end_square.piece is None or end_square.piece.color != self.color

        return False

class Knight(Piece):
    def __str__(self):
        return '♘' if self.color == Color.WHITE else '♞'

    def is_valid_move(self, start_square, end_square):
        start_x, start_y = start_square.x, start_square.y
        end_x, end_y = end_square.x, end_square.y

        dx = abs(start_x - end_x)
        dy = abs(start_y - end_y)

        if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
            return end_square.piece is None or end_square.piece.color != self.color

        return False

class Bishop(Piece):
    def __str__(self):
        return '♗' if self.color == Color.WHITE else '♝'

    def is_valid_move(self, start_square, end_square):
        start_x, start_y = start_square.x, start_square.y
        end_x, end_y = end_square.x, end_square.y

        if abs(start_x - end_x) != abs(start_y - end_y):
            return False

        if self.board.is_path_clear(start_square, end_square):
            return end_square.piece is None or end_square.piece.color != self.color

        return False

class Queen(Piece):
    def __str__(self):
        return '♕' if self.color == Color.WHITE else '♛'

    def is_valid_move(self, start_square, end_square):
        start_x, start_y = start_square.x, start_square.y
        end_x, end_y = end_square.x, end_square.y

        if (abs(start_x - end_x) == abs(start_y - end_y) or 
            start_x == end_x or 
            start_y == end_y):
            if self.board.is_path_clear(start_square, end_square):
                return end_square.piece is None or end_square.piece.color != self.color

        return False

class King(Piece):
    def __str__(self):
        return '♔' if self.color == Color.WHITE else '♚'

    def is_valid_move(self, start_square, end_square):
        start_x, start_y = start_square.x, start_square.y
        end_x, end_y = end_square.x, end_square.y

        # Regular king move (one square in any direction)
        if max(abs(start_x - end_x), abs(start_y - end_y)) == 1:
            return end_square.piece is None or end_square.piece.color != self.color

        # Castling move
        if start_y == end_y and not self.has_moved:
            if end_x == start_x + 2:  # Kingside castling
                rook_square = self.board.get_square(Square.columns[start_x + 3] + str(start_y + 1))
                if rook_square.piece and isinstance(rook_square.piece, Rook) and not rook_square.piece.has_moved:
                    if self.board.is_path_clear(start_square, end_square) and self.board.is_path_clear(start_square, rook_square):
                        return True
            elif end_x == start_x - 2:  # Queenside castling
                rook_square = self.board.get_square(Square.columns[start_x - 4] + str(start_y + 1))
                if rook_square.piece and isinstance(rook_square.piece, Rook) and not rook_square.piece.has_moved:
                    if self.board.is_path_clear(start_square, end_square) and self.board.is_path_clear(start_square, rook_square):
                        return True

        return False
    
    def can_castle(self, start_square, end_square):
        # Castling conditions
        if self.has_moved or self.board.is_king_in_check(self.color):
            return False
        
        direction = end_square.x - start_square.x
        if abs(direction) != 2:
            return False

        rook_square = self.board.get_square(Square.columns[end_square.x + (1 if direction < 0 else -1)] + str(start_square.y + 1))
        rook = rook_square.piece
        if not isinstance(rook, Rook) or rook.has_moved:
            return False

        path_clear = self.board.is_path_clear(start_square, end_square)
        if path_clear and not self.board.is_path_under_attack(start_square, end_square, self.color):
            return True

        return False

class Board:
    def __init__(self):
        # Initialize the board with squares and setup pieces
        self.board = {Square.columns[x] + str(y + 1): Square(x, y) for x in range(8) for y in range(8)}
        self.setup_board()

    def setup_board(self):
        # Set up pawns
        for i in range(8):
            self.board[f"{Square.columns[i]}2"].piece = Pawn(Color.WHITE, self)
            self.board[f"{Square.columns[i]}7"].piece = Pawn(Color.BLACK, self)

        # Set up rooks
        self.board["a1"].piece = Rook(Color.WHITE, self)
        self.board["h1"].piece = Rook(Color.WHITE, self)
        self.board["a8"].piece = Rook(Color.BLACK, self)
        self.board["h8"].piece = Rook(Color.BLACK, self)

        # Set up knights
        self.board["b1"].piece = Knight(Color.WHITE, self)
        self.board["g1"].piece = Knight(Color.WHITE, self)
        self.board["b8"].piece = Knight(Color.BLACK, self)
        self.board["g8"].piece = Knight(Color.BLACK, self)

        # Set up bishops
        self.board["c1"].piece = Bishop(Color.WHITE, self)
        self.board["f1"].piece = Bishop(Color.WHITE, self)
        self.board["c8"].piece = Bishop(Color.BLACK, self)
        self.board["f8"].piece = Bishop(Color.BLACK, self)

        # Set up queens
        self.board["d1"].piece = Queen(Color.WHITE, self)
        self.board["d8"].piece = Queen(Color.BLACK, self)

        # Set up kings
        self.board["e1"].piece = King(Color.WHITE, self)
        self.board["e8"].piece = King(Color.BLACK, self)

    def get_square(self, name):
        return self.board[name]

    def is_valid_move(self, start_pos, end_pos):
        start_square = self.board[start_pos]
        end_square = self.board[end_pos]
        piece = start_square.piece
        if piece is None:
            return False
        return piece.is_valid_move(start_square, end_square)

    def move_piece(self, start_pos, end_pos):
        start_square = start_pos.square
        end_square = end_pos.square
        piece = start_square.piece
        if piece and isinstance(piece, King) and abs(start_square.x - end_square.x) == 2:
            if end_square.x == start_square.x + 2:  # Kingside castling
                rook_square = self.get_square(Square.columns[start_square.x + 3] + str(start_square.y + 1))
                new_rook_square = self.get_square(Square.columns[start_square.x + 1] + str(start_square.y + 1))
            elif end_square.x == start_square.x - 2:  # Queenside castling
                rook_square = self.get_square(Square.columns[start_square.x - 4] + str(start_square.y + 1))
                new_rook_square = self.get_square(Square.columns[start_square.x - 1] + str(start_square.y + 1))
            rook = rook_square.piece
            rook_square.piece = None
            new_rook_square.piece = rook
            rook.has_moved = True

        end_square.piece = piece
        start_square.piece = None
        piece.has_moved = True

    def print_board(self, perspective=Color.WHITE):
        if perspective == Color.WHITE:
            rows = range(8, 0, -1)
            cols = Square.columns
        else:
            rows = range(1, 9)
            cols = list(reversed(Square.columns))

        print("  " + " ".join(cols))
        for y in rows:
            row = f"{y} "
            for x in cols:
                square = self.board[f"{x}{y}"]
                row += (str(square.piece) if square.piece else '.') + " "
            print(row + f" {y}")
        print("  " + " ".join(cols))
        
    def is_path_clear(self, start_square, end_square):
        start_x, start_y = start_square.x, start_square.y
        end_x, end_y = end_square.x, end_square.y

        dx = end_x - start_x
        dy = end_y - start_y

        steps = max(abs(dx), abs(dy))
        step_x = dx // steps
        step_y = dy // steps

        x, y = start_x, start_y

        for _ in range(steps - 1):
            x += step_x
            y += step_y
            if self.board[Square.columns[x] + str(y + 1)].piece is not None:
                return False

        return True   

    def is_king_in_check(self, color):
        king_square = None
        for square in self.board.values():
            piece = square.piece
            if isinstance(piece, King) and piece.color == color:
                king_square = square
                break
        
        if king_square:
            for square in self.board.values():
                piece = square.piece
                if piece and piece.color != color and piece.is_valid_move(square, king_square):
                    return True

        return False
    
    def is_path_under_attack(self, start_square, end_square, color):
        start_x, start_y = start_square.x, start_square.y
        end_x, end_y = end_square.x, end_square.y

        if start_x == end_x:  # Vertical move
            step = 1 if start_y < end_y else -1
            for y in range(start_y, end_y + step, step):
                square = self.get_square(Square.columns[start_x] + str(y + 1))
                for sq in self.board.values():
                    piece = sq.piece
                    if piece and piece.color != color and piece.is_valid_move(sq, square):
                        return True
        elif start_y == end_y:  # Horizontal move
            step = 1 if start_x < end_x else -1
            for x in range(start_x, end_x + step, step):
                square = self.get_square(Square.columns[x] + str(start_y + 1))
                for sq in self.board.values():
                    piece = sq.piece
                    if piece and piece.color != color and piece.is_valid_move(sq, square):
                        return True
        elif abs(start_x - end_x) == abs(start_y - end_y):  # Diagonal move
            step_x = 1 if start_x < end_x else -1
            step_y = 1 if start_y < end_y else -1
            x, y = start_x, start_y
            while x != end_x + step_x and y != end_y + step_y:
                square = self.get_square(Square.columns[x] + str(y + 1))
                for sq in self.board.values():
                    piece = sq.piece
                    if piece and piece.color != color and piece.is_valid_move(sq, square):
                        return True
                x += step_x
                y += step_y

        return False
    
class Move:
    def __init__(self, start_pos, end_pos, piece, captured_piece=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.piece = piece
        self.captured_piece = captured_piece

    def __repr__(self):
        return f"{self.piece}{self.start_pos}->{self.end_pos}"

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = Color.WHITE
        self.moves = []

    def setup_board(self):
        self.board.setup_board()

    def switch_turn(self):
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE

    def make_move(self, start_square, end_square):
        piece = start_square.piece
        if piece and isinstance(piece, King) and abs(start_square.x - end_square.x) == 2:
            if end_square.x == start_square.x + 2:  # Kingside castling
                rook_square = self.board.get_square(Square.columns[start_square.x + 3] + str(start_square.y + 1))
                new_rook_square = self.board.get_square(Square.columns[start_square.x + 1] + str(start_square.y + 1))
            elif end_square.x == start_square.x - 2:  # Queenside castling
                rook_square =self.board.get_square(Square.columns[start_square.x - 4] + str(start_square.y + 1))
                new_rook_square = self.board.get_square(Square.columns[start_square.x - 1] + str(start_square.y + 1))
            rook = rook_square.piece
            rook_square.piece = None
            new_rook_square.piece = rook
            rook.has_moved = True

        end_square.piece = piece
        start_square.piece = None
        piece.has_moved = True

    def play_move(self, start_pos, end_pos):
        start_square = self.board.get_square(start_pos)
        end_square = self.board.get_square(end_pos)
        piece = start_square.piece

        if piece and piece.color == self.current_turn:
            if piece.is_valid_move(start_square, end_square):
                self.make_move(start_square, end_square)
                self.switch_turn()
                return True
        return False

    def undo_move(self):
        if not self.moves:
            return False
        last_move = self.moves.pop()
        start_square = self.board.board[last_move.start_pos]
        end_square = self.board.board[last_move.end_pos]
        start_square.piece = last_move.piece
        end_square.piece = last_move.captured_piece
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        return True

    def print_board(self):
        self.board.print_board(self.current_turn)

    def play(self):
        print("Welcome to Chess!")
        self.print_board()
        while True:
            command = input(f"{self.current_turn}'s turn. Enter your move (e.g., e2 e4) or 'undo': ").strip()
            if command.lower() == 'undo':
                if self.undo_move():
                    print("Move undone.")
                else:
                    print("No moves to undo.")
            elif len(command.split()) == 2:
                start_pos, end_pos = command.split()
                if self.play_move(start_pos, end_pos):
                    print(f"Moved from {start_pos} to {end_pos}.")
                else:
                    print("Invalid move. Try again.")
            elif command.lower() == "end":
                print("You ended the game")
                return False
            else:
                print("Invalid command. Try again.")
            self.print_board()

if __name__ == "__main__":
    game = Game()
    game.play()
