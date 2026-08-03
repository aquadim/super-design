from gi.repository import Gtk

def get_properties_page(props, root_node, app):
    # Собранные виджеты
    # container<имя категории> - контейнеры категорий
    # widget<имя свойства> - виджет свойства
    built_widgets = {}

    # Создание страницы
    page_scroll = Gtk.ScrolledWindow()
    page = Gtk.Box()
    page_scroll.set_child(page)
    page.set_orientation(Gtk.Orientation.VERTICAL)
    page.add_css_class("p-3")
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
            category_container.add_css_class("p-3")
            category_container.set_spacing(8)
            category_containers[p.category] = category_container
            category_weights[p.category] = p.category.weight()

            built_widgets[f"container{p.category.written}"] = category_container

        widget = p.build_gtk_widget(root_node, app)
        built_widgets[f"widget{p.prop_name}"] = widget
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

    return page_scroll, built_widgets
