from gi.repository import Gtk, Gio, GObject


# Класс энумерации, наследующий от GObject.Object
class GEnumItem(GObject.Object):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.label = member.written()


def listfactory_setup(_factory, list_item):
	box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

	label = Gtk.Label()
	label.set_halign(Gtk.Align.START)

	box.append(label)

	list_item.set_child(box)
	list_item.__lbl = label


def listfactory_bind(_factory, list_item):
	enum_variant = list_item.get_item()
	label: Gtk.Label = list_item.__lbl
	label.set_label(enum_variant.label)


def factory_setup(_factory, list_item):
	label = Gtk.Label()
	label.set_halign(Gtk.Align.START)
	list_item.set_child(label)


def factory_bind(_factory, list_item):
	enum_variant = list_item.get_item()
	label = list_item.get_child()
	label.set_label(enum_variant.label)


# Возвращает виджет
def get_dropdown_from_enum(enum_type, initial_value):
    items = list(enum_type)

    model = Gio.ListStore(item_type=GEnumItem)
    for member in items:
        model.append(GEnumItem(member))

    dropdown = Gtk.DropDown(model = model)

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
