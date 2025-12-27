"""
3D Circuit Visualization Engine
"""
import plotly.graph_objects as go
from .component_library import Component3D
import numpy as np

class Circuit3DVisualizer:
    """Creates 3D circuit visualizations from AI parameters"""
    
    def __init__(self):
        self.components = []
        self.traces = []
    
    def create_circuit_from_ai(self, ai_output):
        """
        Convert AI output to 3D circuit layout
        ai_output: tensor/list of [resistance, capacitance, inductance, etc.]
        """
        # Extract values (normalize for visualization)
        values = ai_output if isinstance(ai_output, list) else ai_output.tolist()
        
        # Create PCB board
        pcb = Component3D.create_pcb_board()
        self.traces.append(pcb)
        
        # Place components on PCB
        positions = [
            (0.5, 0.5, 0.1),   # Resistor
            (1.5, 0.5, 0.1),   # Capacitor
            (2.0, 1.0, 0.1),   # Voltage source
            (0.5, 1.5, 0.1),   # Optional: Inductor
        ]
        
        # Create resistor
        if len(values) > 0:
            resistor = Component3D.create_resistor(
                value_ohms=values[0] * 1000 if values[0] < 1 else values[0],
                position=positions[0]
            )
            self.traces.append(resistor)
        
        # Create capacitor
        if len(values) > 1:
            capacitor = Component3D.create_capacitor(
                value_farads=values[1],
                position=positions[1]
            )
            self.traces.append(capacitor)
        
        # Create wires/connections
        self._add_wires(positions)
        
        return self._create_3d_scene()
    
    def _add_wires(self, positions):
        """Add 3D wires between components"""
        for i in range(len(positions) - 1):
            wire = self._create_wire(
                start=positions[i],
                end=positions[i+1],
                thickness=0.02
            )
            self.traces.append(wire)
    
    def _create_wire(self, start, end, thickness=0.02):
        """Create a 3D wire/connection"""
        # Create cylinder between two points
        length = np.linalg.norm(np.array(end) - np.array(start))
        
        # Generate cylinder mesh
        theta = np.linspace(0, 2*np.pi, 20)
        z = np.linspace(0, length, 10)
        theta, z = np.meshgrid(theta, z)
        
        x = thickness * np.cos(theta)
        y = thickness * np.sin(theta)
        
        # Rotate to connect start and end points
        # (Simplified - in reality need proper rotation matrix)
        
        # Translate to start position
        x = x + start[0]
        y = y + start[1]
        z = z + start[2]
        
        return go.Mesh3d(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            color='#FFD700',  # Gold wire
            opacity=0.8,
            name='Wire'
        )
    
    def _create_3d_scene(self):
        """Create complete 3D scene"""
        fig = go.Figure(data=self.traces)
        
        fig.update_layout(
            title='3D Circuit Visualization',
            scene=dict(
                xaxis_title='X (mm)',
                yaxis_title='Y (mm)',
                zaxis_title='Z (mm)',
                aspectmode='data'
            ),
            width=1000,
            height=700,
            showlegend=True
        )
        
        return fig