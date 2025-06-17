import os
import sys

class GameDisplay:
    def __init__(self):
        self.colors = {
            0: '\033[0m',      # Default
            2: '\033[97m',     # White
            4: '\033[96m',     # Cyan
            8: '\033[95m',     # Magenta
            16: '\033[94m',    # Blue
            32: '\033[93m',    # Yellow
            64: '\033[92m',    # Green
            128: '\033[91m',   # Red
            256: '\033[35m',   # Purple
            512: '\033[36m',   # Cyan
            1024: '\033[33m',  # Yellow
            2048: '\033[31m',  # Red
        }
        self.reset_color = '\033[0m'
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_board(self, game):
        """Print the game board with colors"""
        self.clear_screen()
        print(f"Score: {game.score}")
        print(f"Max Tile: {game.get_max_tile()}")
        print()
        
        # Top border
        print("┌" + "─" * 7 + "┬" + "─" * 7 + "┬" + "─" * 7 + "┬" + "─" * 7 + "┐")
        
        for i in range(game.size):
            # Print row
            print("│", end="")
            for j in range(game.size):
                value = game.board[i][j]
                color = self.colors.get(value, self.colors[0])
                
                if value == 0:
                    cell_str = "       "
                else:
                    cell_str = f"{color}{value:^7}{self.reset_color}"
                
                print(cell_str, end="│")
            print()
            
            # Print separator (except for last row)
            if i < game.size - 1:
                print("├" + "─" * 7 + "┼" + "─" * 7 + "┼" + "─" * 7 + "┼" + "─" * 7 + "┤")
        
        # Bottom border
        print("└" + "─" * 7 + "┴" + "─" * 7 + "┴" + "─" * 7 + "┴" + "─" * 7 + "┘")
        print()
    
    def print_instructions(self):
        """Print game instructions"""
        print("Controls:")
        print("  W or ↑ - Move Up")
        print("  A or ← - Move Left") 
        print("  S or ↓ - Move Down")
        print("  D or → - Move Right")
        print("  Q - Quit")
        print()
    
    def print_game_over(self, game):
        """Print game over message"""
        print("=" * 40)
        if game.is_won():
            print("🎉 CONGRATULATIONS! YOU WON! 🎉")
        else:
            print("💀 GAME OVER! 💀")
        print(f"Final Score: {game.score}")
        print(f"Max Tile: {game.get_max_tile()}")
        print("=" * 40)
