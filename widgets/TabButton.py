from gi.repository import Gtk

# Возвращает виджет
def get_notebook_tab_button():
    tab_box = Gtk.Box()
    tab_box.set_orientation(Gtk.Orientation.HORIZONTAL)
    tab_box.set_halign(Gtk.Align.START)

    label = Gtk.Label()

    close_btn = Gtk.Button.new_from_icon_name("window-close")

    tab_box.append(label)
    tab_box.append(close_btn)

    return (tab_box, label, close_btn)
