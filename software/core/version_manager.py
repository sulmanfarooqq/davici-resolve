"""Version management: multiple grade versions per clip."""

import copy
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class GradeVersion:
    name: str
    grade_params: dict
    lut_path: Optional[str] = None
    node_graph: Optional[dict] = None


class VersionManager:
    def __init__(self):
        self._versions: List[GradeVersion] = []
        self._current_index: int = -1

    @property
    def versions(self) -> List[GradeVersion]:
        return self._versions

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def current_version(self) -> Optional[GradeVersion]:
        if 0 <= self._current_index < len(self._versions):
            return self._versions[self._current_index]
        return None

    def add_version(self, name: str, grade_params: dict,
                    lut_path: Optional[str] = None,
                    node_graph: Optional[dict] = None) -> int:
        v = GradeVersion(
            name=name,
            grade_params=copy.deepcopy(grade_params),
            lut_path=lut_path,
            node_graph=copy.deepcopy(node_graph) if node_graph else None,
        )
        self._versions.append(v)
        self._current_index = len(self._versions) - 1
        return self._current_index

    def select_version(self, index: int) -> Optional[GradeVersion]:
        if 0 <= index < len(self._versions):
            self._current_index = index
            return self._versions[index]
        return None

    def update_current(self, grade_params: dict, lut_path: Optional[str] = None,
                       node_graph: Optional[dict] = None):
        if 0 <= self._current_index < len(self._versions):
            v = self._versions[self._current_index]
            v.grade_params = copy.deepcopy(grade_params)
            v.lut_path = lut_path
            v.node_graph = copy.deepcopy(node_graph) if node_graph else None

    def delete_version(self, index: int):
        if 0 < index < len(self._versions):
            self._versions.pop(index)
            if self._current_index >= len(self._versions):
                self._current_index = len(self._versions) - 1

    def rename_version(self, index: int, name: str):
        if 0 <= index < len(self._versions):
            self._versions[index].name = name

    def get_snapshot(self) -> dict:
        return {
            'versions': [
                {
                    'name': v.name,
                    'grade_params': copy.deepcopy(v.grade_params),
                    'lut_path': v.lut_path,
                    'node_graph': copy.deepcopy(v.node_graph) if v.node_graph else None,
                }
                for v in self._versions
            ],
            'current_index': self._current_index,
        }

    def load_snapshot(self, data: dict):
        self._versions = []
        for vd in data.get('versions', []):
            self._versions.append(GradeVersion(
                name=vd.get('name', 'Version'),
                grade_params=vd.get('grade_params', {}),
                lut_path=vd.get('lut_path'),
                node_graph=vd.get('node_graph'),
            ))
        self._current_index = data.get('current_index', -1)
