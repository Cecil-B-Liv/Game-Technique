Command for running the code file:

Train directional agent
python training/train_directional.py
Saves to:  ./models/directional/best_model.zip

Train rotation agent  
python training/train_rotation.py
Saves to: ./models/rotation/best_model.zip

Option 1: Visual Evaluation (see agent play)
bash
python evaluation/evaluate_directional.py --mode eval --episodes 20
python evaluation/evaluate_rotation.py --mode eval --episodes 20
Option 2: Fast Evaluation (more accurate, no rendering)
bash
python evaluation/evaluate_directional.py --mode fast --episodes 50
python evaluation/evaluate_rotation. py --mode fast --episodes 50

Play manually
python evaluation/evaluate_directional.py --mode play
python evaluation/evaluate_rotation.py --mode play

TensorBoard (separate for each)
tensorboard --logdir ./logs/directional/tensorboard
tensorboard --logdir ./logs/rotation/tensorboard
tensorboard --logdir ./logs