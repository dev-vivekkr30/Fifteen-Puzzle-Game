from flask import Flask, jsonify, render_template
import random
import heapq
from copy import deepcopy

app = Flask(__name__)

# Initialize a solved puzzle state
puzzle = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 0]
]

class Node:
    def __init__(self, puzzle, empty_pos, g, parent=None):
        self.puzzle = puzzle
        self.empty_pos = empty_pos
        self.g = g
        self.parent = parent
        self.h = self.manhattan_distance()
    
    def manhattan_distance(self):
        distance = 0
        for i in range(4):
            for j in range(4):
                value = self.puzzle[i][j]
                if value == 0:
                    continue
                target_x = (value - 1) // 4
                target_y = (value - 1) % 4
                distance += abs(i - target_x) + abs(j - target_y)
        return distance
    
    @property
    def f(self):
        return self.g + self.h
    
    def __lt__(self, other):
        return self.f < other.f

def is_solvable(puzzle):
    flat_puzzle = [tile for row in puzzle for tile in row if tile != 0]
    inversion_count = sum(
        1 for i in range(len(flat_puzzle)) for j in range(i + 1, len(flat_puzzle))
        if flat_puzzle[i] > flat_puzzle[j]
    )
    return inversion_count % 2 == 0

def shuffle_puzzle():
    global puzzle
    flat_puzzle = [tile for row in puzzle for tile in row]
    random.shuffle(flat_puzzle)
    while not is_solvable([flat_puzzle[i:i + 4] for i in range(0, 16, 4)]):
        random.shuffle(flat_puzzle)
    puzzle = [flat_puzzle[i:i + 4] for i in range(0, 16, 4)]

def find_empty_tile(puzzle):
    for i in range(4):
        for j in range(4):
            if puzzle[i][j] == 0:
                return i, j

def can_move(puzzle, row, col):
    empty_row, empty_col = find_empty_tile(puzzle)
    return (abs(empty_row - row) == 1 and empty_col == col) or (abs(empty_col - col) == 1 and empty_row == row)

def move_tile(puzzle, row, col):
    empty_row, empty_col = find_empty_tile(puzzle)
    puzzle[empty_row][empty_col], puzzle[row][col] = puzzle[row][col], puzzle[empty_row][empty_col]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shuffle')
def shuffle():
    shuffle_puzzle()
    return jsonify({'puzzle': puzzle})

@app.route('/move/<int:row>/<int:col>')
def move(row, col):
    if can_move(puzzle, row, col):
        move_tile(puzzle, row, col)
    return jsonify({'puzzle': puzzle})

def generate_children(node):
    children = []
    x, y = node.empty_pos
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < 4 and 0 <= new_y < 4:
            new_puzzle = deepcopy(node.puzzle)
            new_puzzle[x][y], new_puzzle[new_x][new_y] = new_puzzle[new_x][new_y], new_puzzle[x][y]
            child = Node(new_puzzle, (new_x, new_y), node.g + 1, node)
            children.append(child)
    return children

def solve_puzzle(initial_puzzle):
    initial_empty_pos = find_empty_tile(initial_puzzle)
    root = Node(initial_puzzle, initial_empty_pos, 0)
    
    frontier = []
    heapq.heappush(frontier, root)
    explored = set()
    
    while frontier:
        current_node = heapq.heappop(frontier)
        explored.add(tuple(map(tuple, current_node.puzzle)))
        
        if current_node.h == 0:  # Goal test
            return current_node
        
        for child in generate_children(current_node):
            if tuple(map(tuple, child.puzzle)) not in explored:
                heapq.heappush(frontier, child)
    
    return None  # No solution found

@app.route('/help')
def help_move():
    solution_node = solve_puzzle(deepcopy(puzzle))
    if not solution_node:
        return jsonify({'error': 'No solution found'})
    
    next_move = solution_node
    while next_move.parent and next_move.parent.parent:
        next_move = next_move.parent
    
    empty_row, empty_col = find_empty_tile(puzzle)
    move_row, move_col = find_empty_tile(next_move.puzzle)
    
    return jsonify({'move': [move_row, move_col], 'puzzle': puzzle})

if __name__ == '__main__':
    app.run(debug=True)
