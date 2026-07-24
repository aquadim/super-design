from enum import Enum
import properties
from gi.repository import GObject, Gio


def translate_enum(*args):
    translation = {}
    for i in range(1,len(args)):
        if i % 2 == 0:
            translation[args[i - 1]] = args[i]
    if not args[0] in translation:
        return "..."
    return translation[args[0]]


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


class NodeType(Enum):
    CONFIGURATION = 1
    LANGUAGE = 2
    STORAGE = 3
    CATALOG = 4
    SUBSYSTEM = 5
    COMMONMODULE = 6

    def written(self):
        return translate_enum(
            self,
            NodeType.CONFIGURATION, "Конфигурация",
            NodeType.LANGUAGE, "Язык",
            NodeType.CATALOG, "Справочник",
            NodeType.SUBSYSTEM, "Подсистема",
            NodeType.COMMONMODULE, "Общий модуль",
        )


class CategoryType(Enum):
    GENERAL     = 1
    DEVELOPMENT = 2
    LANG        = 3
    HIERARCHY   = 4
    HELP        = 5
    SOURCECODE  = 6

    def written(self):
        return translate_enum(
            self,
            CategoryType.GENERAL, "📝 Общее",
            CategoryType.DEVELOPMENT, "👨‍💻 Разработка",
            CategoryType.LANG, "💬 Язык",
            CategoryType.HIERARCHY, "📶 Иерархия",
            CategoryType.HELP, "🛟 Справочная информация",
            CategoryType.SOURCECODE, "</> Программный код"
        )

    # Возвращает вес категории. 0 - минимум, 10001 - максимум
    def weight(self):
        if self == CategoryType.GENERAL:
            return 0
        elif self == CategoryType.DEVELOPMENT:
            return 8000
        elif self == CategoryType.LANG:
            return 100
        elif self == CategoryType.HIERARCHY:
            return 300
        elif self == CategoryType.HELP:
            return 10000
        elif self == CategoryType.SOURCECODE:
            return 400
        return 10001


class SourceCodeType(Enum):
    OBJECT      = 1
    MANAGER     = 2
    MODULE      = 3

    def written(self):
        return translate_enum(
            self,
            SourceCodeType.OBJECT, "Модуль объекта",
            SourceCodeType.MANAGER, "Модуль менеджера",
            SourceCodeType.MODULE, "Модуль",
        )


class DefaultRunMode(Enum):
    ManagedApplication = 0
    OrdinaryApplication = 1

    def written(self):
        return translate_enum(
            self,
            DefaultRunMode.ManagedApplication, "Управляемое приложение",
            DefaultRunMode.OrdinaryApplication, "Обычное приложение"
        )


class ConfigurationExtensionCompatibilityMode(Enum):
    Version8_5_4 = 1

    def written(self):
        return translate_enum(
            self,
            ConfigurationExtensionCompatibilityMode.Version8_5_4, "8.5.4"
        )


class HierarchyType(Enum):
    HierarchyFoldersAndItems = 1
    HierarchyOfItems = 2

    def written(self):
        return translate_enum(
            self,
            HierarchyType.HierarchyFoldersAndItems, "Иерархия групп и элементов",
            HierarchyType.HierarchyOfItems, "Иерархия элементов",
        )


# Узел конфигурации
class Node(GObject.Object):
    __slots__ = ['id', 'Synonym', 'Comment', 'node_type', 'children']
    __gtype_name__ = 'DataObject'
    emoji = "👽"
    can_display_properties_page = False

    name = GObject.Property(type=str, default=None)

    def __init__(self, id, Name, Synonym, Comment, node_type, children=[]):
        super().__init__()
        self.id = id
        self.name = Name
        self.Synonym = Synonym
        self.Comment = Comment
        self.node_type = node_type
        self.children = children

    def get_properties(self):
        return [
            properties.BindTextProperty(CategoryType.GENERAL, self, 'name', self.name, "Имя"),
            properties.LocalisedStringProperty(CategoryType.GENERAL, self, 'Synonym', self.Synonym, "Синоним"),
            properties.SimpleTextProperty(CategoryType.GENERAL, self, 'Comment', self.Comment, "Комментарий"),
        ]

    def modify_page(self, page):
        pass


