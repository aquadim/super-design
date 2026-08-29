from enum import Enum


def translate_enum(*args):
    translation = {}
    for i in range(1,len(args)):
        if i % 2 == 0:
            translation[args[i - 1]] = args[i]
    if not args[0] in translation:
        return "..."
    return translation[args[0]]


class NodeType(Enum):
    CONFIGURATION = 1
    LANGUAGE = 2
    STORAGE = 3
    CATALOG = 4
    SUBSYSTEM = 5
    COMMONMODULE = 6
    ATTRIBUTE = 7
    DOCUMENT = 8
    TABULAR_SECTION = 9

    def written(self):
        return translate_enum(
            self,
            NodeType.CONFIGURATION, "Конфигурация",
            NodeType.LANGUAGE, "Язык",
            NodeType.CATALOG, "Справочник",
            NodeType.SUBSYSTEM, "Подсистема",
            NodeType.COMMONMODULE, "Общий модуль",
            NodeType.ATTRIBUTE, "Реквизит",
            NodeType.DOCUMENT, "Документ",
            NodeType.TABULAR_SECTION, "Табличная часть",
        )


class CategoryType(Enum):
    GENERAL             = 1
    DEVELOPMENT         = 2
    LANG                = 3
    HIERARCHY           = 4
    HELP                = 5
    SOURCECODE          = 6
    SUBSYSTEMCONTENT    = 7
    ATTRIBUTES          = 8
    NO                  = 9

    def written(self):
        return translate_enum(
            self,
            CategoryType.GENERAL, "📝 Общее",
            CategoryType.DEVELOPMENT, "👨‍💻 Разработка",
            CategoryType.LANG, "💬 Язык",
            CategoryType.HIERARCHY, "📶 Иерархия",
            CategoryType.HELP, "🛟 Справочная информация",
            CategoryType.SOURCECODE, "</> Программный код",
            CategoryType.SUBSYSTEMCONTENT, "✅ Состав подсистемы",
            CategoryType.ATTRIBUTES, "➖ Реквизиты",
            CategoryType.NO, "(без категории)",
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
        elif self == CategoryType.SUBSYSTEMCONTENT:
            return 100
        elif self == CategoryType.ATTRIBUTES:
            return 350
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
    Version8_5_4 = 8*5*4
    Version8_3_25 = 8*3*25

    def written(self):
        return translate_enum(
            self,
            ConfigurationExtensionCompatibilityMode.Version8_5_4, "8.5.4",
            ConfigurationExtensionCompatibilityMode.Version8_3_25, "8.3.25",
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
