import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject
import widgets
import sys
import model

# Текст с привязкой свойств GObject
# Привязывается к GtkEntry
class BindText:
    def __init__(self, prop_name, obj, value):
        self.prop_name = prop_name
        self.obj = obj
        self.value = value
    
    def bind(self, builder, app):
        w = builder.get_object(self.prop_name)
        buf = Gtk.EntryBuffer.new(self.value, -1)
        w.set_buffer(buf)
        w.bind_property('text', self.obj, self.prop_name, GObject.BindingFlags.SYNC_CREATE)

# Локализованная строка
# Привязывается к контейнеру (GtkBox)
class Localised:
    def __init__(self, prop_name, obj, languages_store_node):
        self.prop_name = prop_name
        self.obj = obj
        self.languages_store_node = languages_store_node
        self.window = None
    
    # Функция обратного вызова для обновления значения в поле ввода
    def update_callback(self, new_value):
        print(new_value)
        setattr(self.obj, self.prop_name, new_value)

        entry_text = "; ".join(list(new_value.values()))
        self.entry.set_text(entry_text)

        if self.window != None:
            self.window.close()
        self.window = None
    
    def cancel_callback(self):
        self.window.close()
        self.window = None
    
    def bind(self, builder, app):
        def on_clicked(src):
            if self.window == None:
                self.window = widgets.get_localised_string_editor(
                    getattr(self.obj, self.prop_name, {}),
                    app.configuration.store_lang,
                    False,
                    self.update_callback,
                    self.cancel_callback
                )
            self.window.present()

        box = builder.get_object(self.prop_name)
        self.entry = box.get_first_child()
        btn = self.entry.get_next_sibling()
        
        self.update_callback(getattr(self.obj, self.prop_name, {}))
        btn.connect("clicked", on_clicked)

# Просто текст
# Привязывается к GtkEntry
class Text:
    def __init__(self, prop_name, obj, value):
        self.prop_name = prop_name
        self.obj = obj
        self.value = value
    
    def bind(self, builder, app):
        def on_focus_change(src, ex):
            setattr(self.obj, self.prop_name, src.get_buffer().get_text())
        w = builder.get_object(self.prop_name)
        buf = Gtk.EntryBuffer.new(self.value, -1)
        w.set_buffer(buf)
        w.connect("notify::has-focus", on_focus_change)

# Исходный код
# Привязывается к GtkButton
class SourceCode():
    def __init__(self, prop_name, obj, value):
        self.prop_name = prop_name
        self.obj = obj
        self.value = value

    def bind(self, builder, app):
        def on_click(src, value):
            app.open_code(value)
        w = builder.get_object(self.prop_name)
        w.connect("clicked", on_click, self.value)

# Перечисление
# Пока никуда не привязывается
class Enum:
    def __init__(self, prop_name, obj, value):
        self.prop_name = prop_name
        self.obj = obj
        self.value = value
    
    def bind(self, builder, app):
        pass

# Объект конфигурации
class Object:
    def __init__(self, prop_name, obj, value, storage_node, non_null):
        self.prop_name = prop_name
        self.obj = obj
        self.value = value
        self.storage_node = storage_node
        self.entry = None
        self.window = None
        self.non_null = non_null
    
    # Функция обратного вызова для обновления значения
    def update_callback(self, new_value):
        if new_value != None and new_value.node_type == model.NodeType.STORAGE:
            return
        setattr(self.obj, self.prop_name, new_value)
        if new_value == None:
            self.entry.set_text("<не выбрано>")
        else:
            self.entry.set_text(new_value._Name)
        if self.window != None:
            self.window.close()
        self.window = None
    
    def cancel_callback(self):
        self.window.close()
        self.window = None
    
    def bind(self, builder, app):
        def on_clicked(src):
            if self.window != None:
                self.window.activate()
            else:
                self.window = widgets.get_single_object_selector(
                    self.storage_node,
                    self.non_null,
                    self.update_callback, 
                    self.cancel_callback
                )
                self.window.present()

        box = builder.get_object(self.prop_name)
        self.entry = box.get_first_child()
        btn = self.entry.get_next_sibling()
        
        self.update_callback(self.value)
        btn.connect("clicked", on_clicked)

