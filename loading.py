# Модуль загрузки модели конфигурации из XML файлов
from lxml import etree as ET
import model
import os
from pathlib import Path


# Возвращает все объекты указанного класса из Configuration.xml
def get_dumped_objects(root_children, kind, ns):
    return root_children.findall(f"md:{kind}", ns)


# Возвращает папку объекта
# Для /Subsystems/УИ_УниверсальныеИнструменты.xml и dir_name = Subsystems
# Вывод /Subsystems/УИ_УниверсальныеИнструменты/Subsystems/
def get_object_any_dir(obj_path, dir_name):
    obj_dir = os.path.dirname(obj_path)
    obj_name = obj_path.stem
    return os.path.join(obj_dir, obj_name, dir_name)


# Возвращает Ext папку объекта
# Для /Subsystems/УИ_УниверсальныеИнструменты.xml
# Вывод /Subsystems/УИ_УниверсальныеИнструменты/Ext/
def get_object_ext_dir(obj_path):
    return get_object_any_dir(obj_path, "Ext")


# Возвращает путь к модулю
# Для /Catalogs/УИ_Алгоритмы.xml
# Вывод /Catalogs/УИ_Алгоритмы.xml/Ext/Module.bsl
def get_module_path(obj_path, module_name="Module.bsl"):
    return os.path.join(get_object_ext_dir(obj_path), module_name)


# Возвращает путь к модулю объекта
# Для /Catalogs/УИ_Алгоритмы.xml
# Вывод /Catalogs/УИ_Алгоритмы.xml/Ext/ObjectModule.bsl
def get_object_module_path(obj_path):
    return os.path.join(get_object_ext_dir(obj_path), "ObjectModule.bsl")


# Возвращает путь к модулю менеджера объекта
# Для /Catalogs/УИ_Алгоритмы.xml
# Вывод /Catalogs/УИ_Алгоритмы.xml/Ext/ManagerModule.bsl
def get_manager_module_path(obj_path):
    return os.path.join(get_object_ext_dir(obj_path), "ManagerModule.bsl")


# Возвращает значение строкового свойства
def parse_string(props_obj, tag_name, ns):
    return props_obj.find("md:"+tag_name, ns).text


# Возвращает значение численного свойства
def parse_int(props_obj, tag_name, ns):
    return int(props_obj.find("md:"+tag_name, ns).text)


# Возвращает значение булевого свойства
def parse_bool(props_obj, tag_name, ns):
    return props_obj.find(f"md:{tag_name}", ns).text == "true"


# Возвращает значение локализованной строки
def parse_localized_string(language_collection, props_obj, tag_name, ns):
    items = props_obj.find(f"md:{tag_name}", ns).findall("v8:item", ns)
    d = {}
    parsed = {}
    for i in items:
        language_code = i.find("v8:lang", ns).text
        content = i.find("v8:content", ns).text
        parsed[language_code] = content

    for lang_ptr in language_collection:
        if lang_ptr.LanguageCode in parsed:
            d[lang_ptr] = parsed[lang_ptr.LanguageCode]

    return d


# Возвращает значение перечисления свойства
def parse_enum(props_obj, tag_name, ns, enum_class):
    value = props_obj.find(f"md:{tag_name}", ns).text
    return enum_class.__members__[value]

def parse_object(props_obj, tag_name, ns, storage_node):
    value = props_obj.find(f"md:{tag_name}", ns).text
    _, name = value.split(".")
    return storage_node.name_to_node[name]

# Загрузка реквизитов объекта
def collect_attributes(configuration, obj, parent_node, ns):
    child_objects = obj.find("md:ChildObjects", ns)
    attributes = child_objects.findall("md:Attribute", ns)
    output = []
    for a in attributes:
        props = a.find("md:Properties", ns)

        attribute = model.AttributeNode(
            parse_string(props, "Name", ns),
            parse_localized_string(configuration.store_lang.children, props, "Synonym", ns),
            parse_string(props, "Comment", ns),
            parent_node,
            None,
            parse_bool(props, "PasswordMode", ns),
        )
        output.append(attribute)
    return output


