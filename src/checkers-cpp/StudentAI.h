#ifndef STUDENTAI_H
#define STUDENTAI_H
#include "AI.h"
#include "Board.h"
#include <cmath>
#include <vector>
#include <random>

#define MAX_ROLLOUT_PLIES 20
#define MAX_ITERATIONS 1000
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

struct MCTSNode{
    MCTSNode *parent; // parent node
    vector<MCTSNode*> children; // children
    
    Move actionToGetHere;
    vector<Move> untriedMoves;

    int currPlayer; // black is 1, white is 2

    int visits = 0;
    double wins = 0.0;
};

vector<Move> flatten(Board &board, int color); // white is 2, black is 1

int isThereWinner(Board &board, int lastPlayer);

double UCT(const MCTSNode &node, int parentVisits, double C  = 1.4);

double evaluatePlayer(Board &board, int player);

MCTSNode* selectChild(MCTSNode *node);

MCTSNode* expandNode(MCTSNode *node, Board &simBoard, int &currentPlayer);

double rollout(Board &simBoard, int currentPlayer, int myPlayer);

void backprop(MCTSNode *node, double result);

#endif //STUDENTAI_H;
