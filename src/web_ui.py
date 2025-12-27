# FILE: src/web_ui.py
"""
Advanced Web UI for AI Circuit Designer with 3D Visualization
Run with: streamlit run src/web_ui.py
"""
import streamlit as st
import torch
import pandas as pd
import matplotlib.pyplot as plt
from models.simple_circuit_ai import SimpleCircuitAI
from visualization.circuit_3d_engine import Circuit3DVisualizer
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="AI Circuit Designer 2026", layout="wide")
st.title("🔌 AI Circuit Designer 2026")
st.markdown("Design optimized circuits using AI with 3D visualization")

# Load AI model
@st.cache_resource
def load_model():
    return SimpleCircuitAI()

ai = load_model()

# Sidebar for circuit parameters
st.sidebar.header("⚙️ Circuit Parameters")

voltage = st.sidebar.slider("Voltage (V)", 1.0, 24.0, 5.0, 0.1)
resistance = st.sidebar.slider("Resistance (Ω)", 10.0, 10000.0, 1000.0, 10.0)
capacitance = st.sidebar.slider("Capacitance (F)", 1e-9, 1e-3, 1e-4, 1e-9)
frequency = st.sidebar.slider("Frequency (Hz)", 1.0, 1e6, 1000.0, 100.0)
current = st.sidebar.slider("Current (A)", 0.001, 1.0, 0.01, 0.001)

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
            
            # Recommendations
            st.subheader("💡 AI Recommendations")
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