# Загрузка объектов конфигурации
def collect_objects(p, configuration, collection_name, mdo_name, items, parse_func, ns):
    obj_dir = os.path.join(p, collection_name)
    collection = []
    for item in items:
        obj_path    = Path(os.path.join(obj_dir, item.text + ".xml"))
        mdo         = ET.parse(obj_path).getroot()
        obj         = mdo.find(f"md:{mdo_name}", ns)
        props       = obj.find("md:Properties", ns)
        collection.append(parse_func(configuration, obj_path, obj, props, ns))
    return collection


# Загрузка языков
def collect_languages(p, items, ns):
    obj_dir = os.path.join(p, "Languages")
    collection = []
    props_objs = []

    for item in items:
        obj_path    = Path(os.path.join(obj_dir, item.text + ".xml"))
        mdo         = ET.parse(obj_path).getroot()
        obj         = mdo.find("md:Language", ns)
        props       = obj.find("md:Properties", ns)

        lang = model.LanguageNode(
            parse_string(props, "Name", ns),
            None,
            parse_string(props, "Comment", ns),
            parse_string(props, "LanguageCode", ns),
        )

        collection.append(lang)
        props_objs.append(props)

    for idx, item in enumerate(collection):
        # Загрузить синонимы для всех языков
        props = props_objs[idx]
        item.Synonym = parse_localized_string(collection, props, "Synonym", ns)

    return collection


# XML -> Подсистема
def parse_func_Subsystem(configuration, obj_path, obj, props, ns):
    subsystem = model.SubsystemNode(
        parse_string(props, "Name", ns),
        parse_localized_string(configuration.store_lang.children, props, "Synonym", ns),
        parse_string(props, "Comment", ns),
        parse_bool(props, "IncludeInCommandInterface", ns),
        parse_bool(props, "UseOneCommand", ns),
        parse_localized_string(configuration.store_lang.children, props, "Explanation", ns),
    )

    # Состав подсистемы
    content_xml = props.find("md:Content", ns)
    items = content_xml.findall("xr:Item", ns)
    for item in items:
        item_id = item.text
        id_parts = item_id.split(".")

        store_node = None
        if id_parts[0] == "Catalog":
            store_node = configuration.store_catalog
        elif id_parts[0] == "CommonModule":
            store_node = configuration.store_commonmodule
        else:
            # Неизвестный вид объекта
            # TODO log
            continue
        node = store_node.id_to_node[item_id]
        subsystem.Content.append(node)

    # Поиск подчиненных подсистем
    children_xml = obj.find("md:ChildObjects", ns)
    if len(children_xml) > 0:
        children = collect_objects(
            os.path.dirname(get_object_ext_dir(obj_path)),
            configuration,
            "Subsystems",
            "Subsystem",
            children_xml,
            parse_func_Subsystem,
            ns
        )
        for c in children:
            subsystem.children.append(c)


    return subsystem


# XML -> Справочник
def parse_func_Catalog(configuration, obj_path, obj, props, ns):
    node = model.CatalogNode(
        parse_string(props, "Name", ns),
        parse_localized_string(configuration.store_lang.children, props, "Synonym", ns),
        parse_string(props, "Comment", ns),
        parse_bool(props, "Hierarchical", ns),
        parse_enum(props, "HierarchyType", ns, model.enums.HierarchyType),
        parse_bool(props, "LimitLevelCount", ns),
        parse_int(props, "LevelCount", ns),
        parse_bool(props, "FoldersOnTop", ns),
        parse_localized_string(configuration.store_lang.children, props, "ObjectPresentation", ns),
        parse_localized_string(configuration.store_lang.children, props, "ExtendedObjectPresentation", ns),
        parse_localized_string(configuration.store_lang.children, props, "ListPresentation", ns),
        parse_localized_string(configuration.store_lang.children, props, "ExtendedListPresentation", ns),
        parse_localized_string(configuration.store_lang.children, props, "Explanation", ns),
    )
    attributes = collect_attributes(configuration, obj, node, ns)
    if len(attributes) != 0:
        node.store_attribute.add_bulk(attributes)

    node.ObjectModule = model.LazySourceCode(get_object_module_path(obj_path), node, model.enums.SourceCodeType.OBJECT)
    node.ManagerModule = model.LazySourceCode(get_manager_module_path(obj_path), node, model.enums.SourceCodeType.MANAGER)

    return node


