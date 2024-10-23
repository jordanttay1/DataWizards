import chess.engine
import chess.pgn
import json
import asyncio
import io
import matplotlib.pyplot as plt
import numpy as np

# Set the event loop policy for Windows
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Initialize the Stockfish engine
# https://stockfishchess.org/download/
engine = chess.engine.SimpleEngine.popen_uci('Brandon/stockfish-engine/stockfish/stockfish-windows-x86-64-avx2.exe')

# Load your JSON file
with open('Brandon/brandonritchie99.json', 'r') as file:
    data = json.load(file)

# Get the PGN string from the JSON
pgn_string = data[-1]['games'][0]['pgn']
pgn = io.StringIO(pgn_string)

# Read the game
game = chess.pgn.read_game(pgn)

# Initialize a chess board
board = game.board()  # Starting from the initial position

# Lists to hold evaluations for each player
white_evaluations = []
black_evaluations = []

# Iterate over the moves and evaluate each position
for i, move in enumerate(game.mainline_moves()):
    move_san = board.san(move)
    board.push(move)  # Make the move on the board
    
    # Evaluate the position using Stockfish
    info = engine.analyse(board, chess.engine.Limit(time=0.1))
    evaluation = info["score"].relative.score()  # Score from White's perspective

    # Store the evaluation based on whose turn it is
    if board.turn == chess.WHITE:  # If it's White's turn, previous move was Black's
        black_evaluations.append(evaluation)
    else:  # If it's Black's turn, previous move was White's
        white_evaluations.append(evaluation)

# Close the Stockfish engine
engine.quit()

# Plotting the distributions of evaluations
plt.figure(figsize=(12, 6))

# Plot for White's evaluations
plt.subplot(1, 2, 1)
plt.hist(white_evaluations, bins=np.arange(-600, 600, 50), alpha=0.7, color='blue')
plt.title("Distribution of Move Evaluations (White)")
plt.xlabel("Evaluation Score")
plt.ylabel("Frequency")
plt.xlim(-600, 600)

# Plot for Black's evaluations
plt.subplot(1, 2, 2)
plt.hist(black_evaluations, bins=np.arange(-600, 600, 50), alpha=0.7, color='red')
plt.title("Distribution of Move Evaluations (Black)")
plt.xlabel("Evaluation Score")
plt.xlim(-600, 600)

plt.tight_layout()
plt.show()
