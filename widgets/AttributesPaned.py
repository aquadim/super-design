from gi.repository import Gtk, GObject

class BuilderWithBindings:
    __slots__ = ('b','box','bindings')
    def __init__(self, b, box):
        self.b = b
        self.box = box
        self.bindings = []

    def clear_bindings(self):
        for b in self.bindings:
            b.unbind()
        self.bindings.clear()

# Возвращает окно прокрутки со всеми реквизитами объекта
def get_attributes_paned(store_attribute, id_to_binding):
    # --- Создание модели и фабрики для отображения списка реквизитов --- #
    lv_model = Gtk.SingleSelection(model=store_attribute.children)

    def lv_factory_setup(_factory, list_item):
        label = Gtk.Label(xalign=0.0)
        list_item.set_child(label)

    def lv_factory_bind(_factory, list_item, binding_map):
        label = list_item.get_child()
        node = list_item.get_item()

        binding = node.bind_property(
            "name",
            label,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
            lambda b_, value: f'{node.emoji} {value}')
        binding_map[node.id] = binding

    def lv_factory_unbind(_factory, list_item, binding_map):
        node = list_item.get_item()

        # Удаление привязки данных
        if node.id in binding_map:
            binding_map[node.id].unbind()
            del binding_map[node.id]

    def on_attribute_selected(view, pos, bwb):
        selection_model = view.get_model()
        attribute = selection_model.get_selected_item()
        if attribute == None:
            return

        bwb.clear_bindings()
        b = bwb.b
        box.set_visible(True)

        # Подпись реквизита связываем с именем узла
        props_title = b.get_object("title")
        bwb.bindings.append(attribute.bind_property(
            "name",
            props_title,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
            lambda _, value: f'Реквизит «{value}»' if value is not None else ""
        ))

        # Имя реквизита
        entry_name = b.get_object("entry-name")
        entry_name.set_text(attribute.name)
        bwb.bindings.append(attribute.bind_property(
            "name",
            entry_name,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL
        ))

    lv_factory = Gtk.SignalListItemFactory()
    lv_factory.connect("setup", lv_factory_setup)
    lv_factory.connect("bind", lv_factory_bind, id_to_binding)
    lv_factory.connect("unbind", lv_factory_unbind, id_to_binding)

    # --- Создание окна свойств реквизита --- #
    b = Gtk.Builder()

    b.add_from_file("ui/attributes_page.ui")
    box = b.get_object("box")
    bwb = BuilderWithBindings(b, box)

    lv = Gtk.ListView()
    lv.set_model(lv_model)
    lv.set_factory(lv_factory)
    lv.set_show_separators(True)
    lv.set_single_click_activate(True)
    lv.connect("activate", on_attribute_selected, bwb)

    # --- Окна прокрутки --- #
    # Окно прокрутки для списка реквизитов
    sw1 = Gtk.ScrolledWindow()
    sw1.set_child(lv)
    sw1.set_size_request(256,512)

    # Окно прокрутки для свойств реквизита
    sw2 = Gtk.ScrolledWindow()
    sw2.set_child(box)
    sw2.set_size_request(512,512)

    paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
    paned.set_start_child(sw1)
    paned.set_end_child(sw2)
    paned.set_wide_handle(True)
    return paned
