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

        # какому id соответствует привязка имени
        self.id_to_binding = {}

    def build_right_editor(self, code):
        style_manager = GtkSource.StyleSchemeManager.get_default()
        style = style_manager.get_scheme("solarized-dark")

        lm = GtkSource.LanguageManager()
        language = lm.get_language("bsl")

        buffer_ = GtkSource.Buffer.new_with_language(language)
        buffer_.set_text(code)
        buffer_.set_style_scheme(style)

        view = GtkSource.View.new_with_buffer(buffer_)
        view.add_css_class("bsl-editor")
        view.set_monospace(True)
        view.set_show_line_numbers(True)
        view.set_show_line_marks(True)
        view.set_tab_width(4)

        sw = Gtk.ScrolledWindow()
        sw.set_child(view)
        return sw

    def close_tab(self, src, id_):
        if not id_ in self.tabs:
            return
        page_widget = self.tabs[id_]
        page_num = self.notebook.page_num(page_widget)
        self.notebook.remove_page(page_num)
        del self.tabs[id_]

    def register_tab(self, id_, page):
        self.tabs[id_] = page

    # Открывает вкладку со свойствами узла конфигурации
    def open_properties(self, node):
        if node.id in self.tabs:
            self.notebook.set_current_page(self.tabs[node.id])
            return

        props = node.get_properties()
        page, refs = widgets.get_properties_page(props, self.configuration)

        tab_box, tab_label, close_btn = widgets.get_notebook_tab_button()
        node.bind_property(
            'name',
            tab_label,
            'label',
            GObject.BindingFlags.SYNC_CREATE,
            model.get_transform_func(node)
        )
        widgets.modify_page(node, page, refs)

        page_num = self.notebook.append_page(page, tab_box)
        close_btn.connect("clicked", self.close_tab, node.id)
        self.notebook.set_current_page(page_num)
        self.notebook.set_tab_reorderable(page, True)
        self.register_tab(node.id, page)

    def open_code(self, code):
        sw = self.build_right_editor(code)
        page_num = self.notebook.append_page(sw, Gtk.Label(label="test editor"))
        self.notebook.set_current_page(page_num)

    # Активация приложения
    def on_activate(self, app):
        # css
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string("""
            frame{background-color: @theme_bg_color;}
            .bsl-editor{font: 20px Cascadia Code;}
        """)

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
        self.notebook.set_scrollable(True)

        paned = self.builder.get_object("main-paned")

        # Заполнение дерева конфигурации
        paned.set_start_child(widgets.get_configuration_tree(self.configuration, self.id_to_binding, self))

        # with open("./example/HTTPServices/СервисОбмена/Ext/Module.bsl", 'r', encoding='utf-8') as f:
        #     self.open_code(f.read())
        # self.open_properties(self.configuration)
        # self.open_properties(model.CatalogNode(
        #     "Номенклатура",
        #     model.LocalisedString({model.DEFAULT_LANG: "Номенклатура"}),
        #     "Наименования",
        #     True
        # ))

        c = Gtk.ShortcutController()
        a = Gtk.CallbackAction.new(
            lambda *_a: self.debug_action(),
            None,
            None,
        )
        t = Gtk.ShortcutTrigger.parse_string("<Control>g")
        s = Gtk.Shortcut.new(t, a)

        c.add_shortcut(s)
        self.window.add_controller(c)

        self.window.set_application(app)
        self.window.present()

    def debug_action(self):
        print("doing debug action")
        #self.configuration.store_lang.children.append(model.LanguageNode("добавленный язык","синоним","коммент","added"))


app = SuperDesign()
app.run(sys.argv)
