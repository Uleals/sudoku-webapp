import random
import mysql.connector
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host='Isi host lu',
        user='Isi user lu',
        password='Ya isi pw nya lah',
        database='Yahh mau tau db gw yakk, table nya aja dah'
    )

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
    for _ in range(9):
        r, c = random.randint(0, 8), random.randint(0, 8)
        num = random.randint(1, 9)
        if is_valid(board, r, c, num):
            board[r][c] = num
    
    solve(board)
    return board

def create_puzzle(solution):
    puzzle = [row[:] for row in solution]
    attempts = random.randint(40, 60)
    for _ in range(attempts):
        r, c = random.randint(0, 8), random.randint(0, 8)
        puzzle[r][c] = 0
    return puzzle

@app.route('/')
def index():
    solution = generate_sudoku()
    puzzle = create_puzzle(solution)
    puzzle_str = ''.join(str(num) if num != 0 else '0' for row in puzzle for num in row)
    solution_str = ''.join(str(num) for row in solution for num in row)
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
