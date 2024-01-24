import uuid
from dataclasses import dataclass, field
from enum import Enum
from itertools import count
from typing import Set, List

from dataclasses_json import dataclass_json


class NodeTag(Enum):
    DEFAULT = "default"
    PRIMARY = "primary"
    INSERTED = "inserted"
    LEAF = "leaf"
    ROOT = "root"
    SINGLE = "single"


@dataclass_json
@dataclass(frozen=True)
class NodeData:
    label: str = ""
    value: float = 0.0
    tag: NodeTag = NodeTag.DEFAULT

    def __str__(self):
        return f"NodeData(label={self.label!r}, value={self.value}, tag={self.tag.value})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.label == other.label and self.value == other.value and self.tag == other.tag
        return False


@dataclass_json
@dataclass(frozen=True)
class TreeNode:
    data: NodeData = NodeData()
    children: List["TreeNode"] = field(default_factory=list)

    def __str__(self):
        children_str = ", ".join(str(child) for child in self.children)
        return f"Node(data={self.data}, children=[{children_str}])"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.data == other.data
        return False


class State(Enum):
    INVALID = "invalid"
    START = "start"
    MATCHED = "matched"
    COMPARED = "compared"
    EXPANDING = "expanding"
    EXPANDED = "expanded"
    REVERSING = "reversing"
    REVERSED = "reversed"
    FINISH = "finish"


@dataclass_json
@dataclass(frozen=True)
class Move:
    source: Set[str] = field(default_factory=set)
    target: Set[str] = field(default_factory=set)


@dataclass_json
@dataclass(frozen=True)
class Status:
    value: float = 0.0
    state: State = State.START


@dataclass_json
@dataclass(frozen=True)
class MoveGroup:
    applied: List[Move] = field(default_factory=list)
    possible: List[Move] = field(default_factory=list)
    base: List[Move] = field(default_factory=list)
    reverse: List[Move] = field(default_factory=list)


@dataclass_json
@dataclass(frozen=True)
class Record:
    node: TreeNode
    moves: MoveGroup = MoveGroup()


@dataclass_json
@dataclass(frozen=True)
class Decision:
    data: List[Record] = field(default_factory=list)
    status: Status = Status()
    children: List["Decision"] = field(default_factory=list)
    label: int = field(default_factory=count().__next__, init=False)

    def __str__(self):
        children_str = ", ".join(str(child) for child in self.children)
        return f"DecisionNode(decision_data={self.data}, children=[{children_str}])"
