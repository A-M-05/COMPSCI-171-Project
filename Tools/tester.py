import subprocess

NUM_GAMES = 100
player1_wins = 0
player2_wins = 0
ties = 0

for i in range(NUM_GAMES):
    print(f"--- Game {i+1}/{NUM_GAMES} ---")

    # Run AI_Runner.py as a subprocess
    result = subprocess.run(
        [
            "python3", "AI_Runner.py",
            "8", "8", "3", "l",    # 8x8 board, 2-player local
            "../src/checkers-python/main.py",  # Player 1: your AI
            "Sample_AIs/Random_AI/main.py"     # Player 2: opponent
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout.lower()
    error_output = result.stderr

    # Debug if needed
    print(output)

    if "player 1 wins" in output:
        player1_wins += 1
    elif "player 2 wins" in output:
        player2_wins += 1
    elif "tie" in output:
        ties += 1
    elif "crashed" in output:
        print("Crashed!", i+1)
        if error_output:
            print("stderr:\n", error_output)
    else:
        print(f"UNEXPECTED OUTPUT IN GAME {i+1}:")
        print(result.stdout)
        if error_output:
            print("stderr:\n", error_output)

# Compute percentages
print("\n========== RESULTS ==========")
print(f"Total games: {NUM_GAMES}")
print(f"Player 1 wins: {player1_wins} ({player1_wins / NUM_GAMES * 100:.1f}%)")
print(f"Player 2 wins: {player2_wins} ({player2_wins / NUM_GAMES * 100:.1f}%)")
print(f"Ties: {ties} ({ties / NUM_GAMES * 100:.1f}%)")

