import model


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
