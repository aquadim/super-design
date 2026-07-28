from gi.repository import Gtk, Gio, GObject
import model

# Класс энумерации, наследующий от GObject.Object
class GEnumItem(GObject.Object):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.label = member.written()


def modify_hierarchy(page, refs):
    checkmark = refs["widgetHierarchical"]
    items_to_modify = [
        refs["widgetHierarchyType"],
        refs["widgetFoldersOnTop"],
        refs["widgetLimitLevelCount"],
        refs["widgetLevelCount"]
    ]

    def on_toggled(checkmark_, items_to_modify_):
        active = checkmark_.get_active()
        for item in items_to_modify_:
            item.set_sensitive(active)

    checkmark.connect("toggled", on_toggled, items_to_modify)
    on_toggled(checkmark, items_to_modify)


def modify_page(node, page, refs):
    # Если есть иерархия
    if node.node_type == model.NodeType.CATALOG:
        modify_hierarchy(page, refs)


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


def get_properties_page(props, root_node, app):
    # Хранилище ссылок
    refs = {}

    # Создание страницы
    page_scroll = Gtk.ScrolledWindow()
    page = Gtk.Box()
    page_scroll.set_child(page)
    page.set_orientation(Gtk.Orientation.VERTICAL)
    page.set_margin_start(16)
    page.set_margin_end(16)
    page.set_margin_top(16)
    page.set_margin_bottom(16)
    page.set_spacing(16)

    # Контейнеры для категорий
    category_containers = {}
    category_weights = {}
    for p in props:
        if p.category in category_containers:
            category_container = category_containers[p.category]
        else:
            # Создание контейнера для категории свойств
            category_container = Gtk.Box()
            category_container.set_orientation(Gtk.Orientation.VERTICAL)
            category_container.set_margin_start(16)
            category_container.set_margin_end(16)
            category_container.set_margin_top(16)
            category_container.set_margin_bottom(16)
            category_container.set_spacing(8)
            category_containers[p.category] = category_container
            category_weights[p.category] = p.category.weight()

            refs[f"container{p.category.written}"] = category_container

        widget = p.build_gtk_widget(root_node, app)
        refs[f"widget{p.prop_name}"] = widget
        category_container.append(widget)

    cats_ordered = [k for k, v in sorted(category_weights.items(), key=lambda kv: kv[1])]
    for c in cats_ordered:
        # Рамка
        frame = Gtk.Frame.new()
        frame.set_child(category_containers[c])

        # Расширитель
        category_expander = Gtk.Expander.new_with_mnemonic(
            c.written()
        )
        category_expander.set_child(frame)
        category_expander.set_expanded(True)
        page.append(category_expander)

    return page_scroll, refs


def when_storage_node_changes(src, pos, rem, add, expander):
    expander.set_hide_expander(len(src) == 0)

def get_configuration_tree(configmodel, id_to_binding, app):
    root_model = Gio.ListStore.new(model.Node)
    root_model.append(configmodel)

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

    tree_model = Gtk.TreeListModel.new(
        root = root_model,
        passthrough = False,
        autoexpand = False,
        create_func = create_gio_model,
        user_data = None
    )

    def factory_setup(_factory, list_item):
        label = Gtk.Label(xalign=0.0)
        expander = Gtk.TreeExpander()
        expander.set_child(label)
        list_item.set_child(expander)

    def factory_bind(_factory, list_item, binding_map):
        expander = list_item.get_child()
        label = expander.get_child()

        tree_row = list_item.get_item()
        node = tree_row.get_item()

        if node.node_type == model.NodeType.STORAGE:
            node.children.connect("items-changed", when_storage_node_changes, expander)
        expander.set_hide_expander(len(node.children) == 0)

        # Добавление привязки имени объекта к подписи в дереве
        # transform_func - замыкание, для добавления эмодзи узла
        def transform_func(binding, value):
            return f'{node.emoji} {value}'
        binding = node.bind_property(
            "name",
            label,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
            transform_func)
        binding_map[node.id] = binding

        expander.set_list_row(tree_row)

    def factory_unbind(_factory, list_item, binding_map):
        tree_row = list_item.get_item()
        node = tree_row.get_item()

        # Удаление привязки данных
        if node.id in binding_map:
            binding_map[node.id].unbind()
            del binding_map[node.id]

    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", factory_setup)
    factory.connect("bind", factory_bind, id_to_binding)
    factory.connect("unbind", factory_unbind, id_to_binding)

    selection = Gtk.SingleSelection(model=tree_model) # Можно выбрать только один предмет

    col = Gtk.ColumnViewColumn(title="Имя", factory=factory) # Колонка "Имя"
    col.set_expand(True)

    def on_selected(view, pos):
        selection_model = view.get_model()
        tree_row = selection_model.get_selected_item()
        node = tree_row.get_item()
        if node == None:
            return
        if not node.can_display_properties_page:
            return
        app.open_properties(node)

    column_view = Gtk.ColumnView()
    column_view.set_model(selection)
    column_view.append_column(col)
    column_view.connect("activate", on_selected)

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_child(column_view)
    scrolled.set_size_request(512, -1)
    scrolled.add_css_class("conf-tree")
    return scrolled


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


def get_dropdown_from_enum(enum_type, initial_value):
    items = list(enum_type)

    model = Gio.ListStore(item_type=GEnumItem)
    for member in items:
        model.append(GEnumItem(member))

    dropdown = Gtk.DropDown(model = model)

    def listfactory_setup(_factory, list_item):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # check_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        # check_icon.set_visible(False)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)

        box.append(label)
        # box.append(check_icon)

        list_item.set_child(box)
        list_item.__lbl = label
        # list_item.__check = check_icon

    def listfactory_bind(_factory, list_item):
        enum_variant = list_item.get_item()
        # check: Gtk.Image = list_item.__check
        label: Gtk.Label = list_item.__lbl

        # Если выбран - проставить галочку
        #check_icons[enum_variant.member] = check
        # selected_pos = dropdown.get_selected()
        # if selected_pos == Gtk.INVALID_LIST_POSITION:
        #     this_is_selected = False
        # else:
        #     # В Gtk.ListItem есть get_position() (позиция в model)
        #     this_is_selected = (list_item.get_position() == selected_pos)
        #
        # check.set_visible(this_is_selected)
        label.set_label(enum_variant.label)

    def factory_setup(_factory, list_item):
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        list_item.set_child(label)

    def factory_bind(_factory, list_item):
        enum_variant = list_item.get_item()
        label = list_item.get_child()
        label.set_label(enum_variant.label)

    listfactory = Gtk.SignalListItemFactory()
    listfactory.connect("setup", listfactory_setup)
    listfactory.connect("bind", listfactory_bind)

    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", factory_setup)
    factory.connect("bind", factory_bind)

    dropdown.set_factory(factory)
    dropdown.set_list_factory(listfactory)
    dropdown.set_selected(items.index(initial_value))

    return dropdown
