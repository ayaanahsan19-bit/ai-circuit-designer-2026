"""
3D Component Models for Circuit Visualization
"""
import numpy as np
import plotly.graph_objects as go

class Component3D:
    """Base class for 3D electronic components"""
    
    @staticmethod
    def create_resistor(value_ohms, position=(0, 0, 0), rotation=0):
        """Create 3D resistor model"""
        # Resistor body (cylinder)
        length = 0.5
        radius = 0.05
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(-length/2, length/2, 10)
        theta, z = np.meshgrid(theta, z)
        
        x = radius * np.cos(theta) + position[0]
        y = radius * np.sin(theta) + position[1]
        z = z + position[2]
        
        # Resistor color bands
        colors = ['#8B0000', '#000000', '#FFD700', '#0000FF']  # Red, Black, Gold, Blue
        
        # Create 3D mesh
        mesh = go.Mesh3d(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            color='#C0C0C0',  # Metal gray
            opacity=0.9,
            name=f'Resistor {value_ohms}Ω'
        )
        
        return mesh
    
    @staticmethod
    def create_capacitor(value_farads, position=(1, 0, 0), type='ceramic'):
        """Create 3D capacitor model"""
        # Capacitor body (two cylinders with gap)
        height = 0.3
        radius = 0.08
        
        # Create main body
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(0, height, 10)
        theta, z = np.meshgrid(theta, z)
        
        x = radius * np.cos(theta) + position[0]
        y = radius * np.sin(theta) + position[1]
        z = z + position[2]
        
        mesh = go.Mesh3d(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            color='#4682B4',  # Steel blue
            opacity=0.8,
            name=f'Capacitor {value_farads:.6f}F'
        )
        
        return mesh
    
    @staticmethod
    def create_pcb_board(size=(3, 2, 0.1), position=(0, 0, -0.2)):
        """Create 3D PCB board"""
        # PCB as a flat rectangular prism
        x = [position[0], position[0] + size[0], position[0] + size[0], position[0]]
        y = [position[1], position[1], position[1] + size[1], position[1] + size[1]]
        z = [position[2], position[2], position[2], position[2]]
        
        # Extrude to create 3D
        vertices = []
        for i in range(len(x)):
            vertices.append([x[i], y[i], z[i]])
            vertices.append([x[i], y[i], z[i] + size[2]])
        
        mesh = go.Mesh3d(
            x=[v[0] for v in vertices],
            y=[v[1] for v in vertices],
            z=[v[2] for v in vertices],
            color='#2E8B57',  # Sea green (PCB color)
            opacity=0.7,
            name='PCB Board'
        )
        
        return mesh