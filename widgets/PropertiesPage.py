from gi.repository import Gtk

def get_properties_page(node):
    builder = Gtk.Builder()
    builder.add_from_resource(f"/com/super/design/ui/properties/{str(node.node_type)}.compiled.ui")
    container = builder.get_object("container")

    # Выполнение привязок данных
    properties = node.get_properties()
    for p in properties:
        p.bind(builder)

    return container
