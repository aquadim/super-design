import gi
import sys
gi.require_version("Gtk", "4.0")
gi.require_version('Gdk', '4.0')
gi.require_version("GtkSource", "5")
from gi.repository import Gtk, GObject, GtkSource, Gdk
import model
import loading
import widgets
from pathlib import Path


class SuperDesign(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.super.design")

        # Сборка модели
        self.configuration = loading.xml_to_model(Path("./example"))

        self.builder = None
        self.window = None
        self.notebook = None
        self.connect("activate", self.on_activate)
        self.tabs = {}
        self.id_to_binding = {}

    def build_right_editor(self):
        lm = GtkSource.LanguageManager()
        language = lm.get_language("python")
        buffer_ = GtkSource.Buffer.new_with_language(language)
        view = GtkSource.View.new_with_buffer(buffer_)
        view.set_monospace(True)
        view.set_show_line_numbers(True)
        view.set_show_line_marks(True)

        sw = Gtk.ScrolledWindow()
        sw.set_child(view)
        return sw

    # Открывает вкладку со свойствами узла конфигурации
    def open_properties(self, node):
        if node.id in self.tabs:
            self.notebook.set_current_page(self.tabs[node.id])
            return

        props = node.get_properties()
        page, refs = widgets.get_properties_page(props)

        tab_box, tab_label = widgets.get_notebook_tab_button()
        node.bind_property(
            'name',
            tab_label,
            'label',
            GObject.BindingFlags.SYNC_CREATE,
            model.get_transform_func(node)
        )
        widgets.modify_page(node, page, refs)

        page_num = self.notebook.append_page(page, tab_box)
        self.notebook.set_current_page(page_num)
        self.tabs[node.id] = page_num

    # Активация приложения
    def on_activate(self, app):
        # css
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string("frame{background-color: @theme_bg_color;}")

        # Добавляем поставщика стилей к экрану
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui/root4.ui")

        self.window = self.builder.get_object("main-window")
        self.notebook = self.builder.get_object("main-notebook")

        paned = self.builder.get_object("main-paned")

        # Заполнение дерева конфигурации
        paned.set_start_child(widgets.get_configuration_tree(self.configuration, self.id_to_binding, self))

        # self.open_properties(self.configuration)
        # self.open_properties(model.CatalogNode(
        #     "Номенклатура",
        #     model.LocalisedString({model.DEFAULT_LANG: "Номенклатура"}),
        #     "Наименования",
        #     True
        # ))

        self.window.set_application(app)
        self.window.present()


app = SuperDesign()
app.run(sys.argv)
