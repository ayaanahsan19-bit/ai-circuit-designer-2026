# FILE: src/main.py - SIMPLE VERSION
print("=" * 40)
print("🔌 AI CIRCUIT DESIGNER 2026")
print("=" * 40)

# 1. Import the AI we'll create
from models.simple_circuit_ai import SimpleCircuitAI
import torch

print("✅ Step 1: Loading AI...")

# 2. Create AI
ai = SimpleCircuitAI()

# 3. Simple circuit example (5 parameters)
# [Voltage, Resistance, Capacitance, Frequency, Current]
example_circuit = torch.tensor([
    [5.0, 1000.0, 0.0001, 1000.0, 0.01]  # One circuit
])

print(f"\n📊 Step 2: Circuit Input (5 values):")
print(f"• Voltage: {example_circuit[0][0]:.1f}V")
print(f"• Resistance: {example_circuit[0][1]:.0f}Ω")
print(f"• Capacitance: {example_circuit[0][2]:.6f}F")
print(f"• Frequency: {example_circuit[0][3]:.0f}Hz")
print(f"• Current: {example_circuit[0][4]:.3f}A")

# 4. Get AI design
print("\n🤖 Step 3: AI Designing Circuit...")
design = ai(example_circuit)

print(f"\n🎯 Step 4: AI Design Output (3 values):")
print(f"• Design Parameter 1: {design[0][0]:.4f}")
print(f"• Design Parameter 2: {design[0][1]:.4f}")
print(f"• Design Parameter 3: {design[0][2]:.4f}")

print("\n" + "=" * 40)
print("✅ COMPLETE! AI generated circuit design.")
print("=" * 40)