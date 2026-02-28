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

try:
    from simulation.spice_engine import SpiceEngine
    SPICE_AVAILABLE = True
except ImportError:
    SPICE_AVAILABLE = False

# ==========================================
# LAYER 1: THE "FLUX" ASSET LIBRARY
# ==========================================

class FluxAssetLibrary:
    @staticmethod
    def get_3d_model(comp_type, x, y, value="", package=None, refdes=None):
        traces = []
        s = 1.0 
        label = refdes or ""
        
        try:
            if comp_type == "Source":
                traces.append(go.Mesh3d(x=[x-15*s, x+15*s, x+15*s, x-15*s], y=[y-10*s, y-10*s, y+10*s, y+10*s], z=[0.2, 0.2, 0.2, 0.2], color='#006400', name='VIN'))
                traces.append(go.Scatter3d(x=[x], y=[y+12], z=[1.2], mode='text', text=label or value, textfont=dict(color='white', size=10), showlegend=False))

            elif comp_type == "MOSFET":
                # TO-220 style body
                traces.append(go.Mesh3d(x=[x-9*s, x+9*s, x+9*s, x-9*s], y=[y-6*s, y-6*s, y+6*s, y+6*s], z=[1.0, 1.0, 4.0, 4.0], color='#1a1a1a', name='Q1'))
                # Copper pads under leads
                for i in [-4, 0, 4]:
                    traces.append(go.Mesh3d(x=[x+i-1.5, x+i+1.5, x+i+1.5, x+i-1.5], y=[y-10, y-10, y-6, y-6], z=[0.1, 0.1, 0.1, 0.1], color='#d4af37'))
                # Label
                if label:
                    traces.append(go.Scatter3d(x=[x], y=[y+10], z=[4.5], mode='text', text=label, textfont=dict(color='white', size=10), showlegend=False))

            elif comp_type == "Capacitor":
                # Electrolytic vs ceramic style
                if package == "electrolytic":
                    theta = np.linspace(0, 2*np.pi, 30)
                    z = np.linspace(0, 14, 16)
                    theta_grid, z_grid = np.meshgrid(theta, z)
                    r = 7
                    x_grid = r * np.cos(theta_grid) + x
                    y_grid = r * np.sin(theta_grid) + y
                    traces.append(go.Surface(x=x_grid, y=y_grid, z=z_grid + 0.2, colorscale=[[0, '#333333'], [1, '#555555']], showscale=False))
                    traces.append(go.Scatter3d(x=[x], y=[y], z=[15.5], mode='text', text=label or value, textfont=dict(color='white', size=10), showlegend=False))
                else:
                    # Small ceramic/SMD block
                    traces.append(go.Mesh3d(x=[x-5, x+5, x+5, x-5], y=[y-3, y-3, y+3, y+3], z=[0.3, 0.3, 1.5, 1.5], color='#c0c0c0'))
                    if label:
                        traces.append(go.Scatter3d(x=[x], y=[y+6], z=[1.8], mode='text', text=label, textfont=dict(color='white', size=9), showlegend=False))

            elif comp_type == "Inductor":
                # Shielded SMD inductor block
                traces.append(go.Mesh3d(x=[x-8, x+8, x+8, x-8], y=[y-8, y-8, y+8, y+8], z=[0.4, 0.4, 4.0, 4.0], color='#3a2f0b'))
                if label:
                    traces.append(go.Scatter3d(x=[x], y=[y+11], z=[4.5], mode='text', text=label, textfont=dict(color='white', size=10), showlegend=False))

            elif comp_type == "Resistor":
                traces.append(go.Mesh3d(x=[x-4, x+4, x+4, x-4], y=[y-2, y-2, y+2, y+2], z=[1.6, 1.6, 1.6+2, 1.6+2], color='#1a1a1a'))
                traces.append(go.Mesh3d(x=[x-5, x-4, x-4, x-5], y=[y-2, y-2, y+2, y+2], z=[1.6, 1.6, 1.6+2, 1.6+2], color='silver'))
                traces.append(go.Mesh3d(x=[x+4, x+5, x+5, x+4], y=[y-2, y-2, y+2, y+2], z=[1.6, 1.6, 1.6+2, 1.6+2], color='silver'))
                traces.append(go.Scatter3d(x=[x], y=[y], z=[1.6+3], mode='text', text=label or value, textfont=dict(color='white', size=8)))

            elif comp_type == "Diode":
                traces.append(go.Mesh3d(x=[x-5, x+5, x+5, x-5], y=[y-3, y-3, y+3, y+3], z=[1.6, 1.6, 1.6+3, 1.6+3], color='black'))
                traces.append(go.Scatter3d(x=[x+3, x+3], y=[y-3, y+3], z=[1.6+3.1, 1.6+3.1], mode='lines', line=dict(color='white', width=3)))
                if label:
                    traces.append(go.Scatter3d(x=[x], y=[y+7], z=[1.6+3.5], mode='text', text=label, textfont=dict(color='white', size=9), showlegend=False))

            elif comp_type == "Terminal":
                # Two-pin screw terminal block
                traces.append(go.Mesh3d(x=[x-12, x+12, x+12, x-12], y=[y-8, y-8, y+8, y+8], z=[0.4, 0.4, 4.0, 4.0], color='#1e4d2b'))
                traces.append(go.Scatter3d(x=[x-6, x+6], y=[y, y], z=[4.5, 4.5], mode='markers', marker=dict(size=5, color='silver'), showlegend=False))
                if label:
                    traces.append(go.Scatter3d(x=[x], y=[y+11], z=[4.5], mode='text', text=label, textfont=dict(color='white', size=10), showlegend=False))

            elif comp_type == "MountingHole":
                theta = np.linspace(0, 2*np.pi, 40)
                r = 5
                x_ring = r * np.cos(theta) + x
                y_ring = r * np.sin(theta) + y
                traces.append(go.Scatter3d(x=x_ring, y=y_ring, z=[0.3]*len(theta), mode='lines', line=dict(color='#dddddd', width=3), showlegend=False))
                
        except Exception as e:
            traces.append(go.Mesh3d(x=[x-5, x+5, x+5, x-5], y=[y-5, y-5, y+5, y+5], z=[1.6, 1.6, 1.6+5, 1.6+5], color='red'))
            
        return traces