# XML -> Общий модуль
def parse_func_CommonModule(configuration, obj_path, obj, props, ns):
    node = model.CommonModuleNode(
        parse_string(props, "Name", ns),
        parse_localized_string(configuration.store_lang.children, props, "Synonym", ns),
        parse_string(props, "Comment", ns),
        parse_bool(props, "Global", ns),
        parse_bool(props, "ClientManagedApplication", ns),
        parse_bool(props, "Server", ns),
        parse_bool(props, "ExternalConnection", ns),
        parse_bool(props, "ClientOrdinaryApplication", ns),
        parse_bool(props, "ServerCall", ns),
        parse_bool(props, "Privileged", ns),
        None
    )

    node.Module = model.LazySourceCode(get_module_path(obj_path), node, model.enums.SourceCodeType.MODULE)

    return node


# Строит модель конфигурации по выгрузке из XML файлов
def xml_to_model(p):
    type_storage = model.TypeStorage()

    ns = {
        "md": "http://v8.1c.ru/8.3/MDClasses",
        "v8": "http://v8.1c.ru/8.1/data/core",
        "d": "http://v8.1c.ru/8.3/xcf/dumpinfo",
        "xr": "http://v8.1c.ru/8.3/xcf/readable",
    }

    # Загрузка узла конфигурации
    tree = ET.parse(os.path.join(p, "Configuration.xml"))
    mdo = tree.getroot()
    conf = mdo.find("md:Configuration", ns)
    props = conf.find("md:Properties", ns)
    root_children = conf.find("md:ChildObjects", ns)

    # Загрузка языков
    languages_xml = get_dumped_objects(root_children, "Language", ns)
    languages = collect_languages(p, languages_xml, ns)

    configuration = model.RootNode(
        parse_string(props, "Name", ns),
        parse_localized_string(languages, props, "Synonym", ns),
        parse_string(props, "Comment", ns),
        parse_bool(props, "IncludeHelpInContents", ns),
        "TODO!!!",
        parse_enum(props, "ConfigurationExtensionCompatibilityMode", ns, model.enums.ConfigurationExtensionCompatibilityMode),
        parse_enum(props, "DefaultRunMode", ns, model.enums.DefaultRunMode),
        parse_string(props, "Vendor", ns),
        parse_string(props, "Version", ns),
        parse_string(props, "UpdateCatalogAddress", ns),
        parse_bool(props, "UseManagedFormInOrdinaryApplication", ns),
        parse_bool(props, "UseOrdinaryFormInManagedApplication", ns),
        parse_enum(props, "ScriptVariant", ns, model.enums.ScriptVariant),
    )
    configuration.ManagedApplicationModule = model.LazySourceCode(
        get_module_path(p, "ManagedApplicationModule.bsl"),
        configuration, 
        model.enums.SourceCodeType.MANAGED_APPLICATION_MODULE)
    configuration.SessionModule = model.LazySourceCode(
        get_module_path(p, "SessionModule.bsl"),
        configuration, 
        model.enums.SourceCodeType.SESSION_MODULE)
    configuration.ExternalConnectionModule = model.LazySourceCode(
        get_module_path(p, "ExternalConnectionModule.bsl"),
        configuration, 
        model.enums.SourceCodeType.EXTERNAL_CONNECTION_MODULE)

    for obj in languages:
        configuration.store_lang.append(obj)

    # Язык по умолчанию
    configuration.DefaultLanguage = parse_object(props, "DefaultLanguage", ns, configuration.store_lang)

    # Загрузка справочников
    catalogs_xml = get_dumped_objects(root_children, "Catalog", ns)
    catalogs = collect_objects(
        p,
        configuration,
        "Catalogs",
        "Catalog",
        catalogs_xml,
        parse_func_Catalog,
        ns
    )
    for obj in catalogs:
        configuration.store_catalog.append(obj)

    # Загрузка общих модулей
    common_modules_xml = get_dumped_objects(root_children, "CommonModule", ns)
    common_modules = collect_objects(
        p,
        configuration,
        "CommonModules",
        "CommonModule",
        common_modules_xml,
        parse_func_CommonModule,
        ns
    )
    for obj in common_modules:
        configuration.store_commonmodule.append(obj)

    # Загрузка подсистем
    subsystems_xml = get_dumped_objects(root_children, "Subsystem", ns)
    subsystems = collect_objects(
        p,
        configuration,
        "Subsystems",
        "Subsystem",
        subsystems_xml,
        parse_func_Subsystem,
        ns
    )
    for obj in subsystems:
        configuration.store_subsystem.children.append(obj)

    return configuration
