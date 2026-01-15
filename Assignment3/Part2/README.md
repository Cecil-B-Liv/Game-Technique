# Train directional agent
python training/train_directional.py
# Saves to:  ./models/directional/best_model.zip

# Train rotation agent  
python training/train_rotation.py
# Saves to: ./models/rotation/best_model.zip

# Evaluate directional (uses default path automatically)
python evaluation/evaluate_directional.py --mode eval

# Evaluate rotation (uses default path automatically)
python evaluation/evaluate_rotation.py --mode eval

# Play manually
python evaluation/evaluate_directional.py --mode play
python evaluation/evaluate_rotation.py --mode play

# TensorBoard (separate for each)
tensorboard --logdir ./logs/directional/tensorboard
tensorboard --logdir ./logs/rotation/tensorboard