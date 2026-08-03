from gi.repository import Gtk, Gio, GObject
import model

def get_subsystem_content_tree(configuration, subsystem, selected_nodes, id_to_binding):
    root_model = Gio.ListStore.new(model.Node)
    root_model.append(configuration.store_commonmodule)
    root_model.append(configuration.store_catalog)

    # Функция построения Gio модели
    def create_gio_tree_model(item, user_data):
        # В узлах хранилища дети хранятся в Gio.ListStore
        # Благодаря этому, из приложения мы можем добавлять
        # объекты конфигурации и они сразу отобразятся в интерфейсе
        if item.node_type == model.NodeType.STORAGE:
            return item.children

    tree_model = Gtk.TreeListModel.new(
        root = root_model,
        passthrough = False,
        autoexpand = True,
        create_func = create_gio_tree_model,
        user_data = None
    )

    selection = Gtk.SingleSelection(model=tree_model)

    # ---------- Фабрика для колонки "Имя" ----------
    def name_factory_setup(_factory, list_item):
        label = Gtk.Label(xalign=0.0)
        expander = Gtk.TreeExpander()
        expander.set_child(label)
        list_item.set_child(expander)

    def name_factory_bind(_factory, list_item, binding_map):
        expander = list_item.get_child()
        label = expander.get_child()

        tree_row = list_item.get_item()
        node = tree_row.get_item()

        # Связка с именем
        binding = node.bind_property(
            "name",
            label,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
            lambda _, value: f'{node.emoji} {value}')
        binding_map[subsystem.id + node.id] = binding

        expander.set_list_row(tree_row)

    def name_factory_unbind(_factory, list_item, binding_map):
        node = list_item.get_item().get_item()
        binding_id = subsystem.id + node.id

        # Удаление привязки данных
        if binding_id in binding_map:
            binding_map[binding_id].unbind()
            del binding_map[binding_id]

    name_factory = Gtk.SignalListItemFactory()
    name_factory.connect("setup", name_factory_setup)
    name_factory.connect("bind", name_factory_bind, id_to_binding)
    name_factory.connect("unbind", name_factory_unbind, id_to_binding)
    # ---------- //Фабрика для колонки "Имя" ----------

    # ---------- Фабрика для колонки "Выбрано" (галочка) ----------
    def checkbox_factory_setup(_factory, list_item):
        check = Gtk.CheckButton()
        check.set_focusable(False)          # чтобы не перехватывать фокус
        check.set_halign(Gtk.Align.CENTER)  # выравнивание по центру
        list_item.set_child(check)

    def checkbox_factory_bind(_factory, list_item, selected_nodes_):
        tree_row = list_item.get_item()
        node = tree_row.get_item()

        check_button = list_item.get_child()
        check_button.set_active(node in selected_nodes_)

        # Функция удаления объекта из состава подсистемы
        def remove_node_from_content(node_to_remove, content):
            found, position = content.find(node_to_remove)
            if not found:
                # Пофиг
                return
            content.remove(position)

        # Функция добавления объекта в состав подсистемы
        def add_node_to_content(node_to_add, content):
            found, position = content.find(node_to_add)
            if not found:
                content.append(node_to_add)

        # Обработчик переключения галочки
        def on_toggled(cb, node):
            # Защита от бесконечной рекурсии
            is_active = cb.get_active()
            is_selected = node in selected_nodes_
            if is_active == is_selected:
                return

            if not is_active:
                if node.node_type == model.NodeType.STORAGE:
                    # Все объекты с таким то хранилищем удаляем
                    for child_node in node.children:
                        remove_node_from_content(child_node, selected_nodes_)
                remove_node_from_content(node, selected_nodes_)
                cb.set_active(False)
            else:
                if node.node_type == model.NodeType.STORAGE:
                    # Все объекты с таким то хранилищем добавляем
                    bulk_append = []
                    for child_node in node.children:
                        found, position = selected_nodes_.find(child_node)
                        if not found:
                            bulk_append.append(child_node)
                    selected_nodes_.splice(0,0,bulk_append)
                add_node_to_content(node, selected_nodes_)
                cb.set_active(True)

        # При изменении в составе подсистемы, обновить интерфейс
        def on_items_changed(model, position, removed, added):
            check_button.set_active(node in selected_nodes_)

        selected_nodes_.connect("items-changed", on_items_changed)
        check_button.connect("toggled", on_toggled, node)

    checkbox_factory = Gtk.SignalListItemFactory()
    checkbox_factory.connect("setup", checkbox_factory_setup)
    checkbox_factory.connect("bind", checkbox_factory_bind, selected_nodes)
    # ---------- //Фабрика для колонки "Выбрано" (галочка) ----------

    # ---------- Сборка ColumnView ----------
    col1 = Gtk.ColumnViewColumn(title="Выбрано", factory=checkbox_factory)
    col2 = Gtk.ColumnViewColumn(title="Имя", factory=name_factory)
    col2.set_expand(True)

    column_view = Gtk.ColumnView()
    column_view.set_model(selection)
    column_view.append_column(col1)
    column_view.append_column(col2)
    # ---------- //Сборка ColumnView ----------

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_child(column_view)
    scrolled.set_size_request(-1, 512)
    scrolled.add_css_class("conf-tree")
    return scrolled
