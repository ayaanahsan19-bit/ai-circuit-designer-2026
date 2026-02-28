"""
Quick smoke tests / examples for the AI Circuit Designer pipeline.

Run with:
    python -m src.examples.quick_smoke_tests
from the project root.
"""

from PCB_Generator import PCBGenerator


def run_example(prompt: str):
    gen = PCBGenerator(project_name="SmokeTest")
    gen.parse_ai_output(prompt)
    gen.run_calculations()
    netlist_path = gen.generate_netlist()
    print(f"\n=== Prompt: {prompt} ===")
    print(f"Project: {gen.project_name}")
    print("Parameters:", gen.parameters)
    print("Calculations:", gen.calculations)
    print("Netlist file:", netlist_path)


def main():
    prompts = [
        "Design a Buck converter with 24V input and 5V output",
        "Design an LED driver for a single LED from 5V",
        "Design an RC lowpass filter for 1 kHz",
        "Design a non-inverting amplifier with gain of 10",
    ]
    for p in prompts:
        run_example(p)


if __name__ == "__main__":
    main()

