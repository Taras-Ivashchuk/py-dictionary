from dataclasses import dataclass
from typing import Hashable, Any, Union


@dataclass
class Node:
    node_key: Hashable
    node_hash: int
    node_value: Any


# singleton
DELETED = object()


class Dictionary:
    def __init__(self) -> None:
        self.capacity: int = 8
        self.load_factor: float = 2 / 3
        self.threshold: int = int(self.capacity * self.load_factor)
        self.size: int = 0
        self.nodes: list[Node | None] = [None] * self.capacity

    def __setitem__(self, key: Hashable, value: Any) -> None:
        if self.size >= self.threshold:
            self.capacity *= 2
            self.threshold = int(self.capacity * self.load_factor)
            new_nodes = [None] * self.capacity
            for node in self.nodes:
                if not self.__is_empty(node) and not self.__is_deleted(node):
                    rehashed_node = Node(
                        node.node_key,
                        hash(node.node_key),
                        node.node_value
                    )
                    self.__add_node(new_nodes, rehashed_node)
            self.nodes = new_nodes
        new_node = Node(key, hash(key), value)
        # what will happen if add_node returns false? Will capacity increase?
        if self.__add_node(self.nodes, new_node):
            self.size += 1

    @staticmethod
    def __is_empty(node: Node) -> bool:
        return node is None

    @staticmethod
    def __is_deleted(node: Node) -> bool:
        return node is DELETED

    def __add_node(
            self,
            nodes: list[Union[Node, None, object]],
            node: Union[Node, None, object]
    ) -> bool:
        """ True = new item inserted; False: = updated / ignored"""

        if node is None or node is DELETED:
            return False

        slot = node.node_hash % len(nodes)

        # 1. Add the new node
        if self.__is_empty(nodes[slot]) or self.__is_deleted(nodes[slot]):
            nodes[slot] = node
            return True
        # 2. Overwrite the old value
        if (node.node_hash == nodes[slot].node_hash
                and node.node_key == nodes[slot].node_key):
            nodes[slot].node_value = node.node_value
            return False
        # 3. Collision detected
        if nodes[slot].node_key != node.node_key:
            # find an empty slot
            new_slot_inx = (slot + 1) % len(nodes)
            for _ in range(len(nodes)):
                # insert into empty slot
                if (self.__is_empty(nodes[new_slot_inx])
                        or self.__is_deleted(nodes[new_slot_inx])):
                    nodes[new_slot_inx] = node
                    return True
                # overwrite the old value
                if nodes[new_slot_inx].node_key == node.node_key:
                    nodes[new_slot_inx].node_value = node.node_value
                    return False

                new_slot_inx = (new_slot_inx + 1) % len(nodes)
            else:
                raise Exception(f"Size: {len(nodes)} no empty slots found")
        return False

    def __getitem__(self, obj: Any) -> Any:
        key_hash = hash(obj)
        slot = key_hash % self.capacity

        for _ in range(self.capacity):
            if self.__is_empty(self.nodes[slot]):
                raise KeyError(f"{obj} is not found in dictionary")
            if self.__is_deleted(self.nodes[slot]):
                slot = (slot + 1) % self.capacity
                continue
            if (self.nodes[slot].node_hash == key_hash
                    and self.nodes[slot].node_key == obj):
                return self.nodes[slot].node_value
            slot = (slot + 1) % self.capacity
        raise KeyError(f"{obj} is not found in dictionary")

    def __len__(self) -> int:
        return self.size

    def clear(self) -> None:
        self.size = 0
        self.capacity = 8
        self.threshold = int(self.capacity * self.load_factor)
        self.nodes = [None] * self.capacity

    def __delitem__(self, obj: Any) -> None:
        key_hash = hash(obj)
        slot = key_hash % self.capacity

        for _ in range(self.capacity):
            if self.__is_empty(self.nodes[slot]):
                raise KeyError(f"{obj} is not found in dictionary")
            if self.__is_deleted(self.nodes[slot]):
                slot = (slot + 1) % self.capacity
                continue
            if (self.nodes[slot].node_hash == hash(obj)
                    and self.nodes[slot].node_key == obj):
                self.nodes[slot] = DELETED
                self.size -= 1
                break
            slot = (slot + 1) % self.capacity
        else:
            raise KeyError(f"{obj} is not found in dictionary")

    def get(self, node: Node, default: Any = None) -> Any:
        try:
            return self.__getitem__(node)
        except KeyError:
            return default

    def pop(self, obj: Any, default: Any = None) -> Any:
        try:
            value = self.get(obj, default)
            self.__delitem__(obj)
            return value
        except KeyError:
            if default is not None:
                return default
            else:
                raise
