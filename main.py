#!/usr/bin/env python3

from game2048 import Game2048
from display import GameDisplay
from input_handler import InputHandler

def main():
    """Main game loop"""
    game = Game2048()
    display = GameDisplay()
    input_handler = InputHandler()
    
    print("Welcome to 2048!")
    print("Reach the 2048 tile to win!")
    input("Press Enter to start...")
    
    while True:
        # Display current state
        display.print_board(game)
        
        # Check win/lose conditions
        if game.is_won():
            display.print_game_over(game)
            play_again = input("You won! Play again? (y/n): ").lower()
            if play_again == 'y':
                game = Game2048()
                continue
            else:
                break
        
        if not game.can_move():
            display.print_game_over(game)
            play_again = input("Play again? (y/n): ").lower()
            if play_again == 'y':
                game = Game2048()
                continue
            else:
                break
        
        # Show instructions
        display.print_instructions()
        
        # Get user input
        action = input_handler.get_action()
        
        if action == 'quit':
            print("Thanks for playing!")
            break
        
        # Execute move
        moved = False
        if action == 'left':
            moved = game.move_left()
        elif action == 'right':
            moved = game.move_right()
        elif action == 'up':
            moved = game.move_up()
        elif action == 'down':
            moved = game.move_down()
        
        # Add new tile if move was successful
        if moved:
            game.add_new_tile()

if __name__ == "__main__":
    main()
