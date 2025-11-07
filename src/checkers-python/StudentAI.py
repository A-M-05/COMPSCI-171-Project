from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
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
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        moves = self.board.get_all_possible_moves(self.color)
        index = randint(0,len(moves)-1)
        inner_index =  randint(0,len(moves[index])-1)
        move = moves[index][inner_index]
        self.board.make_move(move,self.color)
        return move



    def evaluate_color(self, color):
        """
        Returns a static evaluation of the board from the perspective of `color`.
        Positive score = good for `color`.
        Negative score = bad for `color`.
        """

        # Convert 1/2 → 'B'/'W'
        my = 'B' if color == 1 else 'W'
        opp = 'W' if color == 1 else 'B'

        my_score = 0
        opp_score = 0

        # --- MATERIAL + KING VALUE ---
        for r in range(self.board.row):
            for c in range(self.board.col):
                chk = self.board.board[r][c]
                if chk.color == my:
                    my_score += 3 if chk.is_king else 1
                elif chk.color == opp:
                    opp_score += 3 if chk.is_king else 1

        # --- MOBILITY BONUS ---
        my_moves = self.board.get_all_possible_moves(color)
        opp_moves = self.board.get_all_possible_moves(self.opponent[color])

        my_score += 0.1 * sum(len(g) for g in my_moves)
        opp_score += 0.1 * sum(len(g) for g in opp_moves)

        return my_score - opp_score


    