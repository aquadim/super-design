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

    def build_gtk_widget(self):
        raise RuntimeError("Виджет не установлен для свойства")


class BindTextProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self):
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

    def build_gtk_widget(self):
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

    def build_gtk_widget(self):
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

    def build_gtk_widget(self):
        btn = Gtk.CheckButton.new_with_label(self.label)
        btn.set_active(self.value)
        return btn


class EnumProperty(Property):
    def __init__(self, category, obj, prop_name, default_value, label):
        super().__init__(category, obj, prop_name, default_value)
        self.label = label

    def build_gtk_widget(self):
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

    def clicked_ex(self, src, obj):
        print(obj)

    def build_gtk_widget(self):
        # TODO: вынести в ui файл
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)

        # Подпись свойства
        lbl = Gtk.Label(label=self.label)
        lbl.set_halign(Gtk.Align.START)

        entry = Gtk.Entry()
        entry.set_hexpand(True)

        menu_button = Gtk.Button.new_with_label("...")
        menu_button.connect('clicked', self.clicked_ex, self.obj)

        boxentry = Gtk.Box()
        boxentry.set_orientation(Gtk.Orientation.HORIZONTAL)
        boxentry.append(entry)
        boxentry.append(menu_button)

        box.append(lbl)
        box.append(boxentry)
        return box
