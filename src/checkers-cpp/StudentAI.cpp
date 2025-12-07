#include "StudentAI.h"

//The following part should be completed by students.
//The students can modify anything except the class name and exisiting functions and varibles.
StudentAI::StudentAI(int col,int row,int p)
	:AI(col, row, p)
{
    board = Board(col,row,p);
    board.initializeGame();
    player = 2;
}

Move StudentAI::GetMove(Move move)
{
    if (move.seq.empty())
    {
        player = 1;
    }
    else{
        board.makeMove(move,player == 1?2:1);
    }

    // set up MCTS Node for root node
    MCTSNode *root = new MCTSNode();
    root->parent = nullptr;
    root->currPlayer = player;
    root->untriedMoves = flatten(board, player);
    root->visits = 0;
    root->wins = 0.0;
    root->children.clear();

    for(int i = 0; i < MAX_ITERATIONS; ++i){
        Board simBoard = board;
        MCTSNode *node = root;
        int currentPlayer = root->currPlayer;

        // selection phase
        while(node->untriedMoves.empty() && !node->children.empty()){
            MCTSNode *child = selectChild(node);

            // apply move from child to simBoard
            Move m = child->actionToGetHere;
            simBoard.makeMove(m, currentPlayer);

            // switch player
            currentPlayer = (currentPlayer == 1 ? 2 : 1);

            node = child;
        }

        // expansion phase
        if(!node->untriedMoves.empty()){
            node = expandNode(node, simBoard, currentPlayer);
        }

        // rollout phase
        double result = rollout(simBoard, currentPlayer, player);

        // back propagate result back up
        backprop(node, result);
    }

    MCTSNode *bestChild = nullptr;
    int mostVisits = -1;

    for(auto child : root->children){
        if(child->visits > mostVisits){
            mostVisits = child->visits;
            bestChild = child;
        }
    }

    Move bestMove;

    // fallback if no MCTS expansion available
    if (bestChild == nullptr) {
        // either return an empty Move or pick any legal move from the raw board
        vector<Move> legal = flatten(board, player);
        if (!legal.empty()){
            // choose first move, or make it random?
            bestMove = legal[0];
        }
        else{
            return Move();        // no moves, so game is over
        }
    } 
    else{
        // select the move that made bestChild
        bestMove = bestChild->actionToGetHere;
    }

    // play move
    board.makeMove(bestMove, player);

    // return best move
    return bestMove;

}

// ---------------------------------------------
// FLATTEN MOVES
// ---------------------------------------------
vector<Move> flatten(Board &board, int color){ // 1 = black, 2 = white
    vector<vector<Move>> moves = board.getAllPossibleMoves(color);
    // check if moves is empty
    if(moves.empty()){
        return vector<Move>();
    }

    vector<Move> flattened = moves[0];
    int size = moves.size();
    // go through and insert moves
    for(int i = 1; i < size; i++){
        flattened.insert(flattened.end(), moves[i].begin(), moves[i].end());
    }

    return flattened;
}

// ---------------------------------------------
// CHECK WINNER
// ---------------------------------------------
int isThereWinner(Board &board, int lastPlayer){
    int r = board.isWin(lastPlayer);

    if(r == 1 || r == 2) { return r; }     // winner id
    else if (r == -1) { return 0; }         // tie 
    else { return -1; }                     // game continues
}

// ---------------------------------------------
// UCT (Upper Confidence for Trees)
// ---------------------------------------------
double UCT(const MCTSNode &node, int parentVisits, double C){
    // if node is unvisited, UCT is infinity
    if(node.visits == 0){
        return INFINITY;
    }
    double winRate = double(node.wins) / double(node.visits);
    double exploration = C * sqrt((log(parentVisits + 1) / node.visits));
    
    return winRate + exploration;
}

