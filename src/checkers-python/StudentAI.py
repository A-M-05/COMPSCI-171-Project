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

TACTICAL_NOW_BONUS = 12
TACTICAL_NOW_PENALTY = -14

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
        

    def get_move(self, move):
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
        
        first_moves.sort(key=lambda mv: self._move_priority(mv, self.color), reverse=True)
        
        best_score = -1000000
        best_move = first_moves[0]
        alpha = float("-inf")
        beta = float("inf")
        search_depth = 6

        scores = []
        for mv in first_moves:
            self.board.make_move(mv, self.color)
            score = self.minimax(self.opponent[self.color], search_depth - 1, alpha, beta)
            self.board.undo()
            scores.append(score)
        
        EPS = 5 
        best_score = max(scores)
        candidates = [mv for mv, s in zip(first_moves, scores) if best_score - s <= EPS]

        def _root_tiebreak_key(mv: Move):
            # prefer: will king now, is a capture, reduces opponent mobility after our move
            will_king = self._will_king(mv, self.color)
            is_cap   = self._is_capture_move(mv)

            self.board.make_move(mv, self.color)
            opp_moves_after = sum(len(g) for g in self.board.get_all_possible_moves(self.opponent[self.color]))
            self.board.undo()

            return (
                1 if will_king else 0,
                1 if is_cap else 0,
                -opp_moves_after   # fewer opponent replies is better
            )

        best_move = max(candidates, key=_root_tiebreak_key)

        # keep internal board in sync
        self.board.make_move(best_move, self.color)
        return best_move

    def _is_capture_move(self, mv: Move) -> bool:
        """
        Return True iff `mv` is a capture (jump) move.

        A capture is detected by any step in the path that jumps two rows and two
        columns (standard American checkers). Multi-jumps are still a single Move
        whose `seq` contains multiple hops.

        Parameters
        ----------
        mv : Move
            Candidate move whose `seq` is a list of (row, col) squares.

        Returns
        -------
        bool
            True if at least one hop in `seq` is a 2*2 diagonal jump; False otherwise.
        """

        seq = getattr(mv, "seq", [])
        for (r1, c1), (r2, c2) in zip(seq, seq[1:]):
            if abs(r2-r1) == 2 and abs(c2-c1) == 2:
                return True
        return False
    
    def _capture_move_count(self, side) -> int:
        """
        Count how many legal capture moves the given `side` has from the current state.

        Useful as a cheap "vulnerability" proxy in evaluation:
        if the opponent has many captures now, treat that as danger.

        Parameters
        ----------
        side : int
            Side-to-move color (1 or 2) for which to count captures.

        Returns
        -------
        int
            Number of moves for `side` whose path contains at least one 2*2 jump.
        """

        groups = self.board.get_all_possible_moves(side)
        count = 0
        for g in groups:
            for mv in g:
                if self._is_capture_move(mv):
                    count += 1
        return count
    
    def _has_captures(self, side: int) -> bool:
        groups = self.board.get_all_possible_moves(side)
        for g in groups:
            for mv in g:
                if self._is_capture_move(mv):
                    return True
        return False
    
    def _will_king(self, mv: Move, color: int) -> bool:
        seq = getattr(mv, "seq", [])
        if not seq:
            return False
        (r0, c0) = seq[0]
        (re, ce) = seq[-1]
        checker = self.board.board[r0][c0]
        if not checker or getattr(checker, "is_king", False):
            return False
        return (color == 1 and re == self.board.row - 1) or (color == 2 and re == 0)
    
    def _creates_capture_next(self, mv: Move, color: int) -> bool:
        self.board.make_move(mv, color)
        has_my_cap_next = any(
            self._is_capture_move(mmv)
            for g in self.board.get_all_possible_moves(color)
            for mmv in g
        )
        self.board.undo()
        return has_my_cap_next
    
    def _move_priority(self, mv: Move, color: int) -> tuple:
        seq = getattr(mv, "seq", [])
        length = len(seq)
        is_cap = self._is_capture_move(mv)
        will_king = self._will_king(mv, color)
        creates_cap = self._creates_capture_next(mv, color)

        (re, ce) = seq[-1] if seq else (-1, -1)
        margin_r = 2 if self.board.row >= 8 else max(1, self.board.row // 4)
        margin_c = 2 if self.board.col >= 8 else max(1, self.board.col // 4)
        in_center = (margin_r <= re <= self.board.row - 1 - margin_r and
                        margin_c <= ce <= self.board.col - 1 - margin_c)
        return (
            1 if is_cap else 0,
            length,                  # longer chains first
            1 if will_king else 0,   # promotion now
            1 if creates_cap else 0, # creates a threat
            1 if in_center else 0    # slight tie-breaker
        )
    
    def _quiesce(self, color, alpha: float, beta: float) -> float:
        stand_pat = self.evaluate_color(color)
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
        
        groups = self.board.get_all_possible_moves(color)
        capture_moves = [m for g in groups for m in g if self._is_capture_move(m)]
        capture_moves.sort(key=lambda mv: len(getattr(mv, "seq", [])), reverse=True)

        for mv in capture_moves:
            self.board.make_move(mv, color)
            score = -self._quiesce(self.opponent[color], -beta, -alpha)
            self.board.undo() 

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    # -------------------- HEURISTIC --------------------
    def evaluate_color(self, color) -> float:
        """
        Heuristic evaluation of the current board from `color`'s perspective.

        Positive values favor `color`; negative values favor the opponent.
        This evaluator is linear and fast: MATERIAL (dominant), MOBILITY (aggregate),
        CENTER control, and a lightweight VULNERABILITY proxy.

        Parameters
        ----------
        color : int
            Node's side-to-move (1 or 2). The score is "good for this side".

        Returns
        -------
        float
            Heuristic score of the position for `color`.
        """

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
        opp_captures_now = self._capture_move_count(opp)
        my_captures_now  = self._capture_move_count(color)
        vulnerability_score = (my_captures_now - opp_captures_now) * VULNERABILITY_WEIGHT
        my_cap_now  = self._capture_move_count(color) > 0
        opp_cap_now = self._capture_move_count(self.opponent[color]) > 0

        tactical_now = (TACTICAL_NOW_BONUS if my_cap_now else 0) + \
                    (TACTICAL_NOW_PENALTY if opp_cap_now else 0)

        return material_score + mobility_score + center_score + vulnerability_score + tactical_now
    
    # -------------------- MINIMAX --------------------
    def minimax(self, color, depth: int = 3, alpha: float = float("-inf"), beta: float = float("inf")) -> float:
        """
            Depth-limited minimax with alpha-beta pruning.

        Parameters
        ----------
        color : int
            Node's side-to-move (1 or 2) at this ply.
        depth : int, default=3
            Remaining search plies. When 0, evaluation is returned.
        alpha : float, default = -inf

        beta : float, default = inf


        Returns
        -------
        float
            Best achievable score at this node assuming optimal play by both sides.

        """

        if depth == 0:
            if self._has_captures(color):
                return self._quiesce(color, alpha, beta)
            return self.evaluate_color(color)
        
        groups = self.board.get_all_possible_moves(color)
        moves = [m for g in groups for m in g]
        moves.sort(key=lambda mv: self._move_priority(mv, color), reverse=True)

        if not moves:
            return LOSS_SCORE

        if color == self.color:  # MAX node
            best_value = float("-inf")
            for move in moves:
                self.board.make_move(move, color)
                val = self.minimax(self.opponent[color], depth - 1, alpha, beta)
                self.board.undo()

                if val > best_value:
                    best_value = val
                if best_value > alpha:
                    alpha = best_value
                if alpha >= beta: # prune if alpha > beta
                    break

            return best_value
        
        else:  # MIN node
            best_value = float("inf")
            for move in moves:
                self.board.make_move(move, color)
                val = self.minimax(self.opponent[color], depth - 1, alpha, beta)
                self.board.undo()

                if val < best_value:
                    best_value = val
                if best_value < beta:
                    beta = best_value
                if alpha >= beta: # prune if alpha > beta
                    break
            
            return best_value
