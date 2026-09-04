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

    def append(self, node):
        self.children.append(node)
        self.name_to_node[node.name] = node

    def add_bulk(self, lst):
        for item in lst:
            self.name_to_node[item.name] = item
        self.children.splice(0, 0, lst)
    
    def set_from_dict(self, d):
        self.name_to_node = d
        for k in d:
            self.children.append(d[k])

    def get_properties(self, configuration):
        return []
