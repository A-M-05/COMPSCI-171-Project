from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

REGULAR_VALUE = 100
KING_VALUE = 325

MOBILITY_WEIGHT = 3
VULNERABILITY_WEIGHT = -15

LOSS_SCORE = -100_000
MAX_SEARCH_DEPTH = 2

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = None
        

    def get_move(self, move):
        # infer our color and sync board
        if self.color is None:
            if move and len(move) != 0:
                self.color = 2          # we are White, we go second
                self.board.make_move(move, 1)
            else:
                self.color = 1          # we are Black, we go first
        else:
            if move and len(move) != 0:
                self.board.make_move(move, self.opponent[self.color])

        # generate legal moves
        groups = self.board.get_all_possible_moves(self.color)
        moves = [m for g in groups for m in g]
        if not moves:
            return Move([])
        
        # sort moves based on capture chains
        moves.sort(key=lambda mv: (self._is_capture_move(mv), len(getattr(mv, "seq", []))), reverse=True)

        # loop through each move and run minimax on the 
        # board state it reaches
        best_move = moves[0]
        principal_move = best_move # principal move
        max_depth = MAX_SEARCH_DEPTH

        for depth in range(1, max_depth + 1):
            curr_best_move = moves[0]
            curr_best_score = float("-inf")
            alpha, beta = float("-inf"), float("inf")

            # try the principal move first (if we have one from the last iteration)
            if principal_move in moves:
                moves.remove(principal_move)
                moves.insert(0, principal_move)

            for mv in moves:
                self.board.make_move(mv, self.color)
                score = self.minimax(self.opponent[self.color], depth - 1, alpha, beta)
                self.board.undo()

                if score > curr_best_score:
                    curr_best_score = score
                    curr_best_move = mv

            best_move = curr_best_move
            principal_move = curr_best_move  # use it to order the next iteration

        self.board.make_move(best_move, self.color)
        return best_move
    
    # -------------------- CAPTURE? --------------------
    def _is_capture_move(self, mv: Move) -> bool:
        seq = getattr(mv, "seq", [])
        for (r1, c1), (r2, c2) in zip(seq, seq[1:]):
            if abs(r2 - r1) == 2 and abs(c2 - c1) == 2:
                return True
        return False


    # -------------------- HEURISTIC --------------------
    def evaluate_color(self, color) -> float:
        opp = self.opponent[color]

        # points based on how many of our pieces vs opponents pieces 
        # are on the board right now
        my_men = 0
        my_kings = 0
        opp_men = 0
        opp_kings = 0

        for r in range(self.board.row):
            for c in range(self.board.col):
                checker = self.board.board[r][c]
                if not checker:
                    continue
                is_king = getattr(checker, "is_king", False)
                if checker.color == color:
                    if is_king: my_kings += 1
                    else:       my_men   += 1
                else:
                    if is_king: opp_kings += 1
                    else:       opp_men   += 1
        material = my_men * REGULAR_VALUE + my_kings * KING_VALUE

        # points based on the mobility of our pieces vs opps pieces
        # my_groups  = self.board.get_all_possible_moves(color)
        # opp_groups = self.board.get_all_possible_moves(opp)
        # my_moves   = sum(len(g) for g in my_groups)
        # opp_moves  = sum(len(g) for g in opp_groups)
        # mobility   = (my_moves - opp_moves) * MOBILITY_WEIGHT

        return material # + mobility
    
    # -------------------- MINIMAX --------------------
    def minimax(self, color: int, depth: int, alpha: float = float("-inf"), beta: float = float("inf")) -> float:
        
        if depth == 0:
            return self.evaluate_color(color)

        groups = self.board.get_all_possible_moves(color)
        moves = [m for g in groups for m in g]
        if not moves:
            return LOSS_SCORE  # side-to-move has no legal moves
        
        # sort moves based on capture chains
        moves.sort(key=lambda mv: (self._is_capture_move(mv), len(getattr(mv, "seq", []))), reverse=True)

        if color == self.color:  # MAX
            best = float("-inf")
            for mv in moves:
                self.board.make_move(mv, color)
                val = self.minimax(self.opponent[color], depth - 1, alpha, beta)
                self.board.undo()
                if val > best:
                    best = val
                if best > alpha:
                    alpha = best
                if alpha >= beta:
                    break
            return best
        else:  # MIN
            best = float("inf")
            for mv in moves:
                self.board.make_move(mv, color)
                val = self.minimax(self.opponent[color], depth - 1, alpha, beta)
                self.board.undo()
                if val < best:
                    best = val
                if best < beta:
                    beta = best
                if alpha >= beta:
                    break
            return best
