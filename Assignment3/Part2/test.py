import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")  # Returns True for ROCm too
print(f"Device name: {torch.cuda.get_device_name(0)}")