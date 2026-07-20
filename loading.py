# Модуль загрузки модели конфигурации из XML файлов
from lxml import etree as ET
import model
import os
import observable


def get_dumped_objects(objects_xml, kind, ns):
    return objects_xml.xpath(f"/d:ConfigDumpInfo/d:ConfigVersions/d:Metadata[starts-with(@name,'{kind}')]", namespaces=ns)


# Получает строку из свойств
def parse_string(props_obj, tag_name, ns):
    return props_obj.find("md:"+tag_name, ns).text


# Получает число из свойств
def parse_int(props_obj, tag_name, ns):
    return int(props_obj.find("md:"+tag_name, ns).text)


# Получает булевое значение из свойств
def parse_bool(props_obj, tag_name, ns):
    return props_obj.find(f"md:{tag_name}", ns).text == "true"


# Получает локализованную строку из свойств
def parse_localized_string(props_obj, tag_name, ns):
    items = props_obj.find(f"md:{tag_name}", ns).findall("v8:item", ns)
    d = {}
    for i in items:
        language_code = i.find("v8:lang", ns)
        content = i.find("v8:content", ns)
        d[language_code.text] = content.text
    return d


def parse_enum(props_obj, tag_name, ns, enum_class):
    value = props_obj.find(f"md:{tag_name}", ns).text
    return enum_class.__members__[value]


# Загрузка языков
def collect_objects(p, collection_name, mdo_name, items, parse_func, ns):
    obj_dir = os.path.join(p, collection_name)
    collection = []
    for item in items:
        obj_path    = os.path.join(obj_dir, item.get('name').split('.')[1] + ".xml")
        mdo         = ET.parse(obj_path).getroot()
        obj         = mdo.find(f"md:{mdo_name}", ns)
        props       = obj.find("md:Properties", ns)
        collection.append(parse_func(props, ns))
    return collection


def parse_func_Language(props, ns):
    return model.LanguageNode(
        parse_string(props, "Name", ns),
        parse_localized_string(props, "Synonym", ns),
        parse_string(props, "Comment", ns),
        parse_string(props, "LanguageCode", ns),
    )


def parse_func_Catalog(props, ns):
    return model.CatalogNode(
        parse_string(props, "Name", ns),
        parse_localized_string(props, "Synonym", ns),
        parse_string(props, "Comment", ns),
        parse_bool(props, "Hierarchical", ns),
        parse_enum(props, "HierarchyType", ns, model.HierarchyType),
        parse_bool(props, "LimitLevelCount", ns),
        parse_int(props, "LevelCount", ns),
        parse_bool(props, "FoldersOnTop", ns),
    )


def xml_to_model(p):
    ns = {
        "md": "http://v8.1c.ru/8.3/MDClasses",
        "v8": "http://v8.1c.ru/8.1/data/core",
        "d": "http://v8.1c.ru/8.3/xcf/dumpinfo",
    }

    # Загрузка узла конфигурации
    tree = ET.parse(os.path.join(p, "Configuration.xml"))
    mdo = tree.getroot()
    conf = mdo.find("md:Configuration", ns)
    props = conf.find("md:Properties", ns)

    configuration = model.RootNode(
        parse_string(props, "Name", ns),
        parse_localized_string(props, "Synonym", ns),
        parse_string(props, "Comment", ns),
        parse_bool(props, "IncludeHelpInContents", ns),
        "TODO!!!",
        parse_enum(props, "ConfigurationExtensionCompatibilityMode", ns, model.ConfigurationExtensionCompatibilityMode),
        parse_enum(props, "DefaultRunMode", ns, model.DefaultRunMode),
        parse_string(props, "Vendor", ns),
        parse_string(props, "Version", ns),
        parse_string(props, "UpdateCatalogAddress", ns),
        parse_bool(props, "UseManagedFormInOrdinaryApplication", ns),
        parse_bool(props, "UseOrdinaryFormInManagedApplication", ns),
    )

    objects_xml = ET.parse(os.path.join(p, "ConfigDumpInfo.xml")).getroot()

    # Загрузка языков
    languages_xml = get_dumped_objects(objects_xml, "Language", ns)
    languages = collect_objects(p, "Languages", "Language", languages_xml, parse_func_Language, ns)
    configuration.store_lang.children = observable.ObservableList(languages)

    # Загрузка справочников
    catalogs_xml = get_dumped_objects(objects_xml, "Catalog", ns)
    catalogs = collect_objects(p, "Catalogs", "Catalog", catalogs_xml, parse_func_Catalog, ns)
    configuration.store_catalog.children = observable.ObservableList(catalogs)

    return configuration