# ==========================================
# LAYER 2: THE BRAIN
# ==========================================

class CircuitCompiler:
    @staticmethod
    def compile_prompt(prompt):
        """
        Compile a natural-language prompt into a structured circuit template.

        Returns a design_data dict with (at minimum):
        - project: name
        - components: list of components with logical positions
        - netlist: simple list of component-to-component connections (for legacy uses)
        - nets: richer, node-based connectivity description
        - parameters: high-level circuit parameters for calculations / SPICE
        """
        text = (prompt or "").lower()

        # --- Buck converter family -------------------------------------------------
        if "buck" in text or "step-down" in text:
            # Default to a 12V -> 5V, 2A, 50kHz non-synchronous buck
            vin = 12.0
            vout = 5.0
            iload = 2.0
            f_sw = 50e3
            if "24v" in text:
                vin = 24.0
            if "48v" in text:
                vin = 48.0

            params = {
                "topology": "buck",
                "Vin": vin,
                "Vout": vout,
                "Iload": iload,
                "Fsw": f_sw,
            }

            components = [
                {
                    "id": "JVIN",
                    "type": "Terminal",
                    "value": "VIN",
                    "pos": [0, 0],
                    "role": "input_terminal",
                    "nodes": {"pos": "VIN", "neg": "GND"},
                },
                {
                    "id": "CIN1",
                    "type": "Capacitor",
                    "value": "100uF",
                    "pos": [1, 0],
                    "role": "input_cap_bulk",
                    "package": "electrolytic",
                    "nodes": {"p": "VIN", "n": "GND"},
                },
                {
                    "id": "CIN2",
                    "type": "Capacitor",
                    "value": "0.1uF",
                    "pos": [1, -0.5],
                    "role": "input_cap_ceramic",
                    "package": "ceramic",
                    "nodes": {"p": "VIN", "n": "GND"},
                },
                {
                    "id": "Q1",
                    "type": "MOSFET",
                    "value": "IRF540",
                    "pos": [2, 0],
                    "role": "switch",
                    "nodes": {"d": "SW", "s": "VIN", "g": "GATE"},
                },
                {
                    "id": "D1",
                    "type": "Diode",
                    "value": "Schottky",
                    "pos": [3, 0],
                    "role": "freewheel_diode",
                    "nodes": {"anode": "GND", "cathode": "SW"},
                },
                {
                    "id": "L1",
                    "type": "Inductor",
                    "value": "100uH",
                    "pos": [4, 0],
                    "role": "output_inductor",
                    "nodes": {"p": "SW", "n": "VOUT"},
                },
                {
                    "id": "COUT1",
                    "type": "Capacitor",
                    "value": "100uF",
                    "pos": [5, 0],
                    "role": "output_capacitor",
                    "package": "electrolytic",
                    "nodes": {"p": "VOUT", "n": "GND"},
                },
                {
                    "id": "R1",
                    "type": "Resistor",
                    "value": "10-47R",
                    "pos": [2, -0.8],
                    "role": "gate_resistor",
                    "nodes": {"p": "DRV", "n": "GATE"},
                },
                {
                    "id": "R2",
                    "type": "Resistor",
                    "value": "10k",
                    "pos": [2, -1.3],
                    "role": "gate_pulldown",
                    "nodes": {"p": "GATE", "n": "GND"},
                },
                {
                    "id": "JOUT",
                    "type": "Terminal",
                    "value": "VOUT",
                    "pos": [6, 0],
                    "role": "output_terminal",
                    "nodes": {"pos": "VOUT", "neg": "GND"},
                },
                {
                    "id": "MH1",
                    "type": "MountingHole",
                    "value": "M3",
                    "pos": [-0.5, -1.0],
                    "role": "mount_hole",
                    "nodes": {},
                },
                {
                    "id": "MH2",
                    "type": "Resistor",
                    "value": "M3",
                    "pos": [6.5, -1.0],
                    "role": "mount_hole",
                    "nodes": {},
                },
            ]

            # Simple legacy netlist (component-to-component) for routing / old code
            netlist_pairs = [
                ["JVIN", "CIN1"],
                ["CIN1", "Q1"],
                ["Q1", "D1"],
                ["Q1", "L1"],
                ["L1", "COUT1"],
                ["COUT1", "JOUT"],
            ]

            nets = [
                {"name": "VIN", "connections": [{"comp": "JVIN", "pin": "pos"}, {"comp": "CIN1", "pin": "p"}, {"comp": "CIN2", "pin": "p"}, {"comp": "Q1", "pin": "s"}]},
                {"name": "SW", "connections": [{"comp": "Q1", "pin": "d"}, {"comp": "L1", "pin": "p"}, {"comp": "D1", "pin": "cathode"}]},
                {"name": "VOUT", "connections": [{"comp": "L1", "pin": "n"}, {"comp": "COUT1", "pin": "p"}, {"comp": "JOUT", "pin": "pos"}]},
                {"name": "GND", "connections": [{"comp": "JVIN", "pin": "neg"}, {"comp": "JOUT", "pin": "neg"}, {"comp": "CIN1", "pin": "n"}, {"comp": "CIN2", "pin": "n"}, {"comp": "COUT1", "pin": "n"}, {"comp": "R2", "pin": "n"}, {"comp": "D1", "pin": "anode"}]},
            ]

            return {
                "project": "Buck_Converter",
                "components": components,
                "netlist": netlist_pairs,
                "nets": nets,
                "parameters": params,
            }

        # --- RC filter / simple filter --------------------------------------------
        if "filter" in text or "rc" in text:
            vin = 5.0
            fc = 1e3
            if "audio" in text:
                fc = 1e3
            if "lowpass" in text:
                fc = 1e3

            params = {
                "topology": "rc_lowpass",
                "Vin": vin,
                "Fc": fc,
                "R": 1e3,
                "C": 1.6e-7,
            }

            components = [
                {
                    "id": "V1",
                    "type": "Source",
                    "value": f"{vin}V",
                    "pos": [0, 0],
                    "role": "input_source",
                    "nodes": {"pos": "VIN", "neg": "GND"},
                },
                {
                    "id": "R1",
                    "type": "Resistor",
                    "value": "1k",
                    "pos": [1, 0],
                    "role": "rc_resistor",
                    "nodes": {"p": "VIN", "n": "VC"},
                },
                {
                    "id": "C1",
                    "type": "Capacitor",
                    "value": "160n",
                    "pos": [2, 0],
                    "role": "rc_capacitor",
                    "nodes": {"p": "VC", "n": "GND"},
                },
            ]

            netlist_pairs = [["V1", "R1"], ["R1", "C1"]]
            nets = [
                {"name": "VIN", "connections": [{"comp": "V1", "pin": "pos"}, {"comp": "R1", "pin": "p"}]},
                {"name": "VC", "connections": [{"comp": "R1", "pin": "n"}, {"comp": "C1", "pin": "p"}]},
                {"name": "GND", "connections": [{"comp": "V1", "pin": "neg"}, {"comp": "C1", "pin": "n"}]},
            ]

            return {
                "project": "RC_Filter",
                "components": components,
                "netlist": netlist_pairs,
                "nets": nets,
                "parameters": params,
            }

        # --- Simple amplifier ------------------------------------------------------
        if "amplifier" in text or "amp" in text:
            vin = 1.0
            gain = 10.0

            params = {
                "topology": "opamp_non_inverting",
                "Vin": vin,
                "Gain": gain,
                "Vcc": 9.0,
            }

            components = [
                {
                    "id": "VCC",
                    "type": "Source",
                    "value": "9V",
                    "pos": [0, 1],
                    "role": "supply",
                    "nodes": {"pos": "VCC", "neg": "GND"},
                },
                {
                    "id": "VIN",
                    "type": "Source",
                    "value": f"{vin}V",
                    "pos": [0, -1],
                    "role": "input_source",
                    "nodes": {"pos": "VIN", "neg": "GND"},
                },
                {
                    "id": "U1",
                    "type": "MOSFET",
                    "value": "OpAmp",
                    "pos": [2, 0],
                    "role": "opamp",
                    "nodes": {"non_inv": "VIN", "inv": "VFB", "out": "VOUT", "vcc": "VCC", "vee": "GND"},
                },
                {
                    "id": "R1",
                    "type": "Resistor",
                    "value": "10k",
                    "pos": [3, -0.5],
                    "role": "feedback_top",
                    "nodes": {"p": "VOUT", "n": "VFB"},
                },
                {
                    "id": "R2",
                    "type": "Resistor",
                    "value": "1k",
                    "pos": [3, 0.5],
                    "role": "feedback_bottom",
                    "nodes": {"p": "VFB", "n": "GND"},
                },
            ]

            netlist_pairs = [["VIN", "U1"], ["U1", "R1"], ["R1", "R2"]]
            nets = [
                {"name": "VIN", "connections": [{"comp": "VIN", "pin": "pos"}, {"comp": "U1", "pin": "non_inv"}]},
                {"name": "VOUT", "connections": [{"comp": "U1", "pin": "out"}, {"comp": "R1", "pin": "p"}]},
                {"name": "VFB", "connections": [{"comp": "R1", "pin": "n"}, {"comp": "R2", "pin": "p"}, {"comp": "U1", "pin": "inv"}]},
                {"name": "VCC", "connections": [{"comp": "VCC", "pin": "pos"}, {"comp": "U1", "pin": "vcc"}]},
                {"name": "GND", "connections": [{"comp": "VCC", "pin": "neg"}, {"comp": "VIN", "pin": "neg"}, {"comp": "R2", "pin": "n"}, {"comp": "U1", "pin": "vee"}]},
            ]

            return {
                "project": "Amplifier",
                "components": components,
                "netlist": netlist_pairs,
                "nets": nets,
                "parameters": params,
            }

        # --- Default: LED / simple DC drive ---------------------------------------
        vin = 5.0
        if "12v" in text:
            vin = 12.0

        params = {
            "topology": "led_driver",
            "Vin": vin,
            "ILED": 0.02,
        }

        components = [
            {
                "id": "V1",
                "type": "Source",
                "value": f"{vin}V",
                "pos": [0, 0],
                "role": "input_source",
                "nodes": {"pos": "VIN", "neg": "GND"},
            },
            {
                "id": "R1",
                "type": "Resistor",
                "value": "330",
                "pos": [1, 0],
                "role": "led_resistor",
                "nodes": {"p": "VIN", "n": "VLED"},
            },
            {
                "id": "D1",
                "type": "Diode",
                "value": "LED",
                "pos": [2, 0],
                "role": "led",
                "nodes": {"anode": "VLED", "cathode": "GND"},
            },
        ]

        netlist_pairs = [["V1", "R1"], ["R1", "D1"]]
        nets = [
            {"name": "VIN", "connections": [{"comp": "V1", "pin": "pos"}, {"comp": "R1", "pin": "p"}]},
            {"name": "VLED", "connections": [{"comp": "R1", "pin": "n"}, {"comp": "D1", "pin": "anode"}]},
            {"name": "GND", "connections": [{"comp": "V1", "pin": "neg"}, {"comp": "D1", "pin": "cathode"}]},
        ]

        return {
            "project": "LED_Circuit",
            "components": components,
            "netlist": netlist_pairs,
            "nets": nets,
            "parameters": params,
        }

