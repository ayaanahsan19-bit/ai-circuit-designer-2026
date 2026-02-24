import streamlit as st
import streamlit.components.v1 as components
import json
import sys
import os

# --- ROBUST IMPORT ---
try:
    from PCB_Generator import PCBGenerator
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from PCB_Generator import PCBGenerator

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Circuit Designer 2026", layout="wide", initial_sidebar_state="expanded")

# --- FUTURISTIC CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
    h1 { color: #58a6ff; font-family: 'Courier New', monospace; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white; border: 1px solid #238636; font-weight: bold; border-radius: 6px; padding: 10px 24px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 0 15px rgba(63, 185, 80, 0.4);
    }
    
    /* Inputs */
    .stTextArea textarea { background-color: #0d1117; border: 1px solid #30363d; color: #c9d1d9; border-radius: 6px; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #161b22; border-radius: 6px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8b949e !important; border-radius: 6px 6px 0 0; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #21262d !important; color: #58a6ff !important; border-bottom: 2px solid #58a6ff !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR INFO ---
with st.sidebar:
    st.title("⚡ Circuit AI")
    st.caption("2026 Industrial Edition")
    st.markdown("---")
    st.markdown("### 🛠️ How to use")
    st.markdown("1. 📝 Enter a prompt")
    st.markdown("2. ⚡ Click **Generate**")
    st.markdown("3. 📐 View 2D, 3D & Calculations")
    st.markdown("---")
    st.info("⚡ **Engine:** SchemDraw + Plotly")

# --- MAIN PAGE ---
st.title("⚡ AI CIRCUIT DESIGNER")
st.write("Describe the circuit. The AI will design the Schematic, 3D PCB, and perform Engineering Calculations.")

# Default prompt
default_prompt = "Design a Buck converter with 24V input and 5V output"
user_prompt = st.text_area("Enter Circuit Prompt:", default_prompt, height=100)

if st.button("⚡ GENERATE CIRCUIT"):
    progress_bar = st.progress(0, text="Initializing Core...")
    
    with st.spinner("AI Architect is working..."):
        try:
            # 1. INITIALIZATION
            generator = PCBGenerator(project_name="AI_Design")
            progress_bar.progress(20, text="Parsing Prompt...")
            
            # 2. PARSING & CALCULATIONS
            generator.parse_ai_output(user_prompt)
            progress_bar.progress(40, text="Generating Netlist...")
            
            # 3. NETLIST
            netlist_path = generator.generate_netlist()
            progress_bar.progress(60, text="Drawing Schematic...")
            
            # 4. SCHEMATIC
            svg_code = generator.generate_schematic_svg()
            progress_bar.progress(80, text="Rendering 3D PCB...")
            
            # 5. 3D PCB
            fig_3d = generator.generate_3d_pcb() 
            progress_bar.progress(100, text="Complete!")
            
            # SUCCESS MESSAGE
            st.success(f"✅ Successfully Generated: {generator.project_name}")
            
            # --- DISPLAY TABS ---
            tab1, tab2, tab3, tab4 = st.tabs(["📐 Schematic (2D)", "📦 PCB 3D View", "🧮 Calculations", "💾 Source Code"])

            with tab1:
                st.subheader("Circuit Diagram (IEEE Standard)")
                if svg_code and "Error" not in svg_code:
                    components.html(svg_code, height=450, scrolling=False)
                else:
                    st.error("Schematic generation failed.")
                    st.code(svg_code, language='xml')

            with tab2:
                st.subheader("Interactive 3D View")
                st.write("👆 Click and drag to rotate. Scroll to zoom.")
                st.plotly_chart(fig_3d, use_container_width=True)
                
            with tab3:
                st.subheader("Engineering Parameters")
                # Create a nice display for calculations
                cols = st.columns(3)
                items = list(generator.calculations.items())
                
                for idx, (key, value) in enumerate(items):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.metric(label=key, value=value)
                
                st.markdown("---")
                st.info("These values are calculated using standard power electronics equations based on your prompt.")
                
            with tab4:
                st.subheader("Download Source Files")
                col1, col2, col3 = st.columns(3)
                
                # 1. SVG Download
                with col1:
                    st.download_button(
                        label="📄 Download SVG",
                        data=svg_code,
                        file_name=f"{generator.project_name}.svg",
                        mime="image/svg+xml"
                    )
                
                # 2. Netlist Download
                with col2:
                    try:
                        with open(netlist_path, "r", encoding='utf-8') as f:
                            netlist_data = f.read()
                        st.download_button(
                            label="🔌 Download Netlist",
                            data=netlist_data,
                            file_name=f"{generator.project_name}.net",
                            mime="text/plain"
                        )
                    except Exception:
                        st.warning("Netlist file error.")
                
                # 3. JSON Download
                with col3:
                    json_data = json.dumps(generator.components, indent=4)
                    st.download_button(
                        label="📋 Download JSON",
                        data=json_data,
                        file_name=f"{generator.project_name}.json",
                        mime="application/json"
                    )
                
                st.markdown("---")
                st.subheader("Component Graph (JSON)")
                st.code(json_data, language='json')
                
        except Exception as e:
            st.error(f"⚠️ Critical System Error: {e}")
            st.exception(e)