// ---------------------------------------------
// EVALUATION HEURISTIC
// ---------------------------------------------
double evaluatePlayer(Board &board, int player){
    // establish colors of player and opponent
    string playerColor = (player == 1 ? "B" : "W");
    string opponentColor = (player == 1 ? "W" : "B");

    // establish opponent player
    int opponent = (player == 1 ? 2 : 1);

    // establish player and opponent's scores
    double playerScore = 0.0;
    double opponentScore = 0.0;

    int rows = board.row;
    int cols = board.col;

    // material score
    for(int i = 0; i < rows; ++i){
        for(int j = 0; j < cols; ++j){
            Checker checker = board.board[i][j];
            // no checker there, continue
            if(checker.color == ".") { continue; }

            // check if checker is a king
            bool isKing = checker.isKing;

            if(checker.color == playerColor){
                playerScore += (isKing ? 0.4 : 0.1);
            }
            else if(checker.color == opponentColor){
                opponentScore += (isKing ? 0.4 : 0.1);
            }
        }
    }

    // mobility score
    vector<Move> playerMoves = flatten(board, player);
    vector<Move> opponentMoves = flatten(board, opponent);
    playerScore += 0.1 * playerMoves.size();
    opponentScore += 0.1 * opponentMoves.size();

    double diff = playerScore - opponentScore;
    double big = 0.5;
    double small = 0.2;
    
    if (diff >= big)            { return 0.9; } // big lead
    else if (diff >= small)     { return 0.7; } // small lead
    else if (diff > -small)     { return 0.5; } // roughly equal
    else if (diff > -big)       { return 0.3; } // small disadvantage
    else                        { return 0.1; } // big disadvantage
}

// ---------------------------------------------
// SELECT CHILD
// ---------------------------------------------
MCTSNode* selectChild(MCTSNode *node){
    double maxUCT = -INFINITY;
    MCTSNode *bestChild = nullptr;

    int parentVisits = node->visits;

    for(MCTSNode *child : node->children){
        double uct = UCT(*child, parentVisits);
        if(uct > maxUCT){
            maxUCT = uct;
            bestChild = child;
        }
    }
    return bestChild;
}

// ---------------------------------------------
// EXPAND NODE
// ---------------------------------------------
MCTSNode* expandNode(MCTSNode *node, Board &simBoard, int &currentPlayer){
    Move move = node->untriedMoves.back(); // last move
    node->untriedMoves.pop_back(); // remove move

    // apply move to simBoard
    simBoard.makeMove(move, currentPlayer);

    MCTSNode *child = new MCTSNode();
    child->parent = node;
    child->actionToGetHere = move;

    // switch players
    currentPlayer = (currentPlayer == 1 ? 2 : 1);
    child->currPlayer = currentPlayer;

    // moves from new position
    child->untriedMoves = flatten(simBoard, child->currPlayer);
    child->visits = 0;
    child->wins = 0.0;

    node->children.push_back(child);
    return child;
}

// ---------------------------------------------
// ROLLOUT
// ---------------------------------------------
double rollout(Board &simBoard, int currentPlayer, int myPlayer){
    for(int i = 0; i < MAX_ROLLOUT_PLIES; ++i){
        // generate all legal moves for currentPlayer
        vector<Move> legalMoves = flatten(simBoard, currentPlayer);
        int legalMovesSize = legalMoves.size();

        // if no legal moves for myPlayer...
        if(legalMovesSize == 0 && currentPlayer == myPlayer){
            // ... myPlayer loses, return 0.0
            return 0.0;
        }
        // if no legal moves for myPlayer's opponent...
        else if(legalMovesSize == 0 && currentPlayer != myPlayer){
            // ... myPlayer wins, return 1.0
            return 1.0;
        }

        // choose random move and play it
        int randIndex = std::rand() % legalMoves.size();
        Move randomMove = legalMoves[randIndex];
        simBoard.makeMove(randomMove, currentPlayer);

        // check if node is at a winning state
        int winner = isThereWinner(simBoard, currentPlayer);
        if(winner != -1){
            if(winner == myPlayer) { return 1.0; } // if myPlayer won, return 1.0
            else if(winner == 0) { return 0.5; } // tie case
            else { return 0.0; }
        }

        // switch to opponent
        currentPlayer = (currentPlayer == 1 ? 2 : 1);
    }

    // max-depth reached, so evaluate board based on myPlayer
    return evaluatePlayer(simBoard, myPlayer);
}

// ---------------------------------------------
// BACK PROPAGATION
// ---------------------------------------------
void backprop(MCTSNode *node, double result){
    while(node != nullptr){
        node->visits += 1;
        node->wins += result;
        node = node->parent;
    }
}

