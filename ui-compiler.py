import os
from lxml import etree
from pydoc import locate
import model

def add_property(obj, name, value):
    etree.SubElement(obj, "property", attrib={"name": name}).text = value

def heading_label(text, object):
    child_label = etree.SubElement(object, "child")
    object_label = etree.SubElement(child_label, "object", attrib={"class": "GtkLabel"})
    etree.SubElement(object_label, "property", attrib={"name": "label"}).text = text
    etree.SubElement(object_label, "property", attrib={"name": "halign"}).text = "start"

def tab(label):
    child = etree.Element("child", attrib={"type": "tab"})
    object = etree.SubElement(child, "object", attrib={"class": "GtkLabel"})
    etree.SubElement(object, "property", attrib={"name": "label"}).text = label

    return child

def text_slot(label, bind):
    child = etree.Element("child")
    object = etree.SubElement(child, "object", attrib={"class": "GtkBox"})
    etree.SubElement(object, "property", attrib={"name": "orientation"}).text = "vertical"

    heading_label(label, object)

    entry_c = etree.SubElement(object, "child")
    etree.SubElement(entry_c, "object", attrib={"class": "GtkEntry", "id": bind})

    return child

def entry_and_dots(label, bind, entry_is_always_inactive):
    child = etree.Element("child")
    object = etree.SubElement(child, "object", attrib={"class": "GtkBox"})
    etree.SubElement(object, "property", attrib={"name": "orientation"}).text = "vertical"

    heading_label(label, object)

    # Коробка с вводом и кнопкой
    box_c = etree.SubElement(object, "child")
    box_o = etree.SubElement(box_c, "object", attrib={"class": "GtkBox", "id": bind})
    etree.SubElement(box_o, "property", attrib={"name": "orientation"}).text = "horizontal"

    # Поле ввода
    entry_c = etree.SubElement(box_o, "child")
    entry_o = etree.SubElement(entry_c, "object", attrib={"class": "GtkEntry"})
    add_property(entry_o, "hexpand", "true")
    if entry_is_always_inactive:
        add_property(entry_o, "can-focus", "false")

    # Кнопка "..."
    btn_c = etree.SubElement(box_o, "child")
    btn_o = etree.SubElement(btn_c, "object", attrib={"class": "GtkButton"})
    etree.SubElement(btn_o, "property", attrib={"name": "label"}).text = "..."

    return child

def code(src, bind, column, row):
    btn_c = etree.Element("child")
    btn_o = etree.SubElement(btn_c, "object", attrib={"class": "GtkButton", "id": bind})

    # Положение в сетке
    layout = etree.SubElement(btn_o, "layout")
    add_property(layout, "column", column)
    add_property(layout, "row", row)

    btn_box_c = etree.SubElement(btn_o, "child")
    btn_box_o = etree.SubElement(btn_box_c, "object", attrib={"class": "GtkBox"})
    add_property(btn_box_o, "orientation", "vertical")
    
    enum_member = model.enums.SourceCodeType[src]

    # Подпись кнопки
    lbl_c = etree.SubElement(btn_box_o, "child")
    lbl_o = etree.SubElement(lbl_c, "object", attrib={"class": "GtkLabel"})
    add_property(lbl_o, "label", enum_member.written())
    add_property(lbl_o, "wrap", "true")
    add_property(lbl_o, "justify", "center")

    # Помощь кнопки
    lbl_c = etree.SubElement(btn_box_o, "child")
    lbl_o = etree.SubElement(lbl_c, "object", attrib={"class": "GtkLabel"})
    add_property(lbl_o, "label", enum_member.help_info())
    add_property(lbl_o, "wrap", "true")
    add_property(lbl_o, "justify", "center")
    
    return btn_c
    
