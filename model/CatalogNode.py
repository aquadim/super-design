from .Node import Node
from .StoreNode import StoreNode
from .enums import NodeType
import properties as p

# Справочник
class CatalogNode(Node):
    emoji = '📦'
    can_display_properties_page = True

    def __init__(
        self,
        name,
        Synonym,
        Comment,
        Hierarchical,
        HierarchyType,
        LimitLevelCount,
        LevelCount,
        FoldersOnTop,
        ObjectPresentation,
        ExtendedObjectPresentation,
        ListPresentation,
        ExtendedListPresentation,
        Explanation,
    ):
        ID = f"Catalog.{name}"

        self.store_attribute = StoreNode("➖", "Реквизиты", ID)

        super().__init__(
            ID,
            name,
            Synonym,
            Comment,
            NodeType.CATALOG,
            [
                self.store_attribute,
            ]
        )

        self.Hierarchical = Hierarchical
        self.HierarchyType = HierarchyType
        self.LimitLevelCount = LimitLevelCount
        self.LevelCount = LevelCount
        self.FoldersOnTop = FoldersOnTop
        self.ObjectPresentation = ObjectPresentation
        self.ExtendedObjectPresentation = ExtendedObjectPresentation
        self.ListPresentation = ListPresentation
        self.ExtendedListPresentation = ExtendedListPresentation
        self.Explanation = Explanation

        self.ObjectModule = None
        self.ManagerModule = None

    def get_properties(self, configuration):
        return super().get_properties(configuration) + [
            p.Bool("Hierarchical", self, self.Hierarchical),
            p.Enum("HierarchyType", self, self.HierarchyType),
            p.Bool("FoldersOnTop", self, self.FoldersOnTop),
            p.Bool("LimitLevelCount", self, self.LimitLevelCount),
            p.Num("LevelCount", self, self.LevelCount),
            p.Localised("ObjectPresentation", self, configuration.store_lang),
            p.Localised("ExtendedObjectPresentation", self, configuration.store_lang),
            p.Localised("ListPresentation", self, configuration.store_lang),
            p.Localised("ExtendedListPresentation", self, configuration.store_lang),
            p.Localised("Explanation", self, configuration.store_lang, True),
            p.SourceCode("ManagerModule", self, self.ManagerModule),
            p.SourceCode("ObjectModule", self, self.ObjectModule),
            #p.AttributesProperty(CategoryType.ATTRIBUTES, self, 'store_attribute', self.store_attribute)
        ]