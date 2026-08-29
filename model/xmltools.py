from lxml import etree
import os

# Возвращает пространства имён для объекта метаданных
def get_mdo_ns():
	return {
        "md": "http://v8.1c.ru/8.3/MDClasses",
        "v8": "http://v8.1c.ru/8.1/data/core",
        "d": "http://v8.1c.ru/8.3/xcf/dumpinfo",
        "xr": "http://v8.1c.ru/8.3/xcf/readable",
    }


# Создаёт элемент MetaDataObject
def new_mdo_xml(ns):
	return etree.Element("{md}MetaDataObject", nsmap=ns)

def tostring(obj):
    return etree.tostring(obj, xml_declaration=True, encoding="UTF-8", pretty_print=True)

def new_file(dir_path, name):
    return open(os.path.join(dir_path, name+".xml"), 'wb')
