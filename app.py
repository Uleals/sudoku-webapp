import random
import mysql.connector
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='uleals',  # replace with your MySQL username
        password='Uleals2708._',  # replace with your MySQL password
        database='sudoku_game'  # ensure this is your database name
    )

# Function to generate a random Sudoku grid
def generate_sudoku():
    def is_valid(board, r, c, num):
        for i in range(9):
            if board[r][i] == num or board[i][c] == num:
                return False
        start_row, start_col = 3 * (r // 3), 3 * (c // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if board[i][j] == num:
                    return False
        return True

    def solve(board):
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    for num in range(1, 10):
                        if is_valid(board, r, c, num):
                            board[r][c] = num
                            if solve(board):
                                return True
                            board[r][c] = 0
                    return False
        return True

    board = [[0] * 9 for _ in range(9)]
    for _ in range(9):  # Try to fill some cells randomly
        r, c = random.randint(0, 8), random.randint(0, 8)
        num = random.randint(1, 9)
        if is_valid(board, r, c, num):
            board[r][c] = num
    
    solve(board)
    return board

# Function to create a puzzle from the solution (by removing numbers)
def create_puzzle(solution):
    puzzle = [row[:] for row in solution]
    attempts = random.randint(40, 60)  # Number of cells to leave empty
    for _ in range(attempts):
        r, c = random.randint(0, 8), random.randint(0, 8)
        puzzle[r][c] = 0
    return puzzle

@app.route('/')
def index():
    # Generate random solution and puzzle
    solution = generate_sudoku()
    puzzle = create_puzzle(solution)
    
    # Flatten the puzzle to send to the HTML template
    puzzle_str = ''.join(str(num) if num != 0 else '0' for row in puzzle for num in row)
    
    # Save the solution as a string (you can store this in your database later)
    solution_str = ''.join(str(num) for row in solution for num in row)

    # Save puzzle and solution to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO puzzles (puzzle, solution) VALUES (%s, %s)', (puzzle_str, solution_str))
    conn.commit()
    puzzle_id = cursor.lastrowid
    conn.close()

    return render_template('index.html', puzzle=puzzle_str, puzzle_id=puzzle_id)

@app.route('/check_solution', methods=['POST'])
def check_solution():
    user_solution = request.form['solution']
    puzzle_id = request.form['puzzle_id']

   
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT solution FROM puzzles WHERE id = %s', (puzzle_id,))
    correct_solution = cursor.fetchone()[0]
    conn.close()

    if user_solution == correct_solution:
        return jsonify({'status': 'success', 'message': 'Correct solution!'})
    else:
        return jsonify({'status': 'error', 'message': 'Incorrect solution. Try again!'})

if __name__ == '__main__':
    app.run(debug=True)
