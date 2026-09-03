from gi.repository import Gtk

def close_window_on_esc(window):
    controller = Gtk.ShortcutController.new()
    trigger = Gtk.ShortcutTrigger.parse_string("Escape")
    action = Gtk.NamedAction.new("window.close")

    shortcut = Gtk.Shortcut.new(trigger, action)
    controller.add_shortcut(shortcut)

    window.add_controller(controller)