# Свойство реквизитов
class AttributesProperty():
    def __init__(self, category, obj, prop_name, default_value):
        super().__init__(category, obj, prop_name, default_value)

    def build_gtk_widget(self, root_node, app):
        paned = widgets.get_attributes_paned(self.value, app.id_to_binding)
        return paned


class NumProperty():
    def __init__(self, category, obj, prop_name, default_value, label, minv, maxv, step):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label
        self.minv = minv
        self.maxv = maxv if maxv is not None else sys.maxsize
        self.step = step

    def build_gtk_widget(self, root_node, app):
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)

        # Подпись свойства
        lbl = Gtk.Label(label=self.label)
        lbl.set_halign(Gtk.Align.START)

        entry = Gtk.SpinButton.new_with_range(self.minv, self.maxv, self.step)
        entry.set_value(self.value)

        box.append(lbl)
        box.append(entry)
        return box


class BoolProperty():
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node, app):
        btn = Gtk.CheckButton.new_with_label(self.label)
        btn.set_active(self.value)
        return btn

# Свойство состава подсистемы
class SubsystemContentProperty():
    def __init__(self, category, obj, prop_name, default_value):
        super().__init__(category, obj, prop_name, default_value)

    def build_gtk_widget(self, root_node, app):
        sw = widgets.get_subsystem_content_tree(
            root_node,
            self.obj,
            self.value,
            app.id_to_binding)
        return sw

class LocalisedStringProperty():
    def __init__(self, category, obj, prop_name, default_value, label, big=False):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label
        self.big = big

    def build_gtk_widget(self, root_node, app):
        # Подпись свойства
        lbl = Gtk.Label(label = self.label)
        lbl.set_halign(Gtk.Align.START)

        # Буфер текста
        if self.big:
            initial_buffer = Gtk.TextBuffer.new()
        else:
            initial_buffer = Gtk.EntryBuffer.new("",0)

        # Создание поля ввода
        if self.big:
            entry = Gtk.TextView()
        else:
            entry = Gtk.Entry()
        entry.set_hexpand(True)

        # Если в конфигурации несколько языков
        # Заблокировать поле ввода, показать просто значения
        entry.set_editable(len(root_node.store_lang.children) == 1)
        if len(root_node.store_lang.children) > 1:
            values = "; ".join(list(self.value.values()))
            initial_buffer.set_text(values, -1)
        else:
            the_only_key = next(iter(self.value))
            initial_buffer.set_text(self.value[the_only_key], -1)
        entry.set_buffer(initial_buffer)

        # При изменении количества языков необходимо заново провести логику
        # настройки поля ввода
        def on_change_langs(_storage,pos,removed,added):
            print("TODO: on change language count fix LocalisedStringProperty")
        signal_id = root_node.store_lang.children.connect("items-changed", on_change_langs)

        # Кнопка открытия окна с редактированием всех строк
        menu_button = Gtk.Button.new_with_label("...")

        # Открытие окна редактирования локализованной строки
        def clicked(btn, ex):
            win = widgets.get_localised_string_editor_window(
                self.obj,
                self.prop_name,
                self.value,
                ex.big,
                app
            )
            win.present()

        menu_button.connect('clicked', clicked, self)

        # Контейнер поле ввода + кнопка менюшки
        boxentry = Gtk.Box()
        boxentry.set_orientation(Gtk.Orientation.HORIZONTAL)
        if self.big:
            sw = Gtk.ScrolledWindow()
            sw.set_size_request(-1,128)
            sw.set_child(entry)
            boxentry.append(sw)
        else:
            boxentry.append(entry)
        boxentry.append(menu_button)

        # Упаковка
        def on_destroy(w,signal_id):
            root_node.store_lang.children.disconnect(signal_id)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.append(lbl)
        box.append(boxentry)
        box.connect("destroy", on_destroy, signal_id)

        return box
