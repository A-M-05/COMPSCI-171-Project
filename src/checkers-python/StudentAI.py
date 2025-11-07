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
        self.WIN_SCORE  = 100000
        self.LOSS_SCORE = -100000

    



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

    def minimax(self, color) -> Move:
        to_move = self.color
        value, move = self.maxim(color);
        return move

    def maxim(self, color):
        if self.board.is_win(self.color): 
            return (1000000, None)
        val = -1000000000
        best_move = None
        moves = self.board.get_all_possible_moves(color)
        for piece in moves:
            for move in piece:
                v2 = self.minim(self.opponent[color])
                if v2 > val:
                    val, best_move = v2, move
        return val, best_move
    
    def minim(self, color):
        opp = self.opponent[self.color]
        if self.board.is_win(self.color): 
            return (1000000, None)
        val = -1000000000
        best_move = None
        moves = self.board.get_all_possible_moves(color)
        for piece in moves:
            for move in piece:
                v2 = self.maxim(self.opponent[color])
                if v2 < val:
                    val, best_move = v2, move
        return val, best_move


    def eval_move(self, move, color):
        self.board.make_move(move)
        val = self.evaluate_color(color)
        self.board.undo()
        return val
    
    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        print(self.board.get_all_possible_moves(self.color))
        print(self.board.get_all_possible_moves(self.opponent[self.color]))
        # moves = self.board.get_all_possible_moves(self.color)
        # index = randint(0,len(moves)-1)
        # inner_index =  randint(0,len(moves[index])-1)
        # move = moves[index][inner_index]
        # self.board.make_move(move,self.color)
        
        score, move = self.minimax(self.color)
        return move