def enum(label, src, bind):
    box_c = etree.Element("child")
    box_o = etree.SubElement(box_c, "object", attrib={"class": "GtkBox"})
    add_property(box_o, "orientation", "vertical")
    
    # Подпись
    lbl_c = etree.SubElement(box_o, "child")
    lbl_o = etree.SubElement(lbl_c, "object", attrib={"class": "GtkLabel"})
    add_property(lbl_o, "label", label)
    add_property(lbl_o, "halign", "start")

    # Выпадающий список
    drp_c = etree.SubElement(box_o, "child")
    drp_o = etree.SubElement(drp_c, "object", attrib={"class": "GtkDropDown", "id": bind})
    model_p = etree.SubElement(drp_o, "property", attrib={"name": "model"})
    
    stringlist = etree.SubElement(model_p, "object", attrib={"class": "GtkStringList"})
    items_o = etree.SubElement(stringlist, "items")
    
    enum_type = locate("model.enums." + src)
    enum_items = list(enum_type)
    for item in enum_items:
        etree.SubElement(items_o, "item", attrib={"translatable": "yes"}).text = item.written()
    
    return box_c

def boolean(label, bind):
    child = etree.Element("child")
    object = etree.SubElement(child, "object", attrib={"class": "GtkCheckButton", "id": bind})
    etree.SubElement(object, "property", attrib={"name": "label"}).text = label

    return child

def spin_button(label, bind, min_value, max_value, step):
    child = etree.Element("child")
    object = etree.SubElement(child, "object", attrib={"class": "GtkBox"})
    etree.SubElement(object, "property", attrib={"name": "orientation"}).text = "vertical"

    heading_label(label, object)

    entry_c = etree.SubElement(object, "child")
    entry_o = etree.SubElement(entry_c, "object", attrib={"class": "GtkSpinButton", "id": bind})
    adjustment_p = etree.SubElement(entry_o, "property", attrib={"name": "adjustment"})
    adjustment_o = etree.SubElement(adjustment_p, "object", attrib={"class": "GtkAdjustment"})

    if min_value != None:
        etree.SubElement(adjustment_o, "property", attrib={"name": "lower"}).text = min_value
    if max_value != None:
        etree.SubElement(adjustment_o, "property", attrib={"name": "upper"}).text = max_value
    if step == None:
        step = "1.0"
    etree.SubElement(adjustment_o, "property", attrib={"name": "step-increment"}).text = step

    return child

def main():
    files = os.listdir("./ui/properties/")
    for f in files:
        if f.find(".compiled.ui") > -1:
            continue

        compiled_fname = "./ui/properties/"+f.replace(".ui", ".compiled.ui")
        et = etree.parse("./ui/properties/"+f)
        slots = et.findall(".//slot")

        for s in slots:
            slot_type = s.get("type")
            parent = s.getparent()

            if slot_type == "text":
                # Текстовое поле
                to_replace = text_slot(s.get("label"), s.get("bind"))
            
            elif slot_type == "tab":
                # Вкладка
                to_replace = tab(s.get("label"))

            elif slot_type == "localised":
                # Локализованная строка
                to_replace = entry_and_dots(s.get("label"), s.get("bind"), False)

            elif slot_type == "code":
                # Код
                to_replace = code(s.get("src"), s.get("bind"), s.get("col"), s.get("row"))

            elif slot_type == "enum":
                # Перечисление
                to_replace = enum(s.get("label"), s.get("src"), s.get("bind"))
            
            elif slot_type == "object":
                # Объект конфигурации
                to_replace = entry_and_dots(s.get("label"), s.get("bind"), True)

            elif slot_type == "bool":
                # Булево
                to_replace = boolean(s.get("label"), s.get("bind"))
            
            elif slot_type == "num":
                # Число
                to_replace = spin_button(
                    s.get("label"),
                    s.get("bind"),
                    s.get("min"),
                    s.get("max"),
                    s.get("step"),
                )
            
            parent.replace(s, to_replace)

        
        with open(compiled_fname, "wb") as f:
            f.write(etree.tostring(
                et, 
                encoding='utf-8',
                pretty_print=True,
                xml_declaration=True
            ))


if __name__=="__main__":
    main()