# FILE: src/web_ui.py
"""
Advanced Web UI for AI Circuit Designer with 3D Visualization
Run with: streamlit run src/web_ui.py
"""
import streamlit as st
import torch
import pandas as pd
import matplotlib.pyplot as plt
import re
from models.simple_circuit_ai import SimpleCircuitAI
from visualization.circuit_3d_engine import Circuit3DVisualizer
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="AI Circuit Designer 2026", layout="wide")
st.title("🔌 AI Circuit Designer 2026")
st.markdown("Design optimized circuits using AI with 3D visualization")

# NEW: Circuit Description Input
st.sidebar.header("💬 Circuit Description")
prompt = st.sidebar.text_area(
    "Describe what you need:",
    "Example: Buck converter 12V to 5V, 1A output\nOr: Low-pass filter, 1kHz cutoff\nOr: LED driver for 3.3V, 20mA",
    height=120
)

# Circuit type detection and auto-suggestion
circuit_type = "custom"
auto_suggestions = {}

if prompt and len(prompt.strip()) > 10:  # Only if meaningful input
    prompt_lower = prompt.lower()
    
    # Buck converter detection
    if any(word in prompt_lower for word in ["buck", "step-down", "step down"]):
        circuit_type = "buck"
        st.sidebar.success("✅ Detected: Buck Converter")
        
        numbers = [float(x) for x in re.findall(r'\d+\.?\d*', prompt) if float(x) > 0]
        
        if numbers:
            # First number as input voltage
            auto_suggestions["voltage"] = numbers[0] if numbers[0] <= 24 else 12.0
            st.sidebar.info(f"Auto-suggested: Input voltage = {auto_suggestions['voltage']}V")
            
            # If second number exists and is smaller, suggest as load
            if len(numbers) > 1 and numbers[1] < numbers[0]:
                auto_suggestions["resistance"] = (numbers[0] - numbers[1]) * 100
                st.sidebar.info(f"Output: ~{numbers[1]}V")
    
    # Filter detection
    elif any(word in prompt_lower for word in ["filter", "lowpass", "highpass", "cutoff"]):
        circuit_type = "filter"
        st.sidebar.success("✅ Detected: Filter Circuit")
        
        # Extract frequency
        freq_match = re.search(r'(\d+)\s*(?:khz|hz|mhz|kHz|Hz|MHz)', prompt_lower)
        if freq_match:
            freq = float(freq_match.group(1))
            if 'khz' in prompt_lower or 'kHz' in prompt_lower:
                freq *= 1000
            elif 'mhz' in prompt_lower or 'MHz' in prompt_lower:
                freq *= 1000000
            auto_suggestions["frequency"] = min(freq, 1e6)  # Cap at 1MHz
            st.sidebar.info(f"Cutoff frequency: {auto_suggestions['frequency']}Hz")
    
    # LED driver detection
    elif any(word in prompt_lower for word in ["led", "driver", "light", "diode"]):
        circuit_type = "led_driver"
        st.sidebar.success("✅ Detected: LED Driver Circuit")
        auto_suggestions["voltage"] = 3.3  # Typical LED voltage
        auto_suggestions["current"] = 0.02  # 20mA typical
        st.sidebar.info("Suggested: 3.3V, 20mA LED circuit")
    
    # Amplifier detection
    elif any(word in prompt_lower for word in ["amplifier", "amp", "gain", "opamp"]):
        circuit_type = "amplifier"
        st.sidebar.success("✅ Detected: Amplifier Circuit")
        auto_suggestions["voltage"] = 12.0  # Typical op-amp voltage
        auto_suggestions["frequency"] = 10000  # 10kHz typical
    
    # Oscillator detection
    elif any(word in prompt_lower for word in ["oscillator", "clock", "timer", "555"]):
        circuit_type = "oscillator"
        st.sidebar.success("✅ Detected: Oscillator Circuit")
        auto_suggestions["voltage"] = 5.0  # Typical for oscillators
        auto_suggestions["frequency"] = 1000  # 1kHz typical

# Sidebar for circuit parameters
st.sidebar.header("⚙️ Circuit Parameters")

# Use auto-suggestions if available
default_voltage = float(auto_suggestions.get("voltage", 5.0))
default_resistance = float(auto_suggestions.get("resistance", 1000.0))
default_frequency = float(auto_suggestions.get("frequency", 1000.0))
default_current = float(auto_suggestions.get("current", 0.01))

voltage = st.sidebar.slider("Voltage (V)", 1.0, 24.0, default_voltage, 0.1)
resistance = st.sidebar.slider("Resistance (Ω)", 10.0, 10000.0, default_resistance, 10.0)
capacitance = st.sidebar.slider("Capacitance (F)", 1e-9, 1e-3, 1e-4, 1e-9)
frequency = st.sidebar.slider("Frequency (Hz)", 1.0, 1e6, default_frequency, 100.0)
current = st.sidebar.slider("Current (A)", 0.001, 1.0, default_current, 0.001)

# Show circuit type
if circuit_type != "custom":
    st.sidebar.markdown(f"**Circuit Type:** {circuit_type.upper().replace('_', ' ')}")

