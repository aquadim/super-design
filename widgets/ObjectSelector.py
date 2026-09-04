from gi.repository import Gtk, Gio
import model
from .Helpers import close_window_on_esc, get_name_factory, create_gio_tree_model

def on_selected(view, pos, update_callback):
	selection_model = view.get_model()
	tree_row = selection_model.get_selected_item()
	node = tree_row.get_item()
	if node == None:
		return
	update_callback(node)

def get_single_object_selector(storage_node, non_null, update_callback, cancel_callback):
    root_model = Gio.ListStore.new(model.Node)
    root_model.append(storage_node)

    tree_model = Gtk.TreeListModel.new(
        root = root_model,
        passthrough = False,
        autoexpand = True,
        create_func = create_gio_tree_model,
        user_data = None
    )

    selection = Gtk.SingleSelection(model=tree_model)

    col_name = Gtk.ColumnViewColumn(title="Имя", factory=get_name_factory())
    col_name.set_expand(True)

    column_view = Gtk.ColumnView()
    column_view.set_model(selection)
    column_view.append_column(col_name)
    column_view.connect("activate", on_selected, update_callback)

    sw = Gtk.ScrolledWindow()
    sw.set_child(column_view)
    sw.set_size_request(512, 512)
    sw.add_css_class("conf-tree")

    # Командная панель
    command_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    command_bar.add_css_class("p-3")

    select_current = Gtk.Button(label="Выбрать")
    select_current.connect("clicked", lambda src : update_callback(selection.get_selected_item().get_item()))
    command_bar.append(select_current)
    
    if not non_null:
        clear = Gtk.Button(label="Очистить")
        clear.connect("clicked", lambda src : update_callback(None))
        command_bar.append(clear)

    cancel = Gtk.Button(label="Отмена")
    cancel.connect("clicked", lambda src : cancel_callback())
    command_bar.append(cancel)
    
    body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    body.append(command_bar)
    body.append(sw)

    window = Gtk.Window()
    close_window_on_esc(window)
    window.set_title("Выберите один объект")
    window.set_child(body)
    window.connect("close-request", lambda src: cancel_callback())
    
    return window