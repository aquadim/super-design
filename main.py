import gi
import sys
import os
gi.require_version("Gtk", "4.0")
gi.require_version('Gdk', '4.0')
gi.require_version("GtkSource", "5")
from gi.repository import Gtk, GObject, GtkSource, Gdk, Gio
import loading
import widgets
from pathlib import Path


class SuperDesign(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.super.design")

        self.bindings = {}

        # Загрузка ресурсов
        resource_path = os.path.join(os.path.dirname(__file__), "resources.gresource")
        resource = Gio.Resource.load(resource_path)
        Gio.resources_register(resource)

        # Сборка модели
        self.configuration = loading.xml_to_model(Path("/home/kor/code/super/example/"))

        self.notebook = None
        self.connect("activate", self.on_activate)
        self.tabs = {}

    # Действие выхода из приложения
    def action_quit(self, action, param):
        self.quit()

    # Действие выгрузки
    def action_export(self, action, param):
        self.configuration.export(Path("./test-export"))

    # Загрузка приложения
    def do_startup(self):
        Gtk.Application.do_startup(self)

        # ВЫХОД (ctrl+q)
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.action_quit)
        self.add_action(action)
        self.set_accels_for_action("app.quit", ["<Control>q"])

        # ЭКСПОРТ (ctrl+e)
        action = Gio.SimpleAction.new("export", None)
        action.connect("activate", self.action_export)
        self.add_action(action)
        self.set_accels_for_action("app.export", ["<Control>e"])

        # Построение менюбара
        menubar_builder = Gtk.Builder()
        menubar_builder.add_from_resource("/com/super/design/ui/menu.ui")
        self.set_menubar(menubar_builder.get_object("menubar"))

    def build_right_editor(self, code):
        style_manager = GtkSource.StyleSchemeManager.get_default()
        style = style_manager.get_scheme("solarized-dark")

        lm = GtkSource.LanguageManager()
        language = lm.get_language("bsl")

        buffer_ = GtkSource.Buffer.new_with_language(language)
        buffer_.set_text(code)
        buffer_.set_style_scheme(style)

        # тэг буфера для свернутых участков кода
        buffer_.create_tag("invisible", invisible=True)

        # TODO: лексер bsl кода

        # Создание виджета редактора кода
        view = GtkSource.View.new_with_buffer(buffer_)
        view.add_css_class("bsl-editor")
        view.set_monospace(True)
        view.set_show_line_numbers(True) # показывать номера строк
        view.set_show_line_marks(True) # показывать отступы (gutters)
        view.set_tab_width(4) # ширина отступов

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
        # Если вкладка со свойствами уже существует, открываем существующую
        if node.id in self.tabs:
            page_num = self.notebook.page_num(self.tabs[node.id])
            self.notebook.set_current_page(page_num)
            return

        page = widgets.get_properties_page(node, self)

        tab_box, tab_label, close_btn = widgets.get_notebook_tab_button()
        node.bind_property(
            'name',
            tab_label,
            'label',
            GObject.BindingFlags.SYNC_CREATE,
            lambda _binding,value: f'{node.emoji} {node.node_type.written()} "{value}"'
        )

        page_num = self.notebook.append_page(page, tab_box)
        close_btn.connect("clicked", self.close_tab, node.id)
        self.notebook.set_current_page(page_num)
        self.notebook.set_tab_reorderable(page, True)
        self.register_tab(node.id, page)

    def open_code(self, sourcecode):
        sw = self.build_right_editor(sourcecode.get_content())

        tab_box, tab_label, close_btn = widgets.get_notebook_tab_button()

        def get_tab_transform_func(sourcecode_):
            def func(binding, value):
                return f'{sourcecode_.node.emoji} {sourcecode_.code_type.written()} "{value}"'
            return func

        sourcecode.node.bind_property(
            'name',
            tab_label,
            'label',
            GObject.BindingFlags.SYNC_CREATE,
            get_tab_transform_func(sourcecode)
        )

        page_num = self.notebook.append_page(sw, tab_box)
        close_btn.connect("clicked", self.close_tab, sourcecode.tabid)
        self.notebook.set_current_page(page_num)
        self.register_tab(sourcecode.tabid, sw)

    # Активация приложения
    def on_activate(self, app):
        # Загрузка CSS приложения
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource("/com/super/design/ui/app.css")

        # Добавляем поставщика стилей к экрану
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        # --- Построение интерфейса --- #
        builder = Gtk.Builder()
        builder.add_from_resource("/com/super/design/ui/root4.ui")

        # Вкладки
        self.notebook = builder.get_object("main-notebook")
        self.notebook.set_scrollable(True)

        # Заполнение дерева конфигурации
        paned = builder.get_object("main-paned")
        paned.set_start_child(
            widgets.get_configuration_tree(self)
        )

        # Комбинации клавиш
        c = Gtk.ShortcutController()
        a = Gtk.CallbackAction.new(
            lambda *_a: self.debug_action(),
            None,
            None,
        )
        t = Gtk.ShortcutTrigger.parse_string("<Control>g")
        s = Gtk.Shortcut.new(t, a)
        c.add_shortcut(s)

        # Представление окна
        window = builder.get_object("main-window")
        window.add_controller(c)
        window.set_application(self)
        window.present()

    def debug_action(self):
        print("doing debug action")


app = SuperDesign()
app.run(sys.argv)
