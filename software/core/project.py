"""Project save/load in .daviciproj JSON format.

Serialises full grade state: media path, grade params, LUT reference,
node graph, and panel layout.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from pathlib import Path


PROJECT_VERSION = "1.0"
RECENT_FILE = os.path.join(str(Path.home()), ".daviciresolve", "recent.json")


@dataclass
class GradeParams:
    lift: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    gamma: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    gain: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    offset: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    contrast: float = 0.0
    saturation: float = 0.0
    exposure: float = 0.0
    temp: float = 0.0
    tint: float = 0.0
    lut_path: Optional[str] = None


@dataclass
class Project:
    version: str = PROJECT_VERSION
    media_path: Optional[str] = None
    grade: GradeParams = field(default_factory=GradeParams)
    node_graph: Optional[Dict[str, Any]] = None
    panel_layout: Dict[str, Any] = field(default_factory=dict)
    versions: Optional[List[Dict[str, Any]]] = None
    version_index: int = -1

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "Project":
        with open(path, "r") as f:
            data = json.load(f)
        grade = GradeParams(**data.get("grade", {}))
        return cls(
            version=data.get("version", "1.0"),
            media_path=data.get("media_path"),
            grade=grade,
            node_graph=data.get("node_graph"),
            panel_layout=data.get("panel_layout", {}),
            versions=data.get("versions"),
            version_index=data.get("version_index", -1),
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        grade = GradeParams(**data.get("grade", {}))
        return cls(
            version=data.get("version", "1.0"),
            media_path=data.get("media_path"),
            grade=grade,
            node_graph=data.get("node_graph"),
            panel_layout=data.get("panel_layout", {}),
            versions=data.get("versions"),
            version_index=data.get("version_index", -1),
        )


# ─── Recent files management ───


def get_recent_files(max_items: int = 10) -> List[str]:
    try:
        with open(RECENT_FILE, "r") as f:
            recent = json.load(f)
        return recent[:max_items]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def add_recent_file(path: str):
    os.makedirs(os.path.dirname(RECENT_FILE), exist_ok=True)
    recent = get_recent_files()
    path = os.path.abspath(path)
    if path in recent:
        recent.remove(path)
    recent.insert(0, path)
    with open(RECENT_FILE, "w") as f:
        json.dump(recent[:20], f)
