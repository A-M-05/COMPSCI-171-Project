#ifndef STUDENTAI_H
#define STUDENTAI_H
#include "AI.h"
#include "Board.h"
#include <cmath>
#include <vector>
#pragma once

//The following part should be completed by students.
//Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI :public AI
{
public:
    Board board;
	StudentAI(int col, int row, int p);
	virtual Move GetMove(Move board);
};

MCTSNode* selectChild(MCTSNode *node);
float UCT(MCTSNode &node, int parentVisits, float C  = 1.4);


bool isThereWinner(Board &board);
int rollout(MCTSNode node);
void backprop();
vector<Move> flatten(Board &board, int color); // white is 2, black is 1


/*
 mcts
 each node has a parent
 visted value
 win value 
 action leading to value
 children nodes
 untried moves
*/
struct MCTSNode{
    Board board;

    MCTSNode *parent; // parent node
    vector<MCTSNode*> children; // children
    
    Move actionToGetHere;
    vector<Move> untriedMoves;
    
    int currPlayer; // black is 1, white is 2

    int visits = 0;
    double wins = 0.0;

    bool terminal = false;
    bool fullyExpanded = false;
};

#endif //STUDENTAI_H;
