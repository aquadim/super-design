from gi.repository import GObject
import properties as p

# Узел конфигурации
class Node(GObject.Object):
    __gtype_name__ = 'DataObject'
    emoji = "👽"
    can_display_properties_page = False

    def __init__(self, id, Name, Synonym, Comment, node_type, children=[]):
        super().__init__()
        self.id = id
        self._Name = Name
        self.Synonym = Synonym
        self.Comment = Comment
        self.node_type = node_type
        self.children = children

    @GObject.Property(type=str, default=None)
    def name(self):
        return self._Name

    @name.setter
    def name(self, value):
        self._Name = value

    def get_properties(self):
        return [
            p.BindText("name", self, self._Name),
            p.Localised("Synonym", self, self.Synonym),
            p.Text("Comment", self, self.Comment),
        ]

    def export(self, root_path):
        pass
