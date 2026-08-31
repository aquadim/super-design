from .enums import NodeType
from .Node import Node
from gi.repository import Gio

# Узел для хранения чего-либо
class StoreNode(Node):
    emoji = "📁"
    can_display_properties_page = False

    def __init__(self, emoji, name, owner_node_id):
        super().__init__(
            owner_node_id+".Storage."+name,
            name,
            None,
            None,
            NodeType.STORAGE,
            Gio.ListStore.new(Node)
        )
        self.emoji = emoji
        self.name_to_node = {}
        self.id_to_node = {}

    def append(self, node):
        self.children.append(node)
        self.id_to_node[node.id] = node
        self.name_to_node[node._Name] = node

    def add_bulk(self, lst):
        for item in lst:
            self.id_to_node[item.id] = item
            self.name_to_node[item._Name] = item
        self.children.splice(0, 0, lst)

    def get_properties(self, configuration):
        return []
