import math
import random
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

class MCTSNode:
    def __init__(self, parent, move, player_to_move):
        self.parent = parent            # parent node
        self.move = move                # move applied at parent to reach this node
        self.player = player_to_move    # side to move at this node
        self.children = []              # list of MCTSNode
        self.untried = []               # moves not expanded yet
        self.visits = 0                 
        self.wins = 0.0                 # wins from ROOT player's POV

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}

    # ---------------------------------------------
    # IS CAPTURE
    # ---------------------------------------------
    def _is_capture_move(self, mv : Move) -> bool:
        """
        Checks if a Move is a capture or not
        
        Args:
            mv (Move): The move to check
        
        Returns:
            bool: Capture move or not
        """

        seq = getattr(mv, "seq", [])
        for (r1, c1), (r2, c2) in zip(seq, seq[1:]):
            if abs(r2 - r1) == 2 and abs(c2 - c1) == 2:
                return True
        return False

    # ---------------------------------------------
    # LEGAL MOVES
    # ---------------------------------------------
    def _legal_moves_flat(self, color) -> list:
        """
        Returns all possible moves of a player shuffled, with a preference towards
        capture moves over quiet moves.

        Args:
            color (int): The color of the player
        
        Returns:
            list: List of all possible moves, flattened
        """

        groups = self.board.get_all_possible_moves(color)
        moves = [m for g in groups for m in g]
        cap = [m for m in moves if self._is_capture_move(m)]
        quiet = [m for m in moves if not self._is_capture_move(m)]
        random.shuffle(cap)
        random.shuffle(quiet)
        return cap + quiet
    
    # ---------------------------------------------
    # WIN CHECK
    # ---------------------------------------------
    def _winner_or_none(self):
        """
        Checks if a player has won or not

        Returns:
            int: 1 if player 1 won, 2 if player 2 won, 
                 None if no one has won
        """

        # return 1 or 2 if someone has won, else None
        if self.board.is_win(1):
            return 1
        if self.board.is_win(2):
            return 2
        return None
    
    # ---------------------------------------------
    # UCT SELECT
    # ---------------------------------------------
    def _uct_select_child(self, node, c=1.4):
        """
        Returns the UCT value of a MCTS Node

        Args:
            node (MCTSNode): node to calculate UCT for
            c (float): exploration factor
        
        Returns:
            UCT value of node
        """

        logN = math.log(node.visits + 1)
        def uct(ch):
            if ch.visits == 0:
                return float("inf")
            exploit = ch.wins / ch.visits
            explore = c * math.sqrt(logN / ch.visits)
            return exploit + explore
        return max(node.children, key = uct)
    
    # ---------------------------------------------
    # EXPANSION
    # ---------------------------------------------
    def _expand(self, node):
        if not node.untried:
            node.untried = self._legal_moves_flat(node.player)
        if not node.untried:
            return node # terminal
        mv = node.untried.pop()
        self.board.make_move(mv, node.player)
        child = MCTSNode(node, mv, self.opponent[node.player])
        node.children.append(child)
        return child
    
    # ---------------------------------------------
    # ROLLOUT
    # ---------------------------------------------
    def _rollout(self, player, max_plies=20):
        local = []

        for _ in range(max_plies):
            # terminal?
            w = self._winner_or_none()
            if w:
                for mv, col in reversed(local): self.board.undo()
                return w

            # moves
            moves = self._legal_moves_flat(player)
            if not moves:
                loser = player
                winner = self.opponent[loser]
                for mv, col in reversed(local): self.board.undo()
                return winner

            # FULL CAPTURE POLICY:
            capture_moves = [m for m in moves if self._is_capture_move(m)]
            if capture_moves:
                # pick the longest capture chain
                max_len = max(len(getattr(mv, "seq", [])) for mv in capture_moves)
                best_caps = [mv for mv in capture_moves if len(getattr(mv, "seq", [])) == max_len]
                mv = random.choice(best_caps)
            else:
                mv = random.choice(moves)

            self.board.make_move(mv, player)
            local.append((mv, player))
            player = self.opponent[player]

        # static fallback (correct perspective)
        score = self.evaluate_color(self.color)
        winner = self.color if score >= 0 else self.opponent[self.color]

        for mv, col in reversed(local): self.board.undo()
        return winner
    
    # ---------------------------------------------
    # BACKPROP
    # ---------------------------------------------
    def _backprop(self, path, winner, root_player):
        for node in path:
            node.visits += 1
            if winner == root_player:
                node.wins += 1.0

    # ---------------------------------------------
    # MCTS SEARCH
    # ---------------------------------------------
    def _mcts_search(self, iterations = 300):
        root = MCTSNode(parent=None, move=None, player_to_move=self.color)
        root.untried = self._legal_moves_flat(root.player)

        if not root.untried:
            return Move([])

        for _ in range(iterations):
            node = root
            path = [node]
            applied = []   # moves applied on self.board in this iteration

            # -------- SELECTION --------
            while not node.untried and node.children:
                node = self._uct_select_child(node)
                if node.move is not None:
                    # apply node's move (chosen by parent.player)
                    self.board.make_move(node.move, node.parent.player)
                    applied.append((node.move, node.parent.player))
                path.append(node)

            # -------- EXPANSION --------
            if node.untried:
                mv = node.untried.pop()
                self.board.make_move(mv, node.player)
                applied.append((mv, node.player))
                child = MCTSNode(node, mv, self.opponent[node.player])
                node.children.append(child)
                node = child
                path.append(node)

            # -------- ROLLOUT --------
            winner = self._rollout(node.player)

            # -------- UNDO SELECTION + EXPANSION --------
            for mv, col in reversed(applied):
                self.board.undo()

            # -------- BACKPROP --------
            self._backprop(path, winner, root_player=self.color)

        # choose move with most visits
        best_child = max(root.children, key=lambda ch: ch.visits)
        return best_child.move
    
    # ---------------------------------------------
    # EVALUATION
    # ---------------------------------------------
    def evaluate_color(self, color):
        """
        Returns a static evaluation of the board from the perspective of `color`.
        Positive score = good for `color`.
        Negative score = bad for `color`.
        """

        opp = self.opponent[color]

        my_score = opp_score = 0

        for i in range(self.board.row):
            for j in range(self.board.col):
                checker = self.board.board[i][j]
                if not checker:
                    continue

                is_king = checker.is_king

                if checker.color == color:
                    my_score += 4 if is_king else 1
                elif checker.color == opp:
                    opp_score += 4 if is_king else 1

        # mobility
        my_moves = self.board.get_all_possible_moves(color)
        opp_moves = self.board.get_all_possible_moves(opp)
        my_score += 0.1 * sum(len(g) for g in my_moves)
        opp_score += 0.1 * sum(len(g) for g in opp_moves)

        return my_score - opp_score

    def get_move(self, move):
        # Determine your assigned color correctly.
        if self.color == '':
            if move:
                # Opponent played first -> you are Player 2 (White)
                self.color = 2
            else:
                # No move history -> you are Player 1 (Black)
                self.color = 1

        # Apply opponent move
        if move:
            self.board.make_move(move, self.opponent[self.color])

        # Run MCTS on the correct root color
        best = self._mcts_search()

        self.board.make_move(best, self.color)
        return best