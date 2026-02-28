"""
Job queue abstractions.

This module defines a thin interface that the FastAPI layer can use to
enqueue background work without depending directly on Celery or RQ.

In production, these functions should be implemented using Redis +
Celery/RQ workers. For now they return dummy job ids so the HTTP API
remains testable.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Literal


def _new_job_id() -> str:
    return f"job_{uuid.uuid4().hex[:16]}"


def enqueue_export_gerber(project_id: str, export_hash: str, config: Dict[str, Any]) -> str:
    """
    Enqueue a Gerber export job.
    """
    return _new_job_id()


def enqueue_rasterize(export_hash: str, texture_hash: str, config: Dict[str, Any]) -> str:
    """
    Enqueue a Gerber rasterization job.
    """
    return _new_job_id()


def enqueue_simulation(project_id: str, sim_hash: str, config: Dict[str, Any]) -> str:
    """
    Enqueue a waveform simulation job.
    """
    return _new_job_id()


def enqueue_drc(project_id: str, export_hash: str) -> str:
    """
    Enqueue a DRC job.
    """
    return _new_job_id()


def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Return a simple job status structure.

    In a real system this would query Redis / the job backend.
    """
    return {"job_id": job_id, "status": "queued"}

