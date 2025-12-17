import torch
import torch.nn as nn

class SimpleCircuitAI(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(5, 10)
        self.layer2 = nn.Linear(10, 10)
        self.layer3 = nn.Linear(10, 5)
    
    def forward(self, x):
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        x = self.layer3(x)
        return x

# TEST
if __name__ == "__main__":
    ai = SimpleCircuitAI()
    print("AI Created!")
    test_input = torch.tensor([[1.0, 2.0, 0.5, 3.0, 1.0]])
    print(f"Test output: {ai(test_input)}")