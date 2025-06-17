from rl_env import Game2048RLEnv
from stable_baselines3 import DQN
import time
import numpy as np

def test_trained_agent():
    # Load trained model
    env = Game2048RLEnv()
    
    try:
        model = DQN.load("dqn_2048_enhanced")
        print("Loaded enhanced model")
    except:
        try:
            model = DQN.load("dqn_2048")
            print("Loaded basic model")
        except:
            print("No trained model found! Train the model first.")
            return
    
    # Test statistics
    scores = []
    max_tiles = []
    games_won = 0
    
    # Test for multiple episodes
    num_test_episodes = 10
    
    for episode in range(num_test_episodes):
        obs, info = env.reset()
        done = False
        step_count = 0
        invalid_moves = 0
        
        print(f"\n=== Episode {episode + 1}/{num_test_episodes} ===")
        env.render()
        
        while not done and step_count < 1000:  # Prevent infinite loops
            # Get valid actions
            valid_actions = env.get_valid_actions()
            
            # Predict action
            action, _ = model.predict(obs, deterministic=True)
            
            # Check if action is valid
            if action not in valid_actions:
                print(f"Invalid action {action}, valid actions: {valid_actions}")
                action = valid_actions[0]  # Use first valid action
                invalid_moves += 1
            
            obs, reward, done, truncated, info = env.step(action)
            
            step_count += 1
            action_names = ['LEFT', 'UP', 'RIGHT', 'DOWN']
            print(f"Step {step_count}: {action_names[action]}, Reward: {reward:.2f}, Score: {info['score']}")
            
            env.render()
            time.sleep(0.3)  # Pause to watch the game
            
            if done or truncated:
                final_score = info['score']
                final_max_tile = info['max_tile']
                
                scores.append(final_score)
                max_tiles.append(final_max_tile)
                
                if final_max_tile >= 2048:
                    games_won += 1
                    print("🎉 WON! Reached 2048!")
                
                print(f"Game Over! Final Score: {final_score}, Max Tile: {final_max_tile}")
                print(f"Steps taken: {step_count}, Invalid moves: {invalid_moves}")
                break
    
    # Print statistics
    print(f"\n{'='*50}")
    print("TESTING RESULTS:")
    print(f"{'='*50}")
    print(f"Games played: {num_test_episodes}")
    print(f"Games won (2048+): {games_won}")
    print(f"Win rate: {games_won/num_test_episodes*100:.1f}%")
    print(f"Average score: {np.mean(scores):.2f}")
    print(f"Best score: {max(scores)}")
    print(f"Average max tile: {np.mean(max_tiles):.2f}")
    print(f"Best max tile: {max(max_tiles)}")
    
    # Tile achievement breakdown
    tile_counts = {}
    for tile in max_tiles:
        tile_counts[tile] = tile_counts.get(tile, 0) + 1
    
    print(f"\nMax tile achievements:")
    for tile in sorted(tile_counts.keys(), reverse=True):
        print(f"  {tile}: {tile_counts[tile]} games ({tile_counts[tile]/num_test_episodes*100:.1f}%)")

def test_single_game_detailed():
    """Test a single game with detailed move-by-move analysis"""
    env = Game2048RLEnv()
    
    try:
        model = DQN.load("dqn_2048_enhanced")
    except:
        model = DQN.load("dqn_2048")
    
    obs, info = env.reset()
    done = False
    step_count = 0
    
    print("=== DETAILED SINGLE GAME ANALYSIS ===")
    env.render()
    
    while not done and step_count < 500:
        valid_actions = env.get_valid_actions()
        action, _ = model.predict(obs, deterministic=True)
        
        print(f"\nStep {step_count + 1}:")
        print(f"Valid actions: {[['LEFT', 'UP', 'RIGHT', 'DOWN'][a] for a in valid_actions]}")
        print(f"Agent chose: {['LEFT', 'UP', 'RIGHT', 'DOWN'][action]}")
        
        if action not in valid_actions:
            print("⚠️  INVALID MOVE! Using first valid action instead.")
            action = valid_actions[0]
        
        obs, reward, done, truncated, info = env.step(action)
        
        print(f"Reward: {reward:.2f}")
        print(f"Score: {info['score']}")
        print(f"Max tile: {info['max_tile']}")
        
        env.render()
        
        step_count += 1
        
        if done or truncated:
            print(f"\nGame ended after {step_count} steps")
            print(f"Final score: {info['score']}")
            print(f"Final max tile: {info['max_tile']}")
            break
        
        input("Press Enter for next move...")

if __name__ == "__main__":
    print("Choose testing mode:")
    print("1. Test multiple games (statistics)")
    print("2. Test single game (detailed)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        test_single_game_detailed()
    else:
        test_trained_agent()
