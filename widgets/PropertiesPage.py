from gi.repository import Gtk, GObject
import model

def get_properties_page(node, app):
    builder = Gtk.Builder()
    builder.add_from_resource(f"/com/super/design/ui/properties/{str(node.node_type)}.compiled.ui")
    container = builder.get_object("container")

    # Выполнение привязок данных
    properties = node.get_properties(app.configuration)
    for p in properties:
        p.bind(builder, app)

    # Пост-обработка
    # Для иерархии справочника
    if node.node_type == model.enums.NodeType.CATALOG:
        checkbutton = builder.get_object("Hierarchical")
        group = builder.get_object("bind-to-Hierarchical")
        checkbutton.bind_property("active", group, "sensitive", GObject.BindingFlags.SYNC_CREATE)

    return container
