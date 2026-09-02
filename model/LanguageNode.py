from .Node import Node
from .enums import NodeType
import properties as p

# Язык
class LanguageNode(Node):
    emoji = '💬'
    can_display_properties_page = True

    def __init__(self, name, Synonym, Comment, LanguageCode):
        super().__init__(
            f"Language.{LanguageCode}",
            name,
            Synonym,
            Comment,
            NodeType.LANGUAGE,
            []
        )
        self.LanguageCode = LanguageCode

    def get_properties(self, configuration):
        return super().get_properties(configuration) + [
            p.Text("LanguageCode", self, self.LanguageCode),
        ]