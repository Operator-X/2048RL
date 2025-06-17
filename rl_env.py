import gymnasium as gym
from gymnasium import spaces
import numpy as np
from game2048 import Game2048

class Game2048RLEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.game = Game2048()
        
        # Action space: 0=left, 1=up, 2=right, 3=down
        self.action_space = spaces.Discrete(4)
        
        # State space: 4x4 grid with log2 encoding
        self.observation_space = spaces.Box(
            low=0, high=17, shape=(16,), dtype=np.float32
        )
        
        self.episode_count = 0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game = Game2048()
        self.episode_count += 1
        return self._get_observation(), {}
    
    def step(self, action):
        # Map actions
        actions = ['left', 'up', 'right', 'down']
        
        # Store previous state for reward calculation
        prev_score = self.game.score
        prev_max_tile = self.game.get_max_tile()
        prev_board = [row[:] for row in self.game.board]
        
        # Execute move
        if actions[action] == 'left':
            moved = self.game.move_left()
        elif actions[action] == 'up':
            moved = self.game.move_up()
        elif actions[action] == 'right':
            moved = self.game.move_right()
        elif actions[action] == 'down':
            moved = self.game.move_down()
        
        # Calculate enhanced reward
        reward = self._calculate_enhanced_reward(moved, prev_score, prev_max_tile, prev_board)
        
        # Add new tile if move was valid
        if moved:
            self.game.add_new_tile()
        
        # Check if game is done
        done = not self.game.can_move()
        
        # Additional info
        info = {
            'score': self.game.score,
            'max_tile': self.game.get_max_tile(),
            'moved': moved,
            'valid_actions': self.get_valid_actions()
        }
        
        return self._get_observation(), reward, done, False, info
    
    def _get_observation(self):
        """Convert board to log2 encoded flat array with additional features"""
        obs = np.zeros(16, dtype=np.float32)
        flat_board = np.array(self.game.board).flatten()
        
        for i, cell in enumerate(flat_board):
            if cell > 0:
                obs[i] = np.log2(cell)
        
        return obs
    
    def _calculate_enhanced_reward(self, moved, prev_score, prev_max_tile, prev_board):
        """Enhanced reward function to prevent getting stuck"""
        if not moved:
            return -1.0  # Strong penalty for invalid moves
        
        # Base reward for score increase
        score_increase = self.game.score - prev_score
        score_reward = score_increase * 0.01
        
        # Bonus for reaching higher tiles
        current_max = self.game.get_max_tile()
        tile_bonus = 0
        if current_max > prev_max_tile:
            tile_bonus = np.log2(current_max) * 50
        
        # Strategy-based rewards
        corner_bonus = self._corner_strategy_reward()
        smoothness_penalty = self._smoothness_penalty()
        monotonicity_bonus = self._monotonicity_bonus()
        empty_cells_bonus = self._empty_cells_bonus()
        
        # Adaptive reward based on training progress
        adaptive_bonus = self._adaptive_reward_bonus(score_increase)
        
        # Small survival bonus
        survival_bonus = 0.1
        
        total_reward = (score_reward + tile_bonus + corner_bonus + 
                       monotonicity_bonus + empty_cells_bonus + 
                       adaptive_bonus + survival_bonus - smoothness_penalty)
        
        return total_reward
    
    def _corner_strategy_reward(self):
        """Reward for keeping largest tile in corner"""
        max_tile = self.game.get_max_tile()
        corners = [
            self.game.board[0][0], self.game.board[0][3],
            self.game.board[3][0], self.game.board[3][3]
        ]
        if max_tile in corners:
            return 5.0
        
        # Smaller reward for keeping it on edges
        edges = (list(self.game.board[0]) + list(self.game.board[3]) + 
                [self.game.board[i][0] for i in range(4)] + 
                [self.game.board[i][3] for i in range(4)])
        if max_tile in edges:
            return 2.0
        
        return 0
    
    def _smoothness_penalty(self):
        """Penalty for having scattered tiles"""
        penalty = 0
        for i in range(4):
            for j in range(4):
                if self.game.board[i][j] != 0:
                    neighbors = []
                    for di, dj in [(0,1), (0,-1), (1,0), (-1,0)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < 4 and 0 <= nj < 4 and self.game.board[ni][nj] != 0:
                            neighbors.append(self.game.board[ni][nj])
                    
                    for neighbor in neighbors:
                        diff = abs(np.log2(self.game.board[i][j]) - np.log2(neighbor))
                        if diff > 2:
                            penalty += diff * 0.1
        return penalty
    
    def _monotonicity_bonus(self):
        """Bonus for maintaining monotonic rows/columns"""
        bonus = 0
        
        # Check rows
        for row in self.game.board:
            non_zero = [x for x in row if x > 0]
            if len(non_zero) > 1:
                if all(non_zero[i] >= non_zero[i+1] for i in range(len(non_zero)-1)) or \
                   all(non_zero[i] <= non_zero[i+1] for i in range(len(non_zero)-1)):
                    bonus += 2.0
        
        # Check columns
        for j in range(4):
            col = [self.game.board[i][j] for i in range(4)]
            non_zero = [x for x in col if x > 0]
            if len(non_zero) > 1:
                if all(non_zero[i] >= non_zero[i+1] for i in range(len(non_zero)-1)) or \
                   all(non_zero[i] <= non_zero[i+1] for i in range(len(non_zero)-1)):
                    bonus += 2.0
        
        return bonus
    
    def _empty_cells_bonus(self):
        """Bonus for maintaining empty cells"""
        empty_count = sum(row.count(0) for row in self.game.board)
        return empty_count * 0.5
    
    def _adaptive_reward_bonus(self, score_increase):
        """Adaptive reward that changes based on training progress"""
        if self.episode_count < 1000:
            # Early training: focus on basic moves and merges
            return score_increase * 0.1
        elif self.episode_count < 5000:
            # Mid training: focus on score improvement
            return score_increase * 0.05
        else:
            # Late training: focus on strategy
            return score_increase * 0.02
    
    def get_valid_actions(self):
        """Get list of valid actions that would change the board"""
        valid_actions = []
        current_board = [row[:] for row in self.game.board]
        
        test_game = Game2048()
        for action in range(4):
            test_game.board = [row[:] for row in current_board]
            
            if action == 0:  # left
                moved = test_game.move_left()
            elif action == 1:  # up
                moved = test_game.move_up()
            elif action == 2:  # right
                moved = test_game.move_right()
            elif action == 3:  # down
                moved = test_game.move_down()
            
            if moved:
                valid_actions.append(action)
        
        return valid_actions if valid_actions else [0]  # Fallback to prevent empty list
    
    def render(self, mode='human'):
        if mode == 'human':
            print(f"Score: {self.game.score}")
            print(f"Episode: {self.episode_count}")
            for row in self.game.board:
                print(" ".join(f"{cell:4d}" if cell != 0 else "   ." for cell in row))
            print()
