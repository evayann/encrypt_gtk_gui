"""
Simple program of code/decode element with GTK GUI
"""
import locale
from gi import require_version

require_version('Gtk', '3.0')
from gi.repository import Gtk

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàéîëïê., !?/:;%'()[]{}°0123456789=+-*²~&#_-|^£$¤"
alpha_list = list(alphabet)


def shift(nb_shift):
	"""
	Shift alphabet
	:param nb_shift: The number to shift alphabet
	:return: A copy of alphabet shifted
	"""
	return alphabet[nb_shift:] + alphabet[:nb_shift]


def code_shift(nb_shift, sentence):
	"""
	Code the sentence with shifting method (Cesar)
	:param nb_shift: The number to shift alphabet
	:param sentence: The sentence to encode
	:return: A new string who is the encoded sentence
	"""
	shifted = shift(nb_shift)
	return "".join([shifted[alphabet.find(char)] for char in sentence])


def decode_shift(nb_shift, sentence):
	"""
	Decode the sentence with shifting method (Cesar)
	:param nb_shift: The number to shift alphabet
	:param sentence: The sentence to decode
	:return: A new string who is the encoded sentence
	"""
	return code_shift(-nb_shift, sentence)


def code_binary(sentence):
	"""
	Code the sentence to transform each character to a binary value
	:param sentence: The sentence to code
	:return: A new string who is the encoded sentence
	"""
	# bin(el)[2:] to remove the start of binary. Ex : '0b10' -> '10'
	return "".join([bin(alphabet.find(char))[2:].zfill(7) for char in sentence])


def decode_binary(binary):
	"""
	Decode the sentence to transform each character to a binary value
	:param binary: The binary to decode to obtain sentences
	:return: A new string who is the encoded sentence
	"""
	from re import findall
	binaries = findall("." * 7, binary)
	return "".join([alpha_list[int(b, 2)] for b in binaries])


BIN_MODE = "bin"
SHIFT_MODE = "shift"

def encode(mode, txt):
	if mode == BIN_MODE:
		return code_binary(txt)
	elif mode == SHIFT_MODE:
		return code_shift(5, txt)

def decode(mode, txt):
	if mode == BIN_MODE:
		return decode_binary(txt)
	elif mode == SHIFT_MODE:
		return decode_shift(5, txt)


_ = None # Put _ for multi lang outside of languages to be accessible everywhere (only for interpreter)
LANG_FILE_NAME = "base"
class Languages:
	def __init__(self):
		# Setup all supported language
		import gettext
		where = "locales"
		self.fr = gettext.translation(LANG_FILE_NAME, localedir=where, languages=["fr"])
		self.en = gettext.translation(LANG_FILE_NAME, localedir=where, languages=["en"])

		# And install english for default language
		locale.bindtextdomain(LANG_FILE_NAME, where)
		self.set_english()

	def set_english(self):
		"""
		Set language of application to English
		:return:
		"""
		locale.setlocale(locale.LC_ALL, "en_US.utf8")
		self.en.install()
		global _
		_ = self.en.gettext

	def set_french(self):
		"""
		Set language of application to French
		:return:
		"""
		locale.setlocale(locale.LC_ALL, "fr_FR.utf8")
		self.fr.install()
		global _
		_ = self.fr.gettext


langs = Languages() # Create languages elements before UI elements to let UI use it


