from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


Coord = Tuple[float, float]


class BoardOutline(BaseModel):
    """Board outer contour and optional cutouts, in mm coordinates."""

    outline: List[Coord] = Field(..., description="Closed polygon for board edge")
    cutouts: List[List[Coord]] = Field(
        default_factory=list, description="Optional internal cutout polygons"
    )


class StackupLayer(BaseModel):
    name: str
    type: str  # e.g. 'signal', 'plane', 'solder_mask', 'silkscreen'
    copper_oz: Optional[float] = None
    color: Optional[str] = None  # e.g. '#008800' for mask


class Stackup(BaseModel):
    thickness_mm: float = 1.6
    layers: List[StackupLayer]


class Component(BaseModel):
    ref: str  # 'Q1'
    footprint_id: str  # library footprint identifier
    model3d_id: Optional[str] = None  # glTF model reference
    x: float
    y: float
    rot_deg: float = 0.0
    side: str = "top"  # 'top' or 'bottom'
    nets: Dict[str, str] = Field(
        default_factory=dict, description="pin_name -> net_name mapping"
    )


class TracePrimitive(BaseModel):
    """
    Logical trace description.

    Stores only a small vertex list describing the polyline on a layer.
    The manufacturing backend is responsible for turning this into
    Gerber segments.
    """

    id: str
    net: str
    layer: str  # e.g. 'F.Cu'
    width_mm: float
    path: List[Coord] = Field(
        ..., description="Polyline vertices (Manhattan / 45-degree only)."
    )


class ViaPrimitive(BaseModel):
    id: str
    net: str
    x: float
    y: float
    drill_mm: float
    diameter_mm: float
    start_layer: str
    end_layer: str


class CopperZone(BaseModel):
    id: str
    net: str
    layer: str
    polygon: List[Coord]
    clearance_mm: float
    min_width_mm: float


class NetClass(BaseModel):
    name: str
    width_mm: float
    clearance_mm: float
    via_diameter_mm: float
    via_drill_mm: float
    max_current_a: Optional[float] = None


class Constraints(BaseModel):
    netclasses: Dict[str, NetClass] = Field(default_factory=dict)
    netclass_map: Dict[str, str] = Field(
        default_factory=dict, description="net_name -> netclass name"
    )


class CorePCBModel(BaseModel):
    """
    Canonical PCB representation shared by API, workers, and viewers.
    """

    id: str
    board_outline: BoardOutline
    stackup: Stackup
    components: List[Component] = Field(default_factory=list)
    nets: List[str] = Field(default_factory=list)
    traces: List[TracePrimitive] = Field(default_factory=list)
    vias: List[ViaPrimitive] = Field(default_factory=list)
    zones: List[CopperZone] = Field(default_factory=list)
    constraints: Constraints = Field(default_factory=Constraints)
    revision: int = 0  # incremented on each accepted patch

