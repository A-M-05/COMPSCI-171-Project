#include "StudentAI.h"
#include <random>
#include <vector>

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
    } else{
        board.makeMove(move,player == 1?2:1);
    }

    // set up MCTS Node for root node
    MCTSNode *root = new MCTSNode();
    root->board = board;
    root->parent = nullptr;
    root->currPlayer = player;
    root->untriedMoves = flatten(board, player);

    MCTSNode *node = root;

    // selection
    while(!node->untriedMoves.empty() && !node->children.empty()){
        node = selectChild(node);
    }

    // expansion
    if(!node->untriedMoves.empty()){
        node = expandNode(node);
    }
    
    // return empty move for now
    return Move();

}

MCTSNode* expandNode(MCTSNode *node){
    if(node->untriedMoves.empty()){
        return node;
    }

    Move move = node->untriedMoves.back(); // last move
    node->untriedMoves.pop_back(); // remove move

    MCTSNode *child = new MCTSNode();
    child->parent = node;
    child->actionToGetHere = move;

    child->board = node->board;
    child->board.makeMove(move, node->currPlayer); // who moved
    child->currPlayer = (node->currPlayer == 1 ? 2 : 1); // next player to move

    child->untriedMoves = flatten(child->board, child->currPlayer);

    node->children.push_back(child);

    return child;
}

bool isThereWinner(Board &board){
    if (board.isWin(1) == 1 || board.isWin(1) == 2 || board.isWin(2) == 1 || board.isWin(2) == 2){
        return true;
    }
    return false;
}

vector<Move> flatten(Board &board, int color){ // 1 = black, 2 = white
    vector<vector<Move>> moves = board.getAllPossibleMoves(color);
    vector<Move> flattened = moves[0];
    if (moves.size() == 1){
        return moves[0];
    }
    int size = moves.size();
    for(int i = 1; i < size; i++){
        flattened.insert( flattened.end(), moves[i].begin(), moves[i].end() );
    }
    return flattened;
}

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

double UCT(const MCTSNode &node, int parentVisits, double C = 1.4){
    // if node is unvisited, UCT is infinity
    if(node.visits == 0){
        return INFINITY;
    }
    double winRate = double(node.wins) / double(node.visits);
    double exploration = C * sqrt((log(parentVisits + 1) / node.visits));
    
    return winRate + exploration;
}

int rollout(MCTSNode node){

}