class UI:
	def __init__(self):
		# Initialize constant text with good language
		self.TEXT_VIEW_PLACE_HOLDER = _("Your text to ")
		self.CODE = _("code")
		self.DECODE = _("decode")

		__gtype_name__ = _("code/decode")

		# Build interface and bind all signal to this class
		self.builder = Gtk.Builder()
		self.builder.set_translation_domain(LANG_FILE_NAME)
		self.builder.add_from_file("code.glade")
		self.builder.connect_signals(self)
		self.go = self.builder.get_object

		# Bind function to change languages
		self.set_english = langs.set_english
		self.set_french = langs.set_french

		# Get settings and update values
		self.settings = Gtk.Settings.get_default()
		if self.settings.get_property("gtk-application-prefer-dark-theme"):
			self.go("dark_theme_box").set_active(True)

		self.default_sys_theme = self.settings.get_property("gtk-theme-name")
		if self.default_sys_theme == "Adapta":
			self.go("adapta_box").set_active(True)

		self.window = self.go("window")

		# TextView
		self.code = self.go("code_txt")
		self.code.set_name(self.CODE)
		self.decode = self.go("decode_txt")
		self.decode.set_name(self.DECODE)
		# Set placeholder
		self.code.get_buffer().set_text(self.TEXT_VIEW_PLACE_HOLDER + self.CODE)
		self.decode.get_buffer().set_text(self.TEXT_VIEW_PLACE_HOLDER + self.DECODE)

		# Set current mode of code/decode
		self.encoding = SHIFT_MODE
		self.go("bin_code").set_active(True)

	def start(self):
		self.window.show_all()
		Gtk.main()

	def close(self):
		self.window.close()
		Gtk.main_quit()

	# region Signals

	# region Encoding
	def on_bin_code_toggled(self, widget):
		self.encoding = BIN_MODE

	def on_shift_code_toggled(self, widget):
		self.encoding = SHIFT_MODE
	# endregion Encoding

	# region PlaceHolder
	def on_focus_out_text_view(self, widget, user_data):
		buf = widget.get_buffer()
		if buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True) == "":
			buf.set_text(self.TEXT_VIEW_PLACE_HOLDER + widget.get_name())
		return False

	def on_focus_in_text_view(self, widget, user_data):
		buf = widget.get_buffer()
		if buf.get_text(buf.get_start_iter(), buf.get_end_iter(),
		                True) == self.TEXT_VIEW_PLACE_HOLDER + widget.get_name():
			buf.set_text("")
		return False
	# endregion PlaceHolder

	# region Button
	def code(self, widget):
		code_buf = self.code.get_buffer()
		code_txt = code_buf.get_text(code_buf.get_start_iter(), code_buf.get_end_iter(), True)
		if code_txt != self.TEXT_VIEW_PLACE_HOLDER + self.CODE:
			code_buf.set_text(encode(self.encoding, code_txt))

	def decode(self, widget):
		decode_buf = self.decode.get_buffer()
		decode_txt = decode_buf.get_text(decode_buf.get_start_iter(), decode_buf.get_end_iter(), True)
		if decode_txt != self.TEXT_VIEW_PLACE_HOLDER + self.DECODE:
			decode_buf.set_text(decode(self.encoding, decode_txt))
	# endregion Button

	# region Menu
	def on_quit(self, widget):
		self.close()

	def on_open_site(self, widget):
		"""
		Open my personal website
		:param widget:
		:return:
		"""
		from webbrowser import open
		open("yann.fzcommunication.fr")

	def set_adapta(self, widget):
		"""
		Set Adapta theme or default
		:param widget:
		:return:
		"""
		theme = "Adapta" if widget.get_active() else self.default_sys_theme
		self.settings.set_property("gtk-theme-name", theme)

	def set_light(self, widget):
		"""
		Set light or dark color
		:param widget:
		:return:
		"""
		activate = True if widget.get_active() else False
		self.settings.set_property("gtk-application-prefer-dark-theme", activate)

	def set_french(self, widget):
		"""
		Change language to French
		:param widget:
		:return:
		"""
		langs.set_french()
		self.close()
		main() # Reload everything with correct language

	def set_english(self, widget):
		"""
		Change language to English
		:param widget:
		:return:
		"""
		langs.set_english()
		self.close()
		main()
	# endregion Menu
	# endregion Signals

def main():
	ui = UI()
	ui.start()


if __name__ == '__main__':
	main()
