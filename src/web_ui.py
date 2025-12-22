# FILE: src/web_ui.py
"""
Simple Web UI for AI Circuit Designer
Run with: streamlit run src/web_ui.py
"""
import streamlit as st
import torch
import pandas as pd
import matplotlib.pyplot as plt
from models.simple_circuit_ai import SimpleCircuitAI

# Page setup
st.set_page_config(page_title="AI Circuit Designer 2026", layout="wide")
st.title("🔌 AI Circuit Designer 2026")
st.markdown("Design optimized circuits using AI")

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
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Component A", f"{design[0][0].item():.4f}")
        with col2:
            st.metric("Component B", f"{design[0][1].item():.4f}")
        with col3:
            st.metric("Layout Score", f"{design[0][2].item():.4f}")
        
        # Visualization
        fig, ax = plt.subplots(figsize=(8, 4))
        values = design[0].detach().numpy()
        ax.bar(['Comp A', 'Comp B', 'Layout', 'Eff', 'Cost'][:len(values)], values)
        ax.set_ylabel("Value")
        ax.set_title("AI Circuit Design Output")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        
        st.success("✅ Circuit design complete!")

# Main area
st.header("📊 Example Circuits")
if st.button("Generate Sample Designs"):
    sample_circuits = torch.randn(5, 5) * 0.5 + 1.0
    designs = ai(sample_circuits)
    
    df = pd.DataFrame({
        'Circuit': [f'Circuit {i+1}' for i in range(5)],
        'Output 1': designs[:, 0].detach().numpy(),
        'Output 2': designs[:, 1].detach().numpy(),
        'Output 3': designs[:, 2].detach().numpy()
    })
    st.dataframe(df.style.highlight_max(axis=0))
    
    st.line_chart(df.set_index('Circuit'))

# Footer
st.markdown("---")
st.caption("AI Circuit Designer 2026 | Built with PyTorch & Streamlit")