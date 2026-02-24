import json
import os
import math
import numpy as np
import plotly.graph_objects as go

# Safe imports for SchemDraw
try:
    import schemdraw
    import schemdraw.elements as elm
    SCHEMDRAW_AVAILABLE = True
except ImportError:
    SCHEMDRAW_AVAILABLE = False

# ==========================================
# LAYER 1: THE "FLUX" ASSET LIBRARY
# ==========================================

class FluxAssetLibrary:
    @staticmethod
    def get_3d_model(comp_type, x, y, value="", package=None):
        traces = []
        s = 1.0 
        
        try:
            if comp_type == "Source":
                traces.append(go.Mesh3d(x=[x-15*s, x+15*s, x+15*s, x-15*s], y=[y-10*s, y-10*s, y+10*s, y+10*s], z=[1.6, 1.6, 1.6, 1.6], color='#006400', name='Base'))
                traces.append(go.Mesh3d(x=[x-15*s, x+15*s, x+15*s, x-15*s], y=[y-10*s, y-10*s, y+10*s, y+10*s], z=[1.6+12*s, 1.6+12*s, 1.6+12*s, 1.6+12*s], color='#004d00', name='Top'))
                traces.append(go.Scatter3d(x=[x-5, x+5], y=[y, y], z=[1.6+13], mode='markers', marker=dict(size=4, color='silver'), showlegend=False))

            elif comp_type == "MOSFET":
                traces.append(go.Mesh3d(x=[x-8*s, x+8*s, x+8*s, x-8*s], y=[y-6*s, y-6*s, y+6*s, y+6*s], z=[1.6, 1.6, 1.6+10*s, 1.6+10*s], color='#1a1a1a', name='Body'))
                traces.append(go.Mesh3d(x=[x-10*s, x+10*s, x+10*s, x-10*s], y=[y-8*s, y-8*s, y+8*s, y+8*s], z=[1.6+10*s, 1.6+10*s, 1.6+12*s, 1.6+12*s], color='#c0c0c0', lighting=dict(specular=1.0, roughness=0.1)))
                for i in [-3, 0, 3]:
                    traces.append(go.Mesh3d(x=[x+i-1, x+i+1, x+i+1, x+i-1], y=[y-15, y-15, y-8, y-8], z=[1.6, 1.6, 1.6, 1.6], color='#d4af37'))
                traces.append(go.Scatter3d(x=[x], y=[y], z=[1.6+13], mode='text', text=value, textfont=dict(color='white', size=10), showlegend=False))

            elif comp_type == "Capacitor":
                theta = np.linspace(0, 2*np.pi, 30)
                z = np.linspace(0, 15, 20)
                theta_grid, z_grid = np.meshgrid(theta, z)
                r = 6
                x_grid = r * np.cos(theta_grid) + x
                y_grid = r * np.sin(theta_grid) + y
                traces.append(go.Surface(x=x_grid, y=y_grid, z=z_grid + 1.6, colorscale=[[0, '#1a1a1a'], [1, '#000033']], showscale=False))
                traces.append(go.Mesh3d(x=r*np.cos(theta)+x, y=r*np.sin(theta)+y, z=[1.6+15]*30, color='silver', lighting=dict(specular=1.0, diffuse=0.5)))
                traces.append(go.Scatter3d(x=[x-6, x-6], y=[y, y], z=[1.6+2, 1.6+14], mode='lines', line=dict(color='white', width=4)))
                traces.append(go.Scatter3d(x=[x], y=[y-15], z=[1.6], mode='text', text=value, textfont=dict(color='white', size=12)))

            elif comp_type == "Inductor":
                theta = np.linspace(0, 2*np.pi, 100)
                r = 10
                x_ring = r * np.cos(theta) + x
                y_ring = r * np.sin(theta) + y
                traces.append(go.Scatter3d(x=x_ring, y=y_ring, z=10*np.ones(100), mode='lines', line=dict(color='#8B4513', width=15)))
                for t in range(0, 360, 20):
                    rad = np.deg2rad(t)
                    traces.append(go.Scatter3d(x=[r*np.cos(rad)+x, (r-5)*np.cos(rad)+x], y=[r*np.sin(rad)+y, (r-5)*np.sin(rad)+y], z=[10, 10], mode='lines', line=dict(color='#b87333', width=3), showlegend=False))
                traces.append(go.Scatter3d(x=[x], y=[y-20], z=[1.6], mode='text', text=value, textfont=dict(color='white', size=12)))

            elif comp_type == "Resistor":
                traces.append(go.Mesh3d(x=[x-4, x+4, x+4, x-4], y=[y-2, y-2, y+2, y+2], z=[1.6, 1.6, 1.6+2, 1.6+2], color='#1a1a1a'))
                traces.append(go.Mesh3d(x=[x-5, x-4, x-4, x-5], y=[y-2, y-2, y+2, y+2], z=[1.6, 1.6, 1.6+2, 1.6+2], color='silver'))
                traces.append(go.Mesh3d(x=[x+4, x+5, x+5, x+4], y=[y-2, y-2, y+2, y+2], z=[1.6, 1.6, 1.6+2, 1.6+2], color='silver'))
                traces.append(go.Scatter3d(x=[x], y=[y], z=[1.6+3], mode='text', text=value, textfont=dict(color='white', size=8)))

            elif comp_type == "Diode":
                traces.append(go.Mesh3d(x=[x-5, x+5, x+5, x-5], y=[y-3, y-3, y+3, y+3], z=[1.6, 1.6, 1.6+3, 1.6+3], color='black'))
                traces.append(go.Scatter3d(x=[x+3, x+3], y=[y-3, y+3], z=[1.6+3.1, 1.6+3.1], mode='lines', line=dict(color='white', width=3)))
                
        except Exception as e:
            traces.append(go.Mesh3d(x=[x-5, x+5, x+5, x-5], y=[y-5, y-5, y+5, y+5], z=[1.6, 1.6, 1.6+5, 1.6+5], color='red'))
            
        return traces

