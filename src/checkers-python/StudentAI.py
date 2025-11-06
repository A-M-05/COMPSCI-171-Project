from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

checker_value = 1
king_factor = 2
mobility_factor = 0.3
# safe_move_bonus = 15

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
        # moves = self.board.get_all_possible_moves(self.color)
        # index = randint(0,len(moves)-1)
        # inner_index =  randint(0,len(moves[index])-1)
        # move = moves[index][inner_index]
        # self.board.make_move(move,self.color)
        # self.evaluate_board()
        # return move

        num = self.minimax(self.color)
        print(num)
        return num

    def minimax(self, color, depth = 3):
        if depth == 0:
            return self.evaluate_color(self.color)
        
        if color == self.color: #1 is black, #2 is white
            best_value = -10000

            for piece in self.board.get_all_possible_moves(color):
                for move in piece:
                    # we already have a function for this
                    self.board.make_move(move, color)
                    val = self.minimax(self.opponent[color], depth-1)

                    if val > best_value:
                        best_value = val
                    self.board.undo()
            return best_value

        else:
            best_value = 10000
            
            for piece in self.board.get_all_possible_moves(self.opponent[color]):
                for move in piece:
                    # we already have a function for this
                    self.board.make_move(move, self.opponent[color])
                    val = -1 * self.minimax(color, depth-1)
            
                    if val < best_value:
                        best_value = val
                    self.board.undo()
        
        return best_value
            

        

    def evaluate_color(self, color):
        #self.color black = 1, white = 2
        
        # check if win for curr player
        if self.board.is_win(self.color):
            return 10000
        # check if win for other player
        elif self.board.is_win(self.opponent[self.color]):
            return -10000
        
        # check all pieces of self.color
        total_points = 0
        for i in range(0, self.board.row):
            for j in range(0, self.board.col):

                checker = self.board.board[i][j]

                # check for self.color
                if checker.color == color:
                    value = checker_value
                    # get num of moves possible from here
                    num_moves = len(checker.get_possible_moves(self.board)[0]) # has [1] being is_capture
                    value += num_moves * mobility_factor
                    # multiplier for being a king cause it's stronger
                    if checker.is_king:
                        value *= king_factor
                    total_points += value

        return total_points