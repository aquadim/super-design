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

class SourceCodeType(Enum):
    OBJECT = 0
    MANAGER = 1
    MODULE = 2
    MANAGED_APPLICATION_MODULE = 3
    SESSION_MODULE = 4
    EXTERNAL_CONNECTION_MODULE = 5

    def written(self):
        return translate_enum(
            self,
            SourceCodeType.OBJECT, "Модуль объекта",
            SourceCodeType.MANAGER, "Модуль менеджера",
            SourceCodeType.MODULE, "Модуль",
            SourceCodeType.MANAGED_APPLICATION_MODULE, "Модуль приложения",
            SourceCodeType.SESSION_MODULE, "Модуль сеанса приложения",
            SourceCodeType.EXTERNAL_CONNECTION_MODULE, "Модуль внешнего соединения",
        )
    
    def help_info(self):
        return translate_enum(
            self,
            SourceCodeType.OBJECT, "Поведение отдельного экземпляра",
            SourceCodeType.MANAGER, "Статическая функциональность",
            SourceCodeType.MODULE, "Программный код",
            SourceCodeType.MANAGED_APPLICATION_MODULE, "Код вызывается при старте системы",
            SourceCodeType.SESSION_MODULE, "Установка параметров сеанса",
            SourceCodeType.EXTERNAL_CONNECTION_MODULE, "Используется при работе через COM-соединение",
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
    Version8_5_4 = 0
    Version8_3_25 = 1
    Version8_3_27 = 2

    def written(self):
        return translate_enum(
            self,
            ConfigurationExtensionCompatibilityMode.Version8_5_4, "8.5.4",
            ConfigurationExtensionCompatibilityMode.Version8_3_25, "8.3.25",
            ConfigurationExtensionCompatibilityMode.Version8_3_27, "8.3.27",
        )


class HierarchyType(Enum):
    HierarchyFoldersAndItems = 0
    HierarchyOfItems = 1

    def written(self):
        return translate_enum(
            self,
            HierarchyType.HierarchyFoldersAndItems, "Иерархия групп и элементов",
            HierarchyType.HierarchyOfItems, "Иерархия элементов",
        )

class ScriptVariant(Enum):
    Russian = 0
    English = 1

    def written(self):
        return translate_enum(
            self,
            ScriptVariant.Russian, "Русский",
            ScriptVariant.English, "Английский",
        )

class UsePurpose(Enum):
    PlatformApplication = 0
    MobilePlatformApplication = 1

    def written(self):
        return translate_enum(
            self,
            UsePurpose.PlatformApplication, "Приложение для платформы",
            UsePurpose.MobilePlatformApplication, "Приложение для мобильной платформы",
        )