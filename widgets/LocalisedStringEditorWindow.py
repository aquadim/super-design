from gi.repository import Gtk


class OnFocusChangeEventData:
	__slots__ = ('obj','prop_name','language_ptr')
	def __init__(self, obj, prop_name, language_ptr):
		self.obj = obj
		self.prop_name = prop_name
		self.language_ptr = language_ptr


def on_focus_change(src, has_focus, ev_data):
	localised_string = getattr(ev_data.obj, ev_data.prop_name)
	localised_string[ev_data.language_ptr] = src.get_text()


# Возвращает виджет
def get_localised_string_editor_window(obj, prop_name, localised_string, big, app):
	win = Gtk.Window()
	win.set_title("Редактирование локализованной строки")
	win.set_destroy_with_parent(True)
	win.set_modal(True)
	win.set_default_size(512,256)

	sw = Gtk.ScrolledWindow()
	page = Gtk.Box()
	page.set_orientation(Gtk.Orientation.VERTICAL)
	page.set_margin_start(16)
	page.set_margin_end(16)
	page.set_margin_top(16)
	page.set_margin_bottom(16)
	page.set_spacing(16)

	for language in app.configuration.store_lang.children:
		# Коробка (подпись + поле ввода)
		lang_box = Gtk.Box()
		lang_box.set_orientation(Gtk.Orientation.VERTICAL)

		# Подпись
		lang_label = Gtk.Label(label=language.name)
		lang_label.set_halign(Gtk.Align.START)

		# Текст
		if language in localised_string:
			text = localised_string[language]
		else:
			text = ""

		# Большой текст?
		if big:
			buf = Gtk.TextBuffer.new()
			buf.set_text(text, -1)
			lang_entry = Gtk.TextView.new_with_buffer(buf)
		else:
			lang_entry = Gtk.Entry.new_with_buffer(Gtk.EntryBuffer.new(
				text,
				-1
			))

		lang_entry.connect(
			"notify::has-focus",
			on_focus_change,
			OnFocusChangeEventData(obj, prop_name, language)
		)

		lang_box.append(lang_label)
		lang_box.append(lang_entry)
		page.append(lang_box)

	sw.set_child(page)
	win.set_child(sw)
	return win