# Load AI model
@st.cache_resource
def load_model():
    return SimpleCircuitAI()

ai = load_model()

# Design button
if st.sidebar.button("🚀 Design Circuit", type="primary"):
    with st.spinner("AI designing circuit..."):
        # Prepare input
        inputs = torch.tensor([[voltage, resistance, capacitance, frequency, current]], dtype=torch.float32)
        
        # Get AI design
        with torch.no_grad():
            design = ai(inputs)
        
        # Display results in tabs
        tab1, tab2, tab3 = st.tabs(["📊 Component Values", "🧊 3D Circuit", "📈 Performance"])
        
        with tab1:
            # Component values bar chart
            fig, ax = plt.subplots(figsize=(10, 5))
            values = design[0].detach().numpy()
            components = ['Resistor', 'Capacitor', 'Inductor', 'Gain', 'Q-Factor'][:len(values)]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            
            bars = ax.bar(components, values, color=colors[:len(values)])
            ax.set_ylabel("Normalized Value")
            ax.set_title("AI Circuit Component Values")
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{value:.4f}', ha='center', va='bottom', fontsize=10)
            
            st.pyplot(fig)
        
        with tab2:
            # 3D CIRCUIT VISUALIZATION
            st.subheader("🧊 3D Circuit Visualization")
            
            # Create 3D visualizer
            viz_3d = Circuit3DVisualizer()
            
            # Convert AI output to 3D circuit
            design_np = design[0].detach().numpy()
            fig_3d = viz_3d.create_circuit_from_ai(design_np)
            
            # Display 3D plot
            st.plotly_chart(fig_3d, use_container_width=True)
            
            # 3D Controls
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("🖱️ Click & drag to rotate")
            with col2:
                st.info("🔍 Scroll to zoom")
            with col3:
                st.info("📐 Hover for values")
            
            # Circuit info
            with st.expander("📋 Circuit Details"):
                st.write(f"**Input Parameters:**")
                st.write(f"- Voltage: {voltage} V")
                st.write(f"- Resistance: {resistance} Ω")
                st.write(f"- Capacitance: {capacitance} F")
                st.write(f"- Frequency: {frequency} Hz")
                st.write(f"- Current: {current} A")
                
                if circuit_type != "custom":
                    st.write(f"**Circuit Type:** {circuit_type.replace('_', ' ').title()}")
                    if prompt:
                        st.write(f"**Description:** {prompt[:100]}...")
        
        with tab3:
            # Performance metrics
            st.subheader("📈 Circuit Performance")
            
            # Performance gauges
            perf_metrics = {
                "Efficiency": design[0][0].item() * 100,
                "Stability": design[0][1].item() * 100,
                "Cost Score": design[0][2].item() * 100
            }
            
            for metric, value in perf_metrics.items():
                st.progress(value/100, text=f"{metric}: {value:.1f}%")
            
            # Performance comparison chart
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.bar(list(perf_metrics.keys()), list(perf_metrics.values()), color=['green', 'blue', 'orange'])
            ax2.set_ylabel("Score (%)")
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
            st.pyplot(fig2)
            
            # Recommendations based on circuit type
            st.subheader("💡 AI Recommendations")
            
            if circuit_type == "buck":
                if design[0][0].item() > 0.7:
                    st.success("✅ High efficiency buck converter - suitable for power supplies")
                st.info("🔧 Consider using LM2596 or MP1584 switching regulator IC")
                
            elif circuit_type == "filter":
                if design[0][1].item() > 0.6:
                    st.success("✅ Sharp cutoff - good frequency response")
                st.info("🎛️ Use Sallen-Key topology for active filters")
                
            elif circuit_type == "led_driver":
                st.success("💡 LED driver optimized for constant current")
                st.info("⚡ Add current limiting resistor: R = (Vin - Vled) / Iled")
                
            elif circuit_type == "amplifier":
                st.success("🎚️ Amplifier design complete")
                st.info("📊 Consider using TL072 or LM358 op-amp")
                
            else:
                if design[0][0].item() > 0.7:
                    st.success("✅ High efficiency design - suitable for power applications")
                if design[0][1].item() > 0.6:
                    st.info("📡 Stable circuit - good for high-frequency applications")
                if design[0][2].item() < 0.4:
                    st.warning("💰 Cost-effective design")
        
        st.success("✅ Circuit design complete! Switch between tabs above.")

# Main area
st.header("📊 Example Circuits")
if st.button("Generate Sample Designs"):
    sample_circuits = torch.randn(5, 5) * 0.5 + 1.0
    designs = ai(sample_circuits)
    
    df = pd.DataFrame({
        'Circuit': [f'Circuit {i+1}' for i in range(5)],
        'Resistor Value': designs[:, 0].detach().numpy(),
        'Capacitor Value': designs[:, 1].detach().numpy(),
        'Layout Score': designs[:, 2].detach().numpy()
    })
    st.dataframe(df.style.highlight_max(axis=0))
    
    st.line_chart(df.set_index('Circuit'))

# Footer
st.markdown("---")
st.caption("AI Circuit Designer 2026 | Built with PyTorch, Streamlit & 3D Visualization")