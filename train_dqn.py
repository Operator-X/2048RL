import gymnasium as gym
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback
from rl_env import Game2048RLEnv
import numpy as np
import matplotlib.pyplot as plt

class TrainingCallback(BaseCallback):
    def __init__(self, check_freq: int, verbose=1):
        super(TrainingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.scores = []
        self.max_tiles = []
        self.episode_rewards = []
        self.invalid_move_counts = []
        
    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:
            # Get info from the last episode
            if len(self.locals.get('infos', [])) > 0:
                info = self.locals['infos'][0]
                if 'score' in info:
                    self.scores.append(info['score'])
                    self.max_tiles.append(info['max_tile'])
                    
                    if len(self.scores) >= 100:
                        avg_score = np.mean(self.scores[-100:])
                        avg_max_tile = np.mean(self.max_tiles[-100:])
                        max_tile_achieved = max(self.max_tiles[-100:])
                        
                        print(f"Step {self.n_calls}:")
                        print(f"  Avg Score (last 100): {avg_score:.2f}")
                        print(f"  Avg Max Tile (last 100): {avg_max_tile:.2f}")
                        print(f"  Best Max Tile (last 100): {max_tile_achieved}")
                        print(f"  Exploration Rate: {self.model.exploration_rate:.3f}")
                        print("-" * 50)
        
        return True

def train_enhanced_dqn():
    # Create environment
    env = Game2048RLEnv()
    
    # Check if environment is valid
    check_env(env)
    
    # Create callback for monitoring
    callback = TrainingCallback(check_freq=5000)
    
    # Create enhanced DQN model
    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=5e-4,  # Higher learning rate
        buffer_size=200000,  # Larger buffer
        learning_starts=10000,  # Start learning after more steps
        batch_size=128,  # Larger batch size
        tau=1.0,
        gamma=0.95,  # Lower discount for immediate rewards
        train_freq=4,
        gradient_steps=2,  # More gradient steps per update
        target_update_interval=5000,  # More frequent target updates
        exploration_fraction=0.4,  # Longer exploration phase
        exploration_initial_eps=1.0,
        exploration_final_eps=0.1,  # Higher final exploration
        policy_kwargs=dict(
            net_arch=[512, 512, 256, 128],  # Larger network
            activation_fn=torch.nn.ReLU
        ),
        verbose=1,
        device='auto'  # Use GPU if available
    )
    
    print("Starting enhanced training...")
    print("This may take 2-6 hours depending on your hardware.")
    print("The agent should start showing better performance after ~50,000 steps.")
    
    # Train the model
    model.learn(
        total_timesteps=1000000,  # More training steps
        callback=callback,
        progress_bar=True
    )
    
    # Save the model
    model.save("dqn_2048_enhanced")
    
    print("Enhanced training completed!")
    print("Model saved as 'dqn_2048_enhanced'")
    
    # Plot training progress
    if len(callback.scores) > 0:
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.plot(callback.scores)
        plt.title('Training Scores')
        plt.xlabel('Episode')
        plt.ylabel('Score')
        
        plt.subplot(1, 3, 2)
        plt.plot(callback.max_tiles)
        plt.title('Max Tiles Achieved')
        plt.xlabel('Episode')
        plt.ylabel('Max Tile Value')
        
        plt.subplot(1, 3, 3)
        # Running average
        if len(callback.scores) >= 50:
            running_avg = [np.mean(callback.scores[max(0, i-49):i+1]) for i in range(len(callback.scores))]
            plt.plot(running_avg)
            plt.title('Running Average Score (50 episodes)')
            plt.xlabel('Episode')
            plt.ylabel('Average Score')
        
        plt.tight_layout()
        plt.savefig('training_progress.png')
        plt.show()

if __name__ == "__main__":
    import torch
    train_enhanced_dqn()
