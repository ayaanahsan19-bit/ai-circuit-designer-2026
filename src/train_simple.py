# FILE: src/train_simple.py
import torch
import torch.nn as nn
import torch.optim as optim
from models.simple_circuit_ai import SimpleCircuitAI

print("🎯 TRAINING AI...")

# Create AI
ai = SimpleCircuitAI()

# Fake training data (10 circuits)
inputs = torch.randn(10, 5)
targets = torch.randn(10, 3)

# Train
loss_fn = nn.MSELoss()
optimizer = optim.Adam(ai.parameters(), lr=0.01)

for step in range(20):
    optimizer.zero_grad()
    predictions = ai(inputs)
    loss = loss_fn(predictions, targets)
    loss.backward()
    optimizer.step()
    
    if (step + 1) % 5 == 0:
        print(f"Step {step+1}/20 | Loss: {loss.item():.4f}")

print("✅ Training Complete!")