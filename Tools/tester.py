import subprocess
import time   # <-- add this

NUM_GAMES = 100
player1_wins = 0
player2_wins = 0
ties = 0
total_time = 0

for i in range(NUM_GAMES):
    print(f"--- Game {i+1}/{NUM_GAMES} ---")

    start = time.time()   # <-- START TIMER

    result = subprocess.run(
        [
            "python3", "AI_Runner.py",
            "8", "8", "3", "l",
            "../src/checkers-cpp/main",  
            "Sample_AIs/Average_AI/main.py"
        ],
        capture_output=True,
        text=True
    )
    

    end = time.time()     # <-- END TIMER
    elapsed = end - start
    total_time += elapsed
    print(f"Game time: {elapsed:.2f} seconds")   # <-- print time

    output = result.stdout.lower()
    error_output = result.stderr

    if "player 1 wins" in output:
        print("player 1 wins")
        player1_wins += 1
    elif "player 2 wins" in output:
        print("player 2 wins")
        player2_wins += 1
    elif "tie" in output:
        print("tie")
        ties += 1
    elif "crashed" in output or "exception" in output:  # FIX YOUR BUGGY CONDITION
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

print(f"Average game time: {total_time / NUM_GAMES:.2f} seconds")
