from gi.repository import Gtk, Gio, GObject
import model


BINDING_PREFIX = "configuration-tree"


def when_storage_node_changes(src, pos, rem, add, expander):
    expander.set_hide_expander(len(src) == 0)

# Функция построения Gio модели
def create_gio_model(item, user_data):
	children = getattr(item, "children")

	# В узлах хранилища дети хранятся в Gio.ListStore
	# Благодаря этому, из приложения мы можем добавлять
	# объекты конфигурации и они сразу отобразятся в интерфейсе
	if item.node_type == model.NodeType.STORAGE:
		return children

	# Детей нет, возвращаем Null (None)
	if len(children) == 0:
		return None

	# В обычных узлах дети не меняются
	# Поэтому модель мы сделали раз и она осталась
	gio_model = Gio.ListStore.new(model.Node)
	for c in children:
		gio_model.append(c)
	return gio_model

def factory_setup(_factory, list_item):
	label = Gtk.Label(xalign=0.0)
	expander = Gtk.TreeExpander()
	expander.set_child(label)
	list_item.set_child(expander)


def factory_bind(_factory, list_item, app):
	expander = list_item.get_child()
	label = expander.get_child()

	tree_row = list_item.get_item()
	node = tree_row.get_item()

	# Прятать раскрыватель когда детей нет
	if node.node_type == model.NodeType.STORAGE:
		node.children.connect("items-changed", when_storage_node_changes, expander)
	expander.set_hide_expander(len(node.children) == 0)

	binding = node.bind_property(
		"name",
		label,
		"label",
		GObject.BindingFlags.SYNC_CREATE,
		lambda binding, value: f'{node.emoji} {value}')
	app.bindings[BINDING_PREFIX+node.id] = binding

	expander.set_list_row(tree_row)


def factory_unbind(_factory, list_item, app):
	tree_row = list_item.get_item()
	node = tree_row.get_item()

	# Удаление привязки данных
	if BINDING_PREFIX+node.id in app.bindings:
		app.bindings[BINDING_PREFIX+node.id].unbind()
		del app.bindings[BINDING_PREFIX+node.id]


def on_selected(view, pos, app):
	selection_model = view.get_model()
	tree_row = selection_model.get_selected_item()
	node = tree_row.get_item()
	if node == None:
		return

	# При клике в дереве по общему модулю открывать его
	# исходный код, а не окно свойств.
	if node.node_type == model.NodeType.COMMONMODULE:
		app.open_code(node.Module)
		return

	if node.can_display_properties_page:
		app.open_properties(node)


# Возвращает виджет дерева конфигурации
def get_configuration_tree(app):
    root_model = Gio.ListStore.new(model.Node)
    root_model.append(app.configuration)

    tree_model = Gtk.TreeListModel.new(
        root = root_model,
        passthrough = False,
        autoexpand = False,
        create_func = create_gio_model,
        user_data = None
    )
    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", factory_setup)
    factory.connect("bind", factory_bind, app)
    factory.connect("unbind", factory_unbind, app)

    selection = Gtk.SingleSelection(model=tree_model) # Можно выбрать только один предмет

    col = Gtk.ColumnViewColumn(title="Имя", factory=factory) # Колонка "Имя"
    col.set_expand(True)

    column_view = Gtk.ColumnView()
    column_view.set_model(selection)
    column_view.append_column(col)
    column_view.connect("activate", on_selected, app)

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_child(column_view)
    scrolled.set_size_request(256, -1)
    scrolled.add_css_class("conf-tree")
    return scrolled
