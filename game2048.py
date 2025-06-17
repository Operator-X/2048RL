import random
import numpy as np

class Game2048:
    def __init__(self):
        self.size = 4
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()
    
    def add_new_tile(self):
        """Add a new tile (2 or 4) to a random empty cell"""
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4
    
    def move_left(self):
        """Move all tiles to the left"""
        moved = False
        for i in range(self.size):
            # Filter out zeros
            row = [cell for cell in self.board[i] if cell != 0]
            
            # Merge adjacent equal tiles
            merged_row = []
            j = 0
            while j < len(row):
                if j < len(row) - 1 and row[j] == row[j + 1]:
                    merged_row.append(row[j] * 2)
                    self.score += row[j] * 2
                    j += 2
                else:
                    merged_row.append(row[j])
                    j += 1
            
            # Pad with zeros
            merged_row += [0] * (self.size - len(merged_row))
            
            # Check if row changed
            if merged_row != self.board[i]:
                moved = True
            
            self.board[i] = merged_row
        
        return moved
    
    def move_right(self):
        """Move all tiles to the right"""
        # Reverse, move left, reverse back
        for i in range(self.size):
            self.board[i] = self.board[i][::-1]
        moved = self.move_left()
        for i in range(self.size):
            self.board[i] = self.board[i][::-1]
        return moved
    
    def move_up(self):
        """Move all tiles up"""
        # Transpose, move left, transpose back
        self.board = list(map(list, zip(*self.board)))
        moved = self.move_left()
        self.board = list(map(list, zip(*self.board)))
        return moved
    
    def move_down(self):
        """Move all tiles down"""
        # Transpose, move right, transpose back
        self.board = list(map(list, zip(*self.board)))
        moved = self.move_right()
        self.board = list(map(list, zip(*self.board)))
        return moved
    
    def can_move(self):
        """Check if any move is possible"""
        # Check for empty cells
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return True
        
        # Check for possible merges
        for i in range(self.size):
            for j in range(self.size):
                current = self.board[i][j]
                # Check right neighbor
                if j < self.size - 1 and self.board[i][j + 1] == current:
                    return True
                # Check bottom neighbor
                if i < self.size - 1 and self.board[i + 1][j] == current:
                    return True
        
        return False
    
    def is_won(self):
        """Check if player has reached 2048"""
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 2048:
                    return True
        return False
    
    def get_max_tile(self):
        """Get the maximum tile value"""
        return max(max(row) for row in self.board)
