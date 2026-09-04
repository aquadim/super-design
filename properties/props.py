import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject, Gio
import widgets
import model
from widgets.Helpers import get_name_factory, create_gio_tree_model

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
    def __init__(self, prop_name, obj, languages_store_node, is_big=False):
        self.prop_name = prop_name
        self.obj = obj
        self.languages_store_node = languages_store_node
        self.window = None
        self.is_big = is_big
    
    # Функция обратного вызова для обновления значения в поле ввода
    def update_callback(self, new_value):
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
                    self.is_big,
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
    
    def on_selected(self, src, _):
        selected_pos = src.get_selected()
        enum_type = type(getattr(self.obj, self.prop_name))
        setattr(self.obj, self.prop_name, list(enum_type)[selected_pos])
    
    def bind(self, builder, app):
        w = builder.get_object(self.prop_name)

        # Установка изначального значения
        member = getattr(self.obj, self.prop_name)
        w.set_selected(member.value)

        w.connect("notify::selected", self.on_selected)

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
    
    def on_clicked(self, src):
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
    
    def bind(self, builder, app):
        box = builder.get_object(self.prop_name)
        self.entry = box.get_first_child()
        btn = self.entry.get_next_sibling()
        
        self.update_callback(self.value)
        btn.connect("clicked", self.on_clicked)

class ObjectsList:
    def __init__(self, prop_name, obj, value, storage_node, non_null):
        self.prop_name = prop_name
        self.obj = obj
        self.storage_node = storage_node
        self.column_view = None
        self.window = None
        self.non_null = non_null
        
        self.stored_items = Gio.ListStore.new(model.Node)
        for item in value:
            self.stored_items.append(item)
    
    def update_callback(self, new_value):
        setattr(self.obj, self.prop_name, new_value)
        self.stored_items.remove_all()
        for item in new_value:
            self.stored_items.append(item)
    
    def cancel_callback(self):
        self.window.close()
        self.window = None

    def on_clicked(self, src):
        if self.window == None:
            self.window = widgets.get_multiple_object_selector(
                self.storage_node,
                self.non_null,
                self.update_callback, 
                self.cancel_callback
            )
        self.window.present()
    
    def bind(self, builder, app):
        # Получение виджетов
        box = builder.get_object(self.prop_name)
        sw = box.get_first_child()
        self.column_view = sw.get_first_child()
        btn = sw.get_next_sibling()
        
        # Создание колонки "Имя"
        col_name = Gtk.ColumnViewColumn(title="Имя", factory=get_name_factory(False))
        col_name.set_expand(True)
        self.column_view.append_column(col_name)

        # Данные
        tree_model = Gtk.TreeListModel.new(
            root = self.stored_items,
            passthrough = False,
            autoexpand = True,
            create_func = create_gio_tree_model,
            user_data = None
        )
        selection = Gtk.SingleSelection(model=tree_model)
        self.column_view.set_model(selection)

        btn.connect("clicked", self.on_clicked)

# Булево
# Привязывается к GtkCheckBox
class Bool:
    def __init__(self, prop_name, obj, value):
        self.prop_name = prop_name
        self.obj = obj
        self.value = value
    
    def bind(self, builder, app):
        def on_activate(src, ex):
            setattr(self.obj, self.prop_name, src.get_active())
        w = builder.get_object(self.prop_name)
        w.set_active(self.value)
        w.connect("activate", on_activate)

# Число
# Привязывается к GtkSpinButton
class Num:
    def __init__(self, prop_name, obj, value):
        self.prop_name = prop_name
        self.obj = obj
        self.value = value
    
    def bind(self, builder, app):
        def on_activate(src):
            setattr(self.obj, self.prop_name, src.get_value())
        w = builder.get_object(self.prop_name)
        w.set_value(self.value)
        w.connect("value-changed", on_activate)

# Свойство реквизитов
class AttributesProperty():
    def __init__(self, category, obj, prop_name, default_value):
        super().__init__(category, obj, prop_name, default_value)

    def build_gtk_widget(self, root_node, app):
        paned = widgets.get_attributes_paned(self.value, app.id_to_binding)
        return paned

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