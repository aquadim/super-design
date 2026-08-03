from gi.repository import Gtk

# Возвращает виджет
def get_notebook_tab_button():
    tab_box = Gtk.Box()
    tab_box.set_orientation(Gtk.Orientation.HORIZONTAL)

    label = Gtk.Label()

    close_btn = Gtk.Button.new_with_label("[x]")
    close_btn.add_css_class("flat")
    close_btn.add_css_class("destructive-action")

    tab_box.append(label)
    tab_box.append(close_btn)

    return (tab_box, label, close_btn)
