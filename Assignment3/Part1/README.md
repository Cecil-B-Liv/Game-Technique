# GridWorld Q-Learning

Reinforcement learning implementation for gridworld navigation using Q-Learning.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run Level 0
python main.py
```

## 📁 Project Structure

```
gridworld_rl/
├── config/
│   └── config_level0.json    # Training hyperparameters
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration loader
│   ├── constants.py          # Game constants and levels
│   ├── environment. py        # GridWorld environment
│   ├── q_table.py            # Q-table implementation
│   ├── agent.py              # Q-Learning agent
│   ├── renderer.py           # Pygame visualization
│   └── trainer.py            # Training loop
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## 🎮 Controls

- **V**: Toggle between visual mode (30 FPS) and fast mode (240 FPS)
- **R**: Reset Q-table and restart training
- **ESC**:  Quit

## 🎯 Features

- ✅ Modular, organized codebase
- ✅ Q-Learning with epsilon-greedy policy
- ✅ Random tie-breaking
- ✅ Linear epsilon decay
- ✅ Visual Pygame rendering
- ✅ Multiple levels (0-5)
- ✅ Support for apples, keys, chests, rocks, fire, monsters

## 📊 Levels

- **Level 0**: Basic apple collection
- **Level 1**:  Apples with fire hazards
- **Level 2**:  Apples + key + chest
- **Level 3**:  Complex key-chest puzzle
- **Level 4**:  Monsters (moving obstacles)
- **Level 5**: Full complexity

## 🔧 Configuration

Edit `config/config_level0.json`:

```json
{
  "episodes": 800,
  "alpha": 0.2,
  "gamma": 0.95,
  "epsilonStart": 1.0,
  "epsilonEnd": 0.05,
  "epsilonDecayEpisodes": 700
}
```

## 📚 Code Overview

### `environment.py`
- GridWorld class
- State encoding
- Step mechanics (movement, rewards, monsters)

### `agent.py`
- QLearningAgent class
- Epsilon-greedy action selection
- Q-value updates

### `q_table.py`
- Sparse Q-table storage
- Random tie-breaking support

### `renderer.py`
- Pygame visualization
- HUD display

### `trainer.py`
- Training loop
- Event handling
- Episode management

## 🐛 Troubleshooting

**Import errors**:  Make sure you're running from the project root directory

**Pygame not found**: `pip install pygame`

**Slow learning**: Adjust alpha, gamma, or epsilon decay schedule in config

## 📝 License

MIT