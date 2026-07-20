import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject
import widgets
import sys
import observable


class Property:
    def __init__(self, category, obj, prop_name, default_value):
        self.category = category
        self.obj = obj
        self.prop_name = prop_name
        self.value = default_value

    def build_gtk_widget(self, root_node):
        raise RuntimeError("Виджет не установлен для свойства")


class BindTextProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node):
        # TODO: вынести в ui файл
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)

        # Подпись свойства
        lbl = Gtk.Label(label=self.label)
        lbl.set_halign(Gtk.Align.START)

        # Связка с данными
        default_buffer = Gtk.EntryBuffer.new(self.value, -1)
        entry = Gtk.Entry.new_with_buffer(default_buffer)
        entry.bind_property('text', self.obj, self.prop_name, GObject.BindingFlags.BIDIRECTIONAL)

        box.append(lbl)
        box.append(entry)
        return box


class SimpleTextProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node):
        # TODO: вынести в ui файл
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)

        # Подпись свойства
        lbl = Gtk.Label(label=self.label)
        lbl.set_halign(Gtk.Align.START)

        # Связка с данными
        def on_edit_done(src):
            print("editing done")
        default_buffer = Gtk.EntryBuffer.new(self.value, -1)
        entry = Gtk.Entry.new_with_buffer(default_buffer)
        entry.connect("changed", on_edit_done)

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

    def build_gtk_widget(self, root_node):
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

    def build_gtk_widget(self, root_node):
        btn = Gtk.CheckButton.new_with_label(self.label)
        btn.set_active(self.value)
        return btn


class EnumProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node):
        enum_type = type(getattr(self.obj, self.prop_name))
        dropdown = widgets.get_dropdown_from_enum(enum_type, self.value)

        lbl = Gtk.Label(label=self.label)
        lbl.set_halign(Gtk.Align.START)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.append(lbl)
        box.append(dropdown)
        return box


class LocalisedStringProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self, root_node):
        # Контейнер свойства
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)

        # Подпись свойства
        lbl = Gtk.Label(label = self.label)
        lbl.set_halign(Gtk.Align.START)

        # Поле ввода
        entry = Gtk.Entry()
        entry.set_hexpand(True)
        entry.set_editable(len(root_node.store_lang.children) == 1)
        if len(root_node.store_lang.children) > 1:
            values = "; ".join(list(self.value.values()))
            initial_buffer = Gtk.EntryBuffer.new(values, -1)
        else:
            the_only_key = next(iter(self.value))
            initial_buffer = Gtk.EntryBuffer.new(self.value[the_only_key], -1)
        entry.set_buffer(initial_buffer)

        # При изменении количества языков, TODO: обновлять entry
        def on_change_langs(ev, payload):
            print("changed languages")
        hid = root_node.store_lang.children.register_handler(on_change_langs)

        # Кнопка открытия окна с редактированием всех строк
        menu_button = Gtk.Button.new_with_label("...")
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
        boxentry.append(entry)
        boxentry.append(menu_button)

        # Упаковка
        box.append(lbl)
        box.append(boxentry)
        def on_destroy(w, ex):
            for hid in ex.handlers:
                ex.storage.unregister_handler(hid)
        box.connect(
            "destroy",
            on_destroy,
            observable.DestroyInfo(
                root_node.store_lang.children,
                [hid]
            )
        )

        return box
