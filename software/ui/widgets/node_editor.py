"""Visual node editor: draggable nodes, socket connections, bypass."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGraphicsView,
                               QGraphicsScene, QGraphicsItem, QPushButton,
                               QHBoxLayout, QMenu, QInputDialog)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import (QPainter, QPen, QColor, QBrush, QFont,
                           QMouseEvent, QKeyEvent)
from core.node_graph import Node, NodeGraph


class NodeItem(QGraphicsItem):
    def __init__(self, node: Node, index: int = 0):
        super().__init__()
        self.node = node
        self._index = index
        self._w = 180
        self._h = 60 + max(len(node.inputs), len(node.outputs)) * 20
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setPos(20 + index * 40, 20 + index * 60)

    def boundingRect(self):
        return QRectF(0, 0, self._w, self._h)

    def paint(self, painter, option, widget):
        rect = self.boundingRect()
        color = QColor(55, 55, 65) if not self.node.bypass else QColor(70, 50, 50)
        if self.isSelected():
            color = QColor(68, 120, 200)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(80, 80, 90), 1))
        painter.drawRoundedRect(rect, 6, 6)
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Segoe UI", 9))
        label = f"[{'x' if self.node.bypass else ' '}] {self.node.label}"
        painter.drawText(rect.adjusted(8, 4, -8, -4), Qt.AlignLeft | Qt.AlignTop, label)
        y0 = 22
        painter.setFont(QFont("Segoe UI", 7))
        for i, inp in enumerate(self.node.inputs):
            painter.setPen(QColor(180, 180, 100))
            painter.drawText(4, y0 + i * 18, inp.name)
        for i, out in enumerate(self.node.outputs):
            painter.setPen(QColor(100, 180, 180))
            tw = painter.fontMetrics().horizontalAdvance(out.name)
            painter.drawText(self._w - tw - 4, y0 + i * 18, out.name)


class NodeEditorScene(QGraphicsScene):
    node_changed = Signal()

    def __init__(self, graph: NodeGraph, parent=None):
        super().__init__(parent)
        self.graph = graph
        self._items: dict = {}
        self._rebuild()

    def _rebuild(self):
        self.clear()
        self._items.clear()
        for i, (nid, node) in enumerate(self.graph.nodes.items()):
            item = NodeItem(node, i)
            self.addItem(item)
            self._items[nid] = item


class NodeEditor(QWidget):
    graph_changed = Signal()

    def __init__(self, graph: NodeGraph, node_classes: dict, parent=None):
        super().__init__(parent)
        self.graph = graph
        self.node_classes = node_classes
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scene = NodeEditorScene(self.graph)
        self._view = QGraphicsView(self._scene)
        self._view.setStyleSheet("background-color: #1a1a1e; border: none;")
        self._view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self._view, 1)

        btn_row = QHBoxLayout()
        for text, cb in [("Add Node", self._add_node),
                         ("Bypass", self._toggle_bypass),
                         ("Delete", self._delete_selected),
                         ("Reset Graph", self._reset)]:
            btn = QPushButton(text)
            btn.clicked.connect(cb)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

    def _add_node(self):
        names = sorted(self.node_classes.keys())
        name, ok = QInputDialog.getItem(self, "Add Node", "Node type:", names, 0, False)
        if ok and name:
            cls = self.node_classes[name]
            node = cls(name)
            self.graph.add_node(node)
            self._scene._rebuild()
            self.graph_changed.emit()

    def _toggle_bypass(self):
        for item in self._view.items():
            if isinstance(item, NodeItem) and item.isSelected():
                item.node.bypass = not item.node.bypass
                item.update()
                self.graph_changed.emit()

    def _delete_selected(self):
        to_remove = [item.node.id for item in self._view.items()
                     if isinstance(item, NodeItem) and item.isSelected()]
        for nid in to_remove:
            self.graph.remove_node(nid)
        self._scene._rebuild()
        self.graph_changed.emit()

    def _reset(self):
        self.graph.nodes.clear()
        self.graph.edges.clear()
        self._scene._rebuild()
        self.graph_changed.emit()

    def rebuild(self):
        self._scene._rebuild()
