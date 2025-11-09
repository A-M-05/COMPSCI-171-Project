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

    def minimax(self, color, alpha, beta, depth = 4) -> Move:
        value, move = self.maxim(color, alpha, beta, depth)
        return move

    def maxim(self, color, alpha, beta, depth):
        
        if depth == 0:
            return (self.evaluate_color(self.color), None)
        if self.board.is_win(self.color): 
            return (10000000, None)
        opp = self.opponent[self.color]
        if self.board.is_win(opp): 
            return (-10000000, None)
        val = -1000000000
        best_move = None
        moves = self.board.get_all_possible_moves(color)
        if not moves:
            return (-100000000, None)
        for piece in moves:
            for move in piece:
                self.board.make_move(move, color)
                v2, _ = self.minim(self.opponent[color], alpha, beta, depth-1)
                self.board.undo()
                if v2 > val:
                    val, best_move = v2, move
                alpha = max(alpha, v2)
                if beta <= alpha:
                    break
        return val, best_move
    
    def minim(self, color, alpha, beta, depth):
        opp = self.opponent[self.color]
        if depth == 0:
            return (self.evaluate_color(self.color), None)
        if self.board.is_win(self.color): 
            return (10000000, None)
        if self.board.is_win(opp): 
            return (-10000000, None)
        val = 1000000000
        best_move = None
        moves = self.board.get_all_possible_moves(color)
        if not moves:
            return (1000000000, None)
        for piece in moves:
            for move in piece:
                self.board.make_move(move, color)
                v2, _ = self.maxim(self.opponent[color], alpha, beta, depth-1)
                self.board.undo()
                if v2 < val:
                    val, best_move = v2, move
                beta = min(beta, v2)
                if beta <= alpha:
                    break
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
        # moves = self.board.get_all_possible_moves(self.color)
        # index = randint(0,len(moves)-1)
        # inner_index =  randint(0,len(moves[index])-1)
        # move = moves[index][inner_index]
        # self.board.make_move(move,self.color)
            
        move = self.minimax(self.color, -10000000, 1000000, 2)

        if move is None:
            # Get all possible moves as fallback
            possible = self.board.get_all_possible_moves(self.color)
            
            if possible and len(possible) > 0 and len(possible[0]) > 0:
                # Use the first available move
                move = possible[0][0]
                print("WARNING: Minimax returned None, using fallback move")
            else:
                # No moves available at all - game is over
                print("ERROR: No valid moves available!")
                return None
        self.board.make_move(move, self.color)
        print(move)
        return move