# ==========================================
# LAYER 3: PROFESSIONAL RENDERERS
# ==========================================

class ProfessionalRenderer:
    def __init__(self):
        self.fig = go.Figure()
        self.setup_scene()

    def setup_scene(self):
        # Slightly angled, more \"photoreal\" camera like CAD tools
        self.fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                bgcolor="#202430",
                aspectmode="data",
                camera=dict(eye=dict(x=1.5, y=1.2, z=0.9)),
            ),
            paper_bgcolor="#0b0d12",
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
        )

    def draw_pcb_stackup(self, x_min, x_max, y_min, y_max):
        """
        Draw a compact 3D board around the components instead of a huge plane.
        """
        # Add some margin so components are nicely framed
        margin = 40
        x0 = x_min - margin
        x1 = x_max + margin
        y0 = y_min - margin
        y1 = y_max + margin

        # Top surface of the PCB
        self.fig.add_trace(
            go.Mesh3d(
                x=[x0, x1, x1, x0],
                y=[y0, y0, y1, y1],
                z=[0, 0, 0, 0],
                color="#0a5f38",
                opacity=1,
                lighting=dict(roughness=0.9),
                name="PCB",
            )
        )

        # Simple silkscreen text near one corner
        self.fig.add_trace(
            go.Scatter3d(
                x=[(x0 + x1) / 2],
                y=[y1 - 20],
                z=[1.0],
                mode="text",
                text="AI CIRCUIT 2026",
                textfont=dict(color="white", size=14, family="Arial Black"),
                showlegend=False,
            )
        )

    def draw_trace(self, p1, p2):
        """
        Draw a copper trace hugging the PCB surface using 45-degree style routing.
        """
        x1, y1 = p1
        x2, y2 = p2

        # Simple 45-degree dogleg: horizontal then diagonal then vertical
        mid_x = (x1 + x2) / 2
        path = [p1, [mid_x, y1], [mid_x, y2], p2]
        self.fig.add_trace(
            go.Scatter3d(
                x=[p[0] for p in path],
                y=[p[1] for p in path],
                z=[0.05] * len(path),
                mode="lines",
                line=dict(color="#d4af37", width=8),
                showlegend=False,
            )
        )

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
        self.parameters = {}

    def parse_ai_output(self, prompt_text):
        self.prompt_text = prompt_text
        self.design_data = CircuitCompiler.compile_prompt(prompt_text)
        self.project_name = self.design_data.get("project", "Circuit")
        self.parameters = self.design_data.get("parameters", {})
        
        # Use a slightly tighter spacing for buck layouts to get a denser, more PCB-like board
        spacing = 150
        if self.design_data.get("parameters", {}).get("topology") == "buck":
            spacing = 80
        start_x = 100; y_center = 250
        real_components = []
        for comp in self.design_data['components']:
            rx = start_x + (comp['pos'][0] * spacing)
            ry = y_center + (comp['pos'][1] * spacing)
            comp['real_x'] = rx; comp['real_y'] = ry
            real_components.append(comp)
        self.components = real_components
        # Basic metadata; detailed calculations added separately
        self.calculations = {"Status": "Design Compiled", "Components": len(self.components)}

    # --------- Calculation helpers -------------------------------------------------
    def run_calculations(self):
        """Populate self.calculations with engineering values based on topology."""
        topo = self.parameters.get("topology", "")
        calcs = {"Status": "Design Compiled", "Components": len(self.components)}

        if topo == "buck":
            vin = float(self.parameters.get("Vin", 24.0))
            vout = float(self.parameters.get("Vout", 5.0))
            iload = float(self.parameters.get("Iload", 2.0))
            f_sw = float(self.parameters.get("Fsw", 100e3))

            duty = vout / vin if vin > 0 else 0.0
            l_h = 100e-6  # from template
            ripple_i = (vin - vout) * duty / (l_h * f_sw) if l_h > 0 and f_sw > 0 else 0.0
            p_out = vout * iload
            eta = 0.9
            p_in = p_out / eta if eta > 0 else p_out
            p_loss = p_in - p_out

            calcs.update(
                {
                    "Topology": "Buck Converter",
                    "Vin": f"{vin:.1f} V",
                    "Vout": f"{vout:.1f} V",
                    "Iload": f"{iload:.2f} A",
                    "Fsw": f"{f_sw/1e3:.1f} kHz",
                    "DutyCycle": f"{duty*100:.1f} %",
                    "InductorRipple": f"{ripple_i:.2f} App",
                    "Pout": f"{p_out:.1f} W",
                    "EfficiencyEst": f"{eta*100:.1f} %",
                    "PlossEst": f"{p_loss:.1f} W",
                }
            )

        elif topo == "led_driver":
            vin = float(self.parameters.get("Vin", 5.0))
            i_led = float(self.parameters.get("ILED", 0.02))
            # Assume one LED at ~2V drop and R chosen ~ (Vin - Vf) / I
            v_f = 2.0 if vin <= 6 else 3.0
            r_val = (vin - v_f) / i_led if i_led > 0 else 0.0
            p_r = (i_led**2) * r_val
            p_led = v_f * i_led

            calcs.update(
                {
                    "Topology": "LED Driver",
                    "Vin": f"{vin:.1f} V",
                    "I_LED": f"{i_led*1e3:.0f} mA",
                    "Rseries": f"{r_val:.0f} Ω",
                    "P_Resistor": f"{p_r*1e3:.1f} mW",
                    "P_LED": f"{p_led*1e3:.1f} mW",
                }
            )

        elif topo == "rc_lowpass":
            vin = float(self.parameters.get("Vin", 5.0))
            r = float(self.parameters.get("R", 1e3))
            c = float(self.parameters.get("C", 1.6e-7))
            fc = 1.0 / (2 * math.pi * r * c) if r > 0 and c > 0 else 0.0

            calcs.update(
                {
                    "Topology": "RC Lowpass",
                    "Vin": f"{vin:.1f} V",
                    "R": f"{r:.0f} Ω",
                    "C": f"{c*1e9:.0f} nF",
                    "Fc": f"{fc:.1f} Hz",
                }
            )

        elif topo == "opamp_non_inverting":
            vin = float(self.parameters.get("Vin", 1.0))
            gain = float(self.parameters.get("Gain", 10.0))
            vout = vin * gain

            calcs.update(
                {
                    "Topology": "Op-Amp (Non-inverting)",
                    "Vin": f"{vin:.2f} V",
                    "Gain": f"{gain:.1f} V/V",
                    "Vout_ideal": f"{vout:.2f} V",
                }
            )

        self.calculations = calcs
        return calcs

    def generate_netlist(self, filename="circuit.net"):
        """
        Generate a simple SPICE-style netlist stub for the current design.
        This will be refined per-topology in later iterations.
        """
        filepath = os.path.join("exports", filename)
        os.makedirs("exports", exist_ok=True)

        topo = self.design_data.get("parameters", {}).get("topology", "")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"* Netlist: {self.project_name}\n")

            if topo == "buck":
                # Very simplified buck netlist skeleton
                p = self.parameters
                vin = float(p.get("Vin", 24.0))
                vout = float(p.get("Vout", 5.0))
                f_sw = float(p.get("Fsw", 100e3))
                f.write(f"V1 VIN 0 {vin}\n")
                f.write("S1 VIN SW SW_CTRL 0 SWMOD\n")
                f.write("L1 SW VOUT 100u\n")
                f.write("C1 VOUT 0 100u\n")
                f.write("RL VOUT 0 10\n")
                f.write(f".tran 0.1u {5.0 / f_sw if f_sw > 0 else 1e-3}\n")

            elif topo == "rc_lowpass":
                p = self.parameters
                vin = float(p.get("Vin", 5.0))
                r = float(p.get("R", 1e3))
                c = float(p.get("C", 1.6e-7))
                f.write(f"V1 VIN 0 {vin}\n")
                f.write(f"R1 VIN VC {r}\n")
                f.write(f"C1 VC 0 {c}\n")
                f.write(".ac dec 20 10 100000\n")

            elif topo == "led_driver":
                p = self.parameters
                vin = float(p.get("Vin", 5.0))
                f.write(f"V1 VIN 0 {vin}\n")
                f.write("R1 VIN VLED 330\n")
                f.write("D1 VLED 0 DLED\n")
                f.write(".dc V1 0 {vin} 0.1\n".replace("{vin}", f"{vin}"))

            elif topo == "opamp_non_inverting":
                p = self.parameters
                vcc = float(p.get("Vcc", 9.0))
                f.write(f"VCC VCC 0 {vcc}\n")
                f.write("VIN VIN 0 AC 1\n")
                f.write("* Op-amp symbol U1 and feedback network omitted in stub\n")
                f.write(".ac dec 20 10 100000\n")

            f.write(".end\n")

        return filepath

    # --------- SPICE & waveform helpers ------------------------------------------
    def simulate_waveforms(self):
        """
        Run SPICE simulation if available and return waveform data.
        Currently this is a safe no-op placeholder that returns empty data
        if the backend is not available.
        """
        if not SPICE_AVAILABLE:
            return {}

        engine = SpiceEngine()
        if not engine.is_available():
            return {}

        # Re-generate a transient netlist in memory
        filepath = self.generate_netlist(filename=f"{self.project_name}.net")
        with open(filepath, "r", encoding="utf-8") as f:
            netlist_text = f.read()

        return engine.run_netlist(netlist_text)

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

    def render_pcb_3d(self, prompt_text=None, show=True):
        """
        Build and optionally display the full 3D 'flux level' PCB.
        
        - If prompt_text is provided, it recompiles the design from that text.
        - Otherwise it uses the last compiled design (or a default buck converter).
        """
        # Ensure we have a compiled design and real-world positions
        if prompt_text is not None:
            self.parse_ai_output(prompt_text)
        elif not self.components:
            # Fallback to a reasonable default if nothing was compiled yet
            self.parse_ai_output(self.prompt_text or "buck converter 24v to 5v")

        # Reset the figure and scene
        self.renderer.fig = go.Figure()
        self.renderer.setup_scene()

        # Compute board extent from component positions for a compact, CAD-like look
        if self.components:
            xs = [c.get("real_x", 0) for c in self.components]
            ys = [c.get("real_y", 0) for c in self.components]
            self.renderer.draw_pcb_stackup(min(xs), max(xs), min(ys), max(ys))

        # Place 3D models for each component
        for comp in self.components:
            x = comp.get("real_x", 0)
            y = comp.get("real_y", 0)
            ctype = comp.get("type", "")
            val = comp.get("value", "")
            pkg = comp.get("package")
            refdes = comp.get("id")

            for trace in FluxAssetLibrary.get_3d_model(ctype, x, y, value=val, package=pkg, refdes=refdes):
                self.renderer.fig.add_trace(trace)

        # Draw net connections as golden traces
        for net in self.design_data.get("netlist", []):
            if len(net) != 2:
                continue
            a_id, b_id = net
            a = next((c for c in self.components if c.get("id") == a_id), None)
            b = next((c for c in self.components if c.get("id") == b_id), None)
            if not a or not b:
                continue
            p1 = [a.get("real_x", 0), a.get("real_y", 0)]
            p2 = [b.get("real_x", 0), b.get("real_y", 0)]
            self.renderer.draw_trace(p1, p2)

        if show:
            self.renderer.fig.show()

        return self.renderer.fig

    # Backwards-compatible name expected by web_ui.py
    def generate_3d_pcb(self, prompt_text=None):
        """Wrapper for older code paths – always returns a Plotly Figure."""
        return self.render_pcb_3d(prompt_text=prompt_text, show=False)