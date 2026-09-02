from gi.repository import Gio
from .enums import NodeType

from .Node import Node
from .StoreNode import StoreNode
import properties

# Класс для ленивой загрузки кода
class LazySourceCode:
    __slots__ = ("tabid", "code_type", "node", "file_path", "content", "loaded")

    def __init__(self, file_path, node, code_type):
        self.file_path = file_path
        self.node = node
        self.content = ""
        self.loaded = False
        self.tabid = f"sourcecode{code_type.written()}:"+node.id
        self.code_type = code_type

    def get_content(self):
        if not self.loaded:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.content = f.read()
            except FileNotFoundError:
                self.content = ""
            self.loaded = True
        return self.content

# Подсистема
class SubsystemNode(Node):
    emoji = '🗂️'
    can_display_properties_page = True

    def __init__(self,
                 name,
                 Synonym,
                 Comment,
                 IncludeInCommandInterface,
                 UseOneCommand,
                 Explanation,
    ):
        super().__init__(
            f"subsystem:{name}",
            name,
            Synonym,
            Comment,
            NodeType.SUBSYSTEM,
            Gio.ListStore.new(Node),
        )
        self.IncludeInCommandInterface = IncludeInCommandInterface
        self.UseOneCommand = UseOneCommand
        self.Explanation = Explanation
        self.Content = Gio.ListStore.new(Node)

    def get_properties(self):
        return super().get_properties() + [
            properties.BoolProperty(
                CategoryType.GENERAL,
                self,
                'IncludeInCommandInterface',
                self.IncludeInCommandInterface,
                "Включать в командный интерфейс"),
            properties.BoolProperty(
                CategoryType.GENERAL,
                self,
                'UseOneCommand',
                self.UseOneCommand,
                "Подсистема с одной командой"),
            properties.LocalisedStringProperty(
                CategoryType.GENERAL,
                self,
                'Explanation',
                self.Explanation,
                "Пояснение",
                True),
            properties.SubsystemContentProperty(
                CategoryType.SUBSYSTEMCONTENT,
                self,
                'Content',
                self.Content),
        ]


# Общий модуль
class CommonModuleNode(Node):
    emoji = '📃'
    can_display_properties_page = True

    def __init__(self, name, Synonym, Comment,
        Global,
        ClientManagedApplication,
        Server,
        ExternalConnection,
        ClientOrdinaryApplication,
        ServerCall,
        Privileged,
        ReturnValuesReuse,
    ):
        super().__init__(
            f"CommonModule.{name}",
            name,
            Synonym,
            Comment,
            NodeType.COMMONMODULE,
            Gio.ListStore.new(Node),
        )
        self.Global = Global
        self.ClientManagedApplication = ClientManagedApplication
        self.Server = Server
        self.ExternalConnection = ExternalConnection
        self.ClientOrdinaryApplication = ClientOrdinaryApplication
        self.ServerCall = ServerCall
        self.Privileged = Privileged
        self.ReturnValuesReuse = ReturnValuesReuse

    def get_properties(self):
        return super().get_properties() + [
            properties.BoolProperty(
                CategoryType.GENERAL,
                self,
                'Global',
                self.Global,
                "Глобальный модуль"),
            properties.SourceCodeProperty(
                CategoryType.SOURCECODE,
                self,
                'Module',
                self.Module,
                "Модуль"
            ),
        ]





# Реквизит
class AttributeNode(Node):
    emoji = '➖'
    can_display_properties_page = False

    def __init__(
        self,
        name,
        Synonym,
        Comment,
        ParentNode,
        Type,
        PasswordMode,
    ):
        super().__init__(
            f"{ParentNode.id}.Attribute.{name}",
            name,
            Synonym,
            Comment,
            NodeType.ATTRIBUTE,
            []
        )
        self.ParentNode = ParentNode
        self.Type = Type
        self.PasswordMode = PasswordMode

    def get_properties(self):
        return super().get_properties() + [
            properties.BoolProperty(CategoryType.NO, self, "PasswordMode", self.value, "Режим пароля"),
        ]