# Корневой узел
class RootNode(Node):
    __slots__ = [
        'ConfigurationExtensionCompatibilityMode',
        'default_run_mode',
        'Vendor',
        'Version',
        'UseManagedFormInOrdinaryApplication',
        'UseOrdinaryFormInManagedApplication',
        'UpdateCatalogAddress',
        'IncludeHelpInContents',
        'HelpHTMLContent',

        'store_lang',
        'store_catalog',
        'store_subsystem',
    ]
    emoji = "🟡"
    can_display_properties_page = True

    def __init__(
        self,
        Name,
        Synonym,
        Comment,
        IncludeHelpInContents,
        HelpHTMLContent,
        ConfigurationExtensionCompatibilityMode,
        DefaultRunMode,
        Vendor,
        Version,
        UpdateCatalogAddress,
        UseManagedFormInOrdinaryApplication,
        UseOrdinaryFormInManagedApplication):

        # Хранилища объектов
        self.store_lang = StoreNode("⋮💬", "Языки")
        self.store_catalog = StoreNode("⋮📦", "Справочники")
        self.store_subsystem = StoreNode("⋮🗂️", "Подсистемы")
        self.store_commonmodule = StoreNode("⋮📃", "Общие модули")

        super().__init__(
            "root",
            Name,
            Synonym,
            Comment,
            NodeType.CONFIGURATION,
            [
                self.store_subsystem,
                self.store_commonmodule,
                self.store_lang,
                self.store_catalog,
            ]
        )
        self.IncludeHelpInContents = IncludeHelpInContents
        self.HelpHTMLContent = HelpHTMLContent
        self.ConfigurationExtensionCompatibilityMode = ConfigurationExtensionCompatibilityMode
        self.DefaultRunMode = DefaultRunMode
        self.Vendor = Vendor
        self.Version = Version
        self.UseManagedFormInOrdinaryApplication = UseManagedFormInOrdinaryApplication
        self.UseOrdinaryFormInManagedApplication = UseOrdinaryFormInManagedApplication
        self.UpdateCatalogAddress = UpdateCatalogAddress

    def get_properties(self):
        return super().get_properties() + [
            properties.EnumProperty(CategoryType.GENERAL, self, 'DefaultRunMode', self.DefaultRunMode, "Основной режим запуска"),
            properties.SimpleTextProperty(CategoryType.DEVELOPMENT, self, 'Vendor', self.Vendor, "Поставщик"),
            properties.SimpleTextProperty(CategoryType.DEVELOPMENT, self, 'Version', self.Version, "Версия"),
            properties.SimpleTextProperty(CategoryType.DEVELOPMENT, self, 'UpdateCatalogAddress', self.UpdateCatalogAddress, "Адрес каталога обновлений"),
            properties.BoolProperty(CategoryType.GENERAL, self, 'UseManagedFormInOrdinaryApplication', self.UseManagedFormInOrdinaryApplication, "Использовать управляемые формы в обычном приложении"),
            properties.BoolProperty(CategoryType.GENERAL, self, 'UseOrdinaryFormInManagedApplication', self.UseOrdinaryFormInManagedApplication, "Использовать обычные формы в управляемом приложении"),
            properties.BoolProperty(CategoryType.HELP, self, 'IncludeHelpInContents', self.IncludeHelpInContents, "Включать в содержание справки"),
            properties.SimpleTextProperty(CategoryType.HELP, self, 'HelpHTMLContent', self.HelpHTMLContent, "Справка")
        ]


