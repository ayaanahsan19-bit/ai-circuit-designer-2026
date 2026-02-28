from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel

from core.models.pcb import CorePCBModel
from backend import jobs, store


app = FastAPI(title="AI PCB Platform API")


def _canonical_json(model: BaseModel) -> str:
    return model.model_dump_json(sort_keys=True, exclude_none=True)


def compute_design_hash(model: CorePCBModel) -> str:
    data = _canonical_json(model).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


class ProjectCreate(BaseModel):
    project: CorePCBModel


class PatchOp(BaseModel):
    op: str
    data: Dict[str, Any]


class PatchRequest(BaseModel):
    ops: List[PatchOp]


class ExportResponse(BaseModel):
    job_id: Optional[str]
    status: str
    export_hash: Optional[str] = None


class RasterizeRequest(BaseModel):
    export_hash: str
    resolutions: List[int] = [512, 1024, 2048, 4096]


class RasterizeResponse(BaseModel):
    job_id: Optional[str]
    status: str
    texture_hash: Optional[str] = None


class SimulateRequest(BaseModel):
    sim_config: Dict[str, Any]
    netlist_source: str = "schematic"


class SimulateResponse(BaseModel):
    job_id: Optional[str]
    status: str
    sim_hash: Optional[str] = None


@app.post("/projects", response_model=CorePCBModel)
def create_project(payload: ProjectCreate):
    model = payload.project
    # In a real system we would validate uniqueness and insert into Postgres.
    store.save_project(model)
    return model


@app.get("/projects/{project_id}", response_model=CorePCBModel)
def get_project(project_id: str):
    try:
        return store.get_project(project_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.patch("/projects/{project_id}", response_model=CorePCBModel)
def patch_project(project_id: str, patch: PatchRequest):
    try:
        model = store.get_project(project_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Minimal patch engine: apply a few well-known operations.
    for op in patch.ops:
        if op.op == "move_component":
            ref = op.data["ref"]
            dx = op.data.get("dx")
            dy = op.data.get("dy")
            x = op.data.get("x")
            y = op.data.get("y")
            for c in model.components:
                if c.ref == ref:
                    if x is not None:
                        c.x = float(x)
                    if y is not None:
                        c.y = float(y)
                    if dx is not None:
                        c.x += float(dx)
                    if dy is not None:
                        c.y += float(dy)
                    break
        elif op.op == "add_trace":
            model.traces.append(op.data)  # FastAPI will coerce via model validation
        # Additional operations (delete_trace, add_via, etc.) can be added here.

    model.revision += 1
    store.save_project(model)
    return model


@app.post("/projects/{project_id}/export-gerber", response_model=ExportResponse)
def export_gerber(project_id: str, config: Dict[str, Any] = Body(default_factory=dict)):
    try:
        model = store.get_project(project_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")

    design_hash = compute_design_hash(model)
    export_key_material = json.dumps(config, sort_keys=True).encode("utf-8")
    export_hash = hashlib.sha256(design_hash.encode("utf-8") + export_key_material).hexdigest()

    # In a full implementation we would check the artifact store for this export_hash.
    job_id = jobs.enqueue_export_gerber(project_id, export_hash, config)
    return ExportResponse(job_id=job_id, status="queued", export_hash=export_hash)


@app.get("/projects/{project_id}/gerber-status")
def gerber_status(job_id: str):
    return jobs.get_job_status(job_id)


@app.post("/projects/{project_id}/rasterize", response_model=RasterizeResponse)
def rasterize(project_id: str, payload: RasterizeRequest):
    texture_key_material = json.dumps(
        {"export_hash": payload.export_hash, "res": payload.resolutions},
        sort_keys=True,
    ).encode("utf-8")
    texture_hash = hashlib.sha256(texture_key_material).hexdigest()
    job_id = jobs.enqueue_rasterize(payload.export_hash, texture_hash, payload.model_dump())
    return RasterizeResponse(job_id=job_id, status="queued", texture_hash=texture_hash)


@app.post("/projects/{project_id}/simulate", response_model=SimulateResponse)
def simulate(project_id: str, payload: SimulateRequest):
    sim_key_material = json.dumps(payload.sim_config, sort_keys=True).encode("utf-8")
    sim_hash = hashlib.sha256(sim_key_material).hexdigest()
    job_id = jobs.enqueue_simulation(project_id, sim_hash, payload.sim_config)
    return SimulateResponse(job_id=job_id, status="queued", sim_hash=sim_hash)


@app.get("/projects/{project_id}/simulation-status")
def simulation_status(job_id: str):
    return jobs.get_job_status(job_id)


@app.post("/projects/{project_id}/run-drc")
def run_drc(project_id: str, export_hash: str = Body(..., embed=True)):
    job_id = jobs.enqueue_drc(project_id, export_hash)
    return {"job_id": job_id, "status": "queued"}


@app.get("/projects/{project_id}/drc-report")
def drc_report(project_id: str, export_hash: str):
    # Placeholder: in production we would stream a JSON report from the artifact store.
    return {"project_id": project_id, "export_hash": export_hash, "status": "not_implemented"}

