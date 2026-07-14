"""Node graph DAG engine with dirty tracking.
Ported from Blender's node graph execution model.
"""

import numpy as np
from typing import Dict, List, Optional, Callable, Any
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

    def execute(self) -> Optional[np.ndarray]:
        # Topological sort
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
        # Execute in order
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
            node._cached_output = node.process(inputs)
            node.dirty = False
        # Find output node (last in order)
        if order:
            last = self.nodes[order[-1]]
            return last._cached_output
        return None

    def to_dict(self) -> dict:
        return {
            'nodes': [n.to_dict() for n in self.nodes.values()],
            'edges': self.edges,
        }