# Узел для хранения чего-либо
class StoreNode(Node):
    __slots__ = []
    emoji = "📁"
    can_display_properties_page = False

    def __init__(self, emoji, name):
        super().__init__(
            "store"+name,
            name,
            None,
            None,
            NodeType.STORAGE,
            Gio.ListStore.new(Node)
        )
        self.emoji = emoji

    def get_properties(self):
        return []


# Язык
class LanguageNode(Node):
    __slots__ = ['LanguageCode',]
    emoji = '💬'
    can_display_properties_page = True

    def __init__(self, name, Synonym, Comment, LanguageCode):
        super().__init__(
            f"lang:{LanguageCode}",
            name,
            Synonym,
            Comment,
            NodeType.LANGUAGE,
            []
        )
        self.LanguageCode = LanguageCode

    def get_properties(self):
        return super().get_properties() + [
            properties.SimpleTextProperty(CategoryType.LANG, self, 'LanguageCode', self.LanguageCode, "Код языка")
        ]

# Подсистема
class SubsystemNode(Node):
    __slots__ = [
        'IncludeInCommandInterface',
        'UseOneCommand',
        'Explanation'
    ]
    emoji = '🗂️'
    can_display_properties_page = True

    def __init__(self, name, Synonym, Comment, IncludeInCommandInterface, UseOneCommand, Explanation):
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

    def get_properties(self):
        return super().get_properties() + [
            properties.BoolProperty(CategoryType.GENERAL, self, 'IncludeInCommandInterface', self.IncludeInCommandInterface, "Включать в командный интерфейс"),
            properties.BoolProperty(CategoryType.GENERAL, self, 'UseOneCommand', self.UseOneCommand, "Подсистема с одной командой"),
            properties.LocalisedStringProperty(CategoryType.GENERAL, self, 'Explanation', self.Explanation, "Пояснение", True),
        ]


# Общий модуль
class CommonModuleNode(Node):
    __slots__ = [
        'Global',
        'ClientManagedApplication',
        'Server',
        'ExternalConnection',
        'ClientOrdinaryApplication',
        'ServerCall',
        'Privileged',
        'ReturnValuesReuse',
        'Module',
    ]
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
            f"commonmodule:{name}",
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


# Справочник
class CatalogNode(Node):
    __slots__ = [
        'Hierarchical',
        'HierarchyType',
        'LimitLevelCount',
        'LevelCount',
        'FoldersOnTop',
        'ManagerModule',
        'ObjectModule',
    ]
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
    ):
        super().__init__(
            f"catalog:{name}",
            name,
            Synonym,
            Comment,
            NodeType.CATALOG,
            []
        )
        self.Hierarchical = Hierarchical
        self.HierarchyType = HierarchyType
        self.LimitLevelCount = LimitLevelCount
        self.LevelCount = LevelCount
        self.FoldersOnTop = FoldersOnTop

    def get_properties(self):
        return super().get_properties() + [
            properties.BoolProperty(CategoryType.HIERARCHY, self, 'Hierarchical', self.Hierarchical, "Иерархический справочник"),
            properties.EnumProperty(CategoryType.HIERARCHY, self, 'HierarchyType', self.HierarchyType, "Вид иерархии"),
            properties.BoolProperty(CategoryType.HIERARCHY, self, 'FoldersOnTop', self.FoldersOnTop, "Помещать группы сверху"),
            properties.BoolProperty(CategoryType.HIERARCHY, self, 'LimitLevelCount', self.LimitLevelCount, "Ограничить количество уровней иерархии"),
            properties.NumProperty(CategoryType.HIERARCHY, self, 'LevelCount', self.LevelCount, "Количество уровней иерархии",1,None,1),
            properties.SourceCodeProperty(CategoryType.SOURCECODE, self, 'ManagerModule', self.ManagerModule, "Модуль менеджера"),
            properties.SourceCodeProperty(CategoryType.SOURCECODE, self, 'ObjectModule', self.ObjectModule, "Модуль объекта"),
        ]


def get_transform_func(node):
    def func(binding, value):
        return f'{node.emoji} {node.node_type.written()} "{value}"'
    return func
