import sys
import termios
import tty

class InputHandler:
    def __init__(self):
        self.key_mappings = {
            'w': 'up',
            'a': 'left', 
            's': 'down',
            'd': 'right',
            'q': 'quit',
            '\x1b[A': 'up',    # Arrow up
            '\x1b[B': 'down',  # Arrow down
            '\x1b[C': 'right', # Arrow right
            '\x1b[D': 'left',  # Arrow left
        }
    
    def get_key(self):
        """Get a single keypress from user"""
        try:
            # Save terminal settings
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            # Set terminal to raw mode
            tty.setraw(fd)
            
            # Read key
            key = sys.stdin.read(1)
            
            # Handle arrow keys (escape sequences)
            if key == '\x1b':
                key += sys.stdin.read(2)
            
            return key
        
        except:
            # Fallback for systems that don't support termios
            return input().lower().strip()
        
        finally:
            # Restore terminal settings
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except:
                pass
    
    def get_action(self):
        """Get user action"""
        while True:
            key = self.get_key()
            action = self.key_mappings.get(key.lower())
            
            if action:
                return action
            else:
                print(f"Invalid key: {key}. Use W/A/S/D or arrow keys.")
