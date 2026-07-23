"""Node graph DAG engine with dirty tracking.
Ported from Blender's node graph execution model.
"""

import numpy as np
from typing import Dict, List, Optional, Any
from uuid import uuid4


class Node:
    def __init__(self, node_type: str, label: str = ""):
        self.id = str(uuid4())
        self.type = node_type
        self.label = label or node_type
        self.params: Dict[str, Any] = {}
        self.inputs: List['Socket'] = []
        self.outputs: List['Socket'] = []
        self.dirty = True
        self.bypass = False
        self.enabled = True
        self._cached_output: Optional[np.ndarray] = None

    def process(self, inputs: Dict[str, np.ndarray]) -> np.ndarray:
        raise NotImplementedError

    def to_dict(self) -> dict:
        return {
            'id': self.id, 'type': self.type, 'label': self.label,
            'params': self.params, 'bypass': self.bypass, 'enabled': self.enabled,
        }


class Socket:
    def __init__(self, name: str, socket_type: str = 'color'):
        self.name = name
        self.socket_type = socket_type
        self.connection: Optional[tuple] = None


class NodeGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[tuple] = []

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def remove_node(self, node_id: str):
        self.nodes.pop(node_id, None)
        self.edges = [e for e in self.edges if e[0] != node_id and e[2] != node_id]

    def connect(self, from_id: str, from_socket: str, to_id: str, to_socket: str):
        self.edges.append((from_id, from_socket, to_id, to_socket))
        node = self.nodes.get(to_id)
        if node:
            node.dirty = True

    def disconnect(self, from_id: str, from_socket: str, to_id: str, to_socket: str):
        self.edges = [e for e in self.edges if not (
            e[0] == from_id and e[1] == from_socket and e[2] == to_id and e[3] == to_socket)]

    def get_inputs(self, node_id: str) -> Dict[str, np.ndarray]:
        inputs = {}
        for from_id, from_sock, to_id, to_sock in self.edges:
            if to_id == node_id:
                src = self.nodes.get(from_id)
                if src and src._cached_output is not None:
                    inputs[to_sock] = src._cached_output
        return inputs

    def _has_cycle(self) -> bool:
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {nid: WHITE for nid in self.nodes}

        def dfs(nid):
            color[nid] = GRAY
            for from_id, _, to_id, _ in self.edges:
                if to_id == nid and from_id in color:
                    if color[from_id] == GRAY:
                        return True
                    if color[from_id] == WHITE and dfs(from_id):
                        return True
            color[nid] = BLACK
            return False

        for nid in self.nodes:
            if color[nid] == WHITE and dfs(nid):
                return True
        return False

    def mark_all_dirty(self):
        for node in self.nodes.values():
            node.dirty = True

    def execute(self, input_image: np.ndarray = None) -> Optional[np.ndarray]:
        if not self.nodes:
            return input_image

        if self._has_cycle():
            return input_image

        visited = set()
        order = []

        def dfs(nid):
            if nid in visited:
                return
            visited.add(nid)
            for from_id, _, to_id, _ in self.edges:
                if to_id == nid:
                    dfs(from_id)
            order.append(nid)

        for nid in self.nodes:
            dfs(nid)

        result = input_image
        for nid in order:
            node = self.nodes[nid]
            if not node.enabled:
                continue
            if node.bypass:
                node._cached_output = None
                continue
            if not node.dirty and node._cached_output is not None:
                continue
            inputs = self.get_inputs(nid)
            if 'Image' not in inputs and result is not None:
                inputs['Image'] = result
            try:
                node._cached_output = node.process(inputs)
                result = node._cached_output
            except Exception:
                node._cached_output = None
            node.dirty = False

        return result

    def to_dict(self) -> dict:
        return {
            'nodes': [n.to_dict() for n in self.nodes.values()],
            'edges': self.edges,
        }

    @classmethod
    def from_dict(cls, data: dict, node_classes: Dict[str, type]) -> "NodeGraph":
        graph = cls()
        node_map = {}
        for nd in data.get('nodes', []):
            ntype = nd.get('type', 'unknown')
            ncls = node_classes.get(ntype)
            if ncls is None:
                continue
            node = ncls(nd.get('label', ''))
            node.id = nd.get('id', node.id)
            params = nd.get('params', {})
            if params:
                node.params.update(params)
            node.bypass = nd.get('bypass', False)
            node.enabled = nd.get('enabled', True)
            graph.add_node(node)
            node_map[nd['id']] = node.id
        for edge in data.get('edges', []):
            from_id = node_map.get(edge[0], edge[0])
            to_id = node_map.get(edge[2], edge[2])
            graph.connect(from_id, edge[1], to_id, edge[3])
        return graph
