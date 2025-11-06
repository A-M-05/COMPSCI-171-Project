from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

REGULAR_VALUE = 100
KING_VALUE = 325

MOBILITY_WEIGHT = 3
CENTER_WEIGHT = 4
VULNERABILITY_WEIGHT = -15

LOSS_SCORE = -100_000

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        

    def get_move(self,move):
        if move and len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1
        # moves = self.board.get_all_possible_moves(self.color)
        # index = randint(0,len(moves)-1)
        # inner_index =  randint(0,len(moves[index])-1)
        # move = moves[index][inner_index]
        # self.board.make_move(move,self.color)
        # self.evaluate_board()
        # return move

        groups = self.board.get_all_possible_moves(self.color)
        first_moves = [m for g in groups for m in g]

        if not first_moves:
            return Move([])
        
        best_score = -1000000
        best_move = first_moves[0]
        search_depth = 4

        first_moves.sort(key=lambda mv: (self.is_capture_move(mv), len(getattr(mv, "seq", []))), reverse=True)

        for mv in first_moves:
            self.board.make_move(mv, self.color)
            score = self.minimax(self.opponent[self.color], search_depth - 1)
            self.board.undo()
            if score > best_score:
                best_score = score
                best_move = mv
        
        self.board.make_move(best_move, self.color)
        return best_move

    def is_capture_move(self, mv: Move):
        seq = getattr(mv, "seq", [])
        for (r1, c1), (r2, c2) in zip(seq, seq[1:]):
            if abs(r2-r1) == 2 and abs(c2-c1) == 2:
                return True
        return False
    
    def capture_move_count(self, side):
        groups = self.board.get_all_possible_moves(side)
        count = 0
        for g in groups:
            for mv in g:
                if self.is_capture_move(mv):
                    count += 1
        return count
    
    def evaluate_color(self, color):
        opp = self.opponent[color]

        # material / king checking
        my_men = my_kings = opp_men = opp_kings = 0
        for r in range(self.board.row):
            for c in range(self.board.col):
                checker = self.board.board[r][c]
                if not checker:
                    continue
                is_king = getattr(checker, "is_king", False)
                if checker.color == color:
                    if is_king:
                        my_kings += 1
                    else:
                        my_men += 1
                else:
                    if is_king:
                        opp_kings += 1
                    else:
                        opp_men += 1
        
        material_score = (my_men - opp_men) * REGULAR_VALUE + (my_kings - opp_kings) * KING_VALUE

        # mobility
        my_groups = self.board.get_all_possible_moves(color)
        opp_groups = self.board.get_all_possible_moves(opp)
        my_moves = sum(len(g) for g in my_groups)
        opp_moves = sum(len(g) for g in opp_groups)
        mobility_score = (my_moves - opp_moves) * MOBILITY_WEIGHT

        # center control
        def in_center(rr, cc):
            margin_r = 2 if self.board.row >= 8 else max(1, self.board.row // 4)
            margin_c = 2 if self.board.col >= 8 else max(1, self.board.col // 4)
            return (margin_r <= rr <= self.board.row - 1 - margin_r and
                    margin_c <= cc <= self.board.col - 1 - margin_c)

        my_center = opp_center = 0
        for r in range(self.board.row):
            for c in range(self.board.col):
                checker = self.board.board[r][c]
                if not checker:
                    continue
                if in_center(r, c):
                    if checker.color == color: my_center += 1
                    else:                    opp_center += 1
        center_score = (my_center - opp_center) * CENTER_WEIGHT

        # vulnerability
        opp_captures_now = self.capture_move_count(opp)
        my_captures_now  = self.capture_move_count(color)
        vulnerability_score = (my_captures_now - opp_captures_now) * VULNERABILITY_WEIGHT

        return material_score + mobility_score + center_score + vulnerability_score
    
    def minimax(self, color, depth = 3):
        if depth == 0:
            return self.evaluate_color(color)
        
        groups = self.board.get_all_possible_moves(color)
        moves = [m for g in groups for m in g]
        moves.sort(key=lambda mv: (self.is_capture_move(mv), len(getattr(mv, "seq", []))), reverse=True)

        if not moves:
            return LOSS_SCORE

        if color == self.color:  # MAX node
            best_value = float("-inf")
            for move in moves:
                self.board.make_move(move, color)
                val = self.minimax(self.opponent[color], depth - 1)
                self.board.undo()
                if val > best_value:
                    best_value = val
            return best_value
        else:  # MIN node
            best_value = float("inf")
            for move in moves:
                self.board.make_move(move, color)
                val = self.minimax(self.opponent[color], depth - 1)
                self.board.undo()
                if val < best_value:
                    best_value = val
            return best_value
