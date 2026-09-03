from gi.repository import Gtk
from .Helpers import close_window_on_esc

class OnFocusChangeEventData:
	__slots__ = ('language_ptr', 'updated_dict', 'big')
	def __init__(self, updated_dict, language_ptr, big):
		self.updated_dict = updated_dict
		self.language_ptr = language_ptr
		self.big = big

def on_focus_change(src, has_focus, ev_data):
	if ev_data.big:
		buffer = src.get_buffer()
		start_iter = buffer.get_start_iter()
		end_iter = buffer.get_end_iter()
		ev_data.updated_dict[ev_data.language_ptr] = buffer.get_text(start_iter, end_iter, False)
	else:
		ev_data.updated_dict[ev_data.language_ptr] = src.get_text()

# Возвращает виджет
def get_localised_string_editor(localised_string, store_lang, big, update_callback, cancel_callback):
	win = Gtk.Window()
	win.set_title("Редактирование локализованного текста")
	win.set_destroy_with_parent(True)
	win.set_modal(True)
	close_window_on_esc(win)

	if big:
		win.set_default_size(512,512)
	else:
		win.set_default_size(512,256)

	sw = Gtk.ScrolledWindow()
	sw.set_vexpand(True)

	page = Gtk.Box()
	page.set_orientation(Gtk.Orientation.VERTICAL)
	page.set_margin_start(16)
	page.set_margin_end(16)
	page.set_margin_top(16)
	page.set_margin_bottom(16)
	page.set_spacing(16)

	updated_dict = {}

	for language in store_lang.children:
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
		
		updated_dict[language] = text

		# Большой текст?
		if big:
			buf = Gtk.TextBuffer.new()
			buf.set_text(text, -1)
			lang_entry = Gtk.TextView.new_with_buffer(buf)
			lang_entry.set_size_request(-1, 64)
		else:
			lang_entry = Gtk.Entry.new_with_buffer(Gtk.EntryBuffer.new(
				text,
				-1
			))
		lang_entry.connect(
			"notify::has-focus",
			on_focus_change,
			OnFocusChangeEventData(updated_dict, language, big)
		)

		lang_box.append(lang_label)
		lang_box.append(lang_entry)
		page.append(lang_box)

	# Командная панель
	command_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
	command_bar.add_css_class("p-3")

	# -- Готово -- #
	select_current = Gtk.Button(label="Готово")
	select_current.connect("clicked", lambda src : update_callback(updated_dict))
	command_bar.append(select_current)

	# -- Отмена -- #
	cancel = Gtk.Button(label="Отмена")
	cancel.connect("clicked", lambda src : cancel_callback())
	command_bar.append(cancel)

	frame = Gtk.Frame()
	frame.set_child(sw)
    
	body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	body.append(command_bar)
	body.append(frame)

	sw.set_child(page)
	win.set_child(body)
	win.connect("close-request", lambda src: cancel_callback())

	return win
