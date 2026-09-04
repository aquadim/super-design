from gi.repository import Gtk, GObject
import model

def close_window_on_esc(window):
    controller = Gtk.ShortcutController.new()
    trigger = Gtk.ShortcutTrigger.parse_string("Escape")
    action = Gtk.NamedAction.new("window.close")

    shortcut = Gtk.Shortcut.new(trigger, action)
    controller.add_shortcut(shortcut)

    window.add_controller(controller)

# Возвращает фабрику для колонки "Имя"
def get_name_factory(need_expander=True):
    def name_factory_setup(_factory, list_item, _need_expander):
        label = Gtk.Label(xalign=0.0)
        if _need_expander:
            expander = Gtk.TreeExpander()
            expander.set_child(label)
            list_item.set_child(expander)
        else:
            list_item.set_child(label)

    def name_factory_bind(_factory, list_item, _need_expander):
        tree_row = list_item.get_item()
        node = tree_row.get_item()

        if _need_expander:
            expander = list_item.get_child()
            label = expander.get_child()
            expander.set_list_row(tree_row)
        else:
            label = list_item.get_child()

        # Связка с именем
        node.bind_property(
            "name",
            label,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
            lambda _, value: f'{node.emoji} {value}')

    name_factory = Gtk.SignalListItemFactory()
    name_factory.connect("setup", name_factory_setup, need_expander)
    name_factory.connect("bind", name_factory_bind, need_expander)

    return name_factory

def create_gio_tree_model(item, user_data):
    # В узлах хранилища дети хранятся в Gio.ListStore
    # Благодаря этому, из приложения мы можем добавлять
    # объекты конфигурации и они сразу отобразятся в интерфейсе
    if item.node_type == model.NodeType.STORAGE:
        return item.children