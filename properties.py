import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject
import widgets
import sys


class Property:
    def __init__(self, category, obj, prop_name, default_value):
        self.category = category
        self.obj = obj
        self.prop_name = prop_name
        self.value = default_value

    def build_gtk_widget(self, root_node, app):
        raise RuntimeError("Виджет не установлен для свойства")


class BindTextProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node, app):
        # Подпись свойства
        lbl = Gtk.Label(label=self.label)
        lbl.set_halign(Gtk.Align.START)

        # Связка с данными
        default_buffer = Gtk.EntryBuffer.new(self.value, -1)
        entry = Gtk.Entry.new_with_buffer(default_buffer)
        binding = entry.bind_property(
            'text',
            self.obj,
            self.prop_name,
            GObject.BindingFlags.BIDIRECTIONAL
        )

        # При удалении поля ввода отключить привязку
        entry.connect("destroy", lambda *_a: binding.unbind())

        # Контейнер
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.append(lbl)
        box.append(entry)
        return box


class SimpleTextProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node, app):
        # Подпись свойства
        lbl = Gtk.Label(label=self.label)
        lbl.set_halign(Gtk.Align.START)

        # Связка с данными
        def on_focus_change(src,ex):
            setattr(self.obj, self.prop_name, src.get_buffer().get_text())

        default_buffer = Gtk.EntryBuffer.new(self.value, -1)
        entry = Gtk.Entry.new_with_buffer(default_buffer)
        entry.connect("notify::has-focus", on_focus_change)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.append(lbl)
        box.append(entry)
        return box


class NumProperty(Property):
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


class BoolProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node, app):
        btn = Gtk.CheckButton.new_with_label(self.label)
        btn.set_active(self.value)
        return btn


class SourceCodeProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node, app):
        btn = Gtk.Button.new_with_label(self.label)
        btn.set_halign(Gtk.Align.START)

        def on_click(src, value):
            app.open_code(self.value)

        btn.connect("clicked", on_click, self.value)
        return btn


class EnumProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node, app):
        enum_type = type(getattr(self.obj, self.prop_name))
        dropdown = widgets.get_dropdown_from_enum(enum_type, self.value)

        lbl = Gtk.Label(label=self.label)
        lbl.set_halign(Gtk.Align.START)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.append(lbl)
        box.append(dropdown)
        return box


# Свойство состава подсистемы
class SubsystemContentProperty(Property):
    def __init__(self, category, obj, prop_name, default_value):
        super().__init__(category, obj, prop_name, default_value)

    def build_gtk_widget(self, root_node, app):
        sw = widgets.get_subsystem_content_tree(
            root_node,
            self.obj,
            self.value,
            app.id_to_binding)
        return sw


class LocalisedStringProperty(Property):
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
            win = Gtk.Window()
            win.set_title("Редактирование локализованной строки")
            win.set_destroy_with_parent(True)
            win.set_modal(True)
            win.set_default_size(512,256)

            sw = Gtk.ScrolledWindow()
            page = Gtk.Box()
            page.set_orientation(Gtk.Orientation.VERTICAL)
            page.set_margin_start(16)
            page.set_margin_end(16)
            page.set_margin_top(16)
            page.set_margin_bottom(16)
            page.set_spacing(16)

            for language in root_node.store_lang.children:
                lang_box = Gtk.Box()
                lang_box.set_orientation(Gtk.Orientation.VERTICAL)

                lang_label = Gtk.Label(label=language.name)
                lang_label.set_halign(Gtk.Align.START)

                if self.big:
                    buf = Gtk.TextBuffer.new()
                    buf.set_text(self.value[language.LanguageCode],-1)
                    lang_entry = Gtk.TextView.new_with_buffer(buf)
                else:
                    lang_entry = Gtk.Entry.new_with_buffer(Gtk.EntryBuffer.new(
                        self.value[language.LanguageCode],
                        -1
                    ))

                lang_box.append(lang_label)
                lang_box.append(lang_entry)
                page.append(lang_box)

            sw.set_child(page)
            win.set_child(sw)
            win.present()
        menu_button.connect('clicked', clicked, self.obj)

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
            print("on destoy: disconnect")
            root_node.store_lang.children.disconnect(signal_id)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.append(lbl)
        box.append(boxentry)
        box.connect("destroy", on_destroy, signal_id)

        return box