# ==========================================
# LAYER 2: THE BRAIN
# ==========================================

class CircuitCompiler:
    @staticmethod
    def compile_prompt(prompt):
        prompt = prompt.lower()
        
        if "buck" in prompt:
            vin, vout = 24, 5
            if "48v" in prompt: vin = 48
            if "12v" in prompt: vout = 12
            
            return {
                "project": "Buck_Converter",
                "components": [
                    {"id": "VIN", "type": "Source", "value": f"{vin}V", "pos": [0, 0]},
                    {"id": "Q1", "type": "MOSFET", "value": "IRF540", "pos": [1, 0]},
                    {"id": "D1", "type": "Diode", "value": "Schottky", "pos": [1, -1]},
                    {"id": "L1", "type": "Inductor", "value": "100uH", "pos": [2, 0]},
                    {"id": "C1", "type": "Capacitor", "value": "100uF", "pos": [3, 0]},
                    {"id": "RL", "type": "Resistor", "value": "Load", "pos": [4, 0]}
                ],
                "netlist": [["VIN", "Q1"], ["Q1", "L1"], ["L1", "C1"], ["C1", "RL"], ["Q1", "D1"]]
            }
        elif "amplifier" in prompt:
             return {
                "project": "Amplifier",
                "components": [
                    {"id": "V1", "type": "Source", "value": "9V", "pos": [0, 0]},
                    {"id": "U1", "type": "MOSFET", "value": "OpAmp", "pos": [2, 0]},
                    {"id": "R1", "type": "Resistor", "value": "10k", "pos": [3, 0]}
                ],
                "netlist": [["V1", "U1"], ["U1", "R1"]]
            }
        else:
            return {
                "project": "LED_Circuit",
                "components": [
                    {"id": "V1", "type": "Source", "value": "5V", "pos": [0, 0]},
                    {"id": "R1", "type": "Resistor", "value": "330", "pos": [1, 0]},
                    {"id": "D1", "type": "Diode", "value": "LED", "pos": [2, 0]}
                ],
                "netlist": [["V1", "R1"], ["R1", "D1"]]
            }

# ==========================================
# LAYER 3: PROFESSIONAL RENDERERS
# ==========================================

class ProfessionalRenderer:
    def __init__(self):
        self.fig = go.Figure()
        self.setup_scene()

    def setup_scene(self):
        self.fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='#111111', aspectmode='data', camera=dict(eye=dict(x=0.8, y=0.8, z=1.2))), paper_bgcolor='#111111', margin=dict(l=0, r=0, t=0, b=0), showlegend=False)

    def draw_pcb_stackup(self):
        self.fig.add_trace(go.Mesh3d(x=[0, 800, 800, 0], y=[0, 0, 500, 500], z=[0,0,0,0], color='#0a5f38', opacity=1, lighting=dict(roughness=0.9)))
        self.fig.add_trace(go.Scatter3d(x=[400], y=[480], z=[0.5], mode='text', text='AI CIRCUIT 2026', textfont=dict(color='white', size=14, family='Arial Black')))

    def draw_trace(self, p1, p2):
        x1, y1 = p1; x2, y2 = p2
        mid_x = (x1 + x2) / 2
        path = [p1, [mid_x, y1], [mid_x, y2], p2]
        self.fig.add_trace(go.Scatter3d(x=[p[0] for p in path], y=[p[1] for p in path], z=[1.65]*len(path), mode='lines', line=dict(color='#d4af37', width=8), showlegend=False))

# ==========================================
# LAYER 4: CONTROLLER
# ==========================================

class PCBGenerator:
    def __init__(self, project_name="generated_circuit"):
        self.project_name = project_name
        self.prompt_text = ""
        self.design_data = {}
        self.renderer = ProfessionalRenderer()
        self.components = []
        self.calculations = {}

    def parse_ai_output(self, prompt_text):
        self.prompt_text = prompt_text
        self.design_data = CircuitCompiler.compile_prompt(prompt_text)
        self.project_name = self.design_data.get("project", "Circuit")
        
        spacing = 150; start_x = 100; y_center = 250
        real_components = []
        for comp in self.design_data['components']:
            rx = start_x + (comp['pos'][0] * spacing)
            ry = y_center + (comp['pos'][1] * spacing)
            comp['real_x'] = rx; comp['real_y'] = ry
            real_components.append(comp)
        self.components = real_components
        self.calculations = {"Status": "Design Compiled", "Components": len(self.components)}

    def generate_netlist(self, filename="circuit.net"):
        filepath = os.path.join("exports", filename)
        os.makedirs("exports", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"* Netlist: {self.project_name}\n")
            for net in self.design_data.get('netlist', []): f.write(f".net {net[0]} {net[1]}\n")
            f.write(".end\n")
        return filepath

    def generate_schematic_svg(self, filename="schematic.svg"):
        if not SCHEMDRAW_AVAILABLE: return "<svg>Missing SchemDraw</svg>"
        filepath = os.path.join("exports", filename)
        os.makedirs("exports", exist_ok=True)
        
        try:
            with schemdraw.Drawing(file=filepath, show=False) as d:
                d.config(unit=3)
                
                # --- BUCK CONVERTER (Manual Perfect Layout) ---
                if "buck" in self.prompt_text.lower():
                    V_in = elm.SourceV().label("Vin 24V").right()
                    elm.Line().right()
                    Q1 = elm.NFet().label("Q1")
                    sw_pt = d.here; elm.Dot()
                    elm.Line().right()
                    elm.Inductor2().right().label("L1")
                    cap_pt = d.here; elm.Dot()
                    elm.Line().right()
                    elm.Resistor().down().label("Load")
                    load_pt = d.here; elm.Dot()
                    
                    # Close the loop safely
                    elm.Line().left().tox(V_in.start[0])
                    elm.Ground()
                    elm.Line().up().toy(V_in.start[1])
                    
                    # Capacitor Branch
                    elm.Capacitor2().at(cap_pt).down().label("C1")
                    elm.Line().down().toy(load_pt[1])
                    elm.Line().left().tox(load_pt[0])
                    
                    # Diode Branch
                    elm.Line().at(sw_pt).down()
                    elm.Diode().down().label("D1")
                    elm.Line().down().toy(load_pt[1])
                    elm.Line().left().tox(load_pt[0])

                # --- GENERIC / LED (Safe Auto Layout) ---
                else:
                    # Draw components in a line for safety
                    for i, comp in enumerate(self.components):
                        if i > 0: elm.Line().right()
                        
                        ctype = comp['type']
                        val = comp.get('value', comp['id'])
                        
                        if ctype == "Source": elm.SourceV().label(val)
                        elif ctype == "Resistor": elm.Resistor().label(val)
                        elif ctype == "Capacitor": elm.Capacitor2().label(val)
                        elif ctype == "Inductor": elm.Inductor2().label(val)
                        elif ctype == "MOSFET": elm.NFet().label(comp['id'])
                        elif ctype == "Diode": elm.Diode().label(val) # FIX: Added Diode
                        else: elm.Resistor().label(comp['id']) # FIX: Safe fallback (Box doesn't exist)

            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f: return f.read()
                    
        except Exception as e:
            return f"<svg width='100%' height='100%'><rect width='100%' height='100%' fill='#222'/><text x='10' y='20' fill='red'>Schematic Error: {e}</text></svg>"
        return ""