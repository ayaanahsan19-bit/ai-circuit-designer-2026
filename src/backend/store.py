"""
Project storage abstraction.

In production this would use PostgreSQL (via SQLAlchemy or similar) to
persist CorePCBModel instances. For now we keep a simple in-memory
dictionary plus function signatures to make the FastAPI layer testable.
"""

from __future__ import annotations

from typing import Dict

from core.models.pcb import CorePCBModel


_IN_MEMORY_PROJECTS: Dict[str, CorePCBModel] = {}


def get_project(project_id: str) -> CorePCBModel:
    """
    Load a project by id.

    Replace this in production with a PostgreSQL-backed implementation.
    """
    if project_id not in _IN_MEMORY_PROJECTS:
        raise KeyError(f"Project {project_id} not found")
    return _IN_MEMORY_PROJECTS[project_id]


def save_project(model: CorePCBModel) -> None:
    """
    Persist (or update) a project.

    In a real deployment this would perform an UPSERT into PostgreSQL.
    """
    _IN_MEMORY_PROJECTS[model.id] = model

