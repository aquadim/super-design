import properties as p
from .xmltools import (
	get_mdo_ns,
	new_file,
	tostring,
	new_mdo_xml,
)
from .enums import NodeType, CategoryType
from .Node import Node
from .StoreNode import StoreNode

# Корневой узел конфигурации
class RootNode(Node):
	emoji = "🟡"
	can_display_properties_page = True

	def __init__(
		self,
		Name,
		Synonym,
		Comment,
		IncludeHelpInContents,
		HelpHTMLContent,
		ConfigurationExtensionCompatibilityMode_,
		DefaultRunMode_,
		Vendor,
		Version,
		UpdateCatalogAddress,
		UseManagedFormInOrdinaryApplication,
		UseOrdinaryFormInManagedApplication):

		ID = "root"

		# Хранилища объектов
		self.store_lang = StoreNode("⋮💬", "Языки", ID)
		self.store_catalog = StoreNode("⋮📦", "Справочники", ID)
		self.store_subsystem = StoreNode("⋮🗂️", "Подсистемы", ID)
		self.store_commonmodule = StoreNode("⋮📃", "Общие модули", ID)

		super().__init__(
			ID,
			Name,
			Synonym,
			Comment,
			NodeType.CONFIGURATION,
			[
				self.store_subsystem,
				self.store_commonmodule,
				self.store_lang,
				self.store_catalog,
			]
		)
		self.IncludeHelpInContents = IncludeHelpInContents
		self.HelpHTMLContent = HelpHTMLContent
		self.ConfigurationExtensionCompatibilityMode = ConfigurationExtensionCompatibilityMode_
		self.DefaultRunMode = DefaultRunMode_
		self.Vendor = Vendor
		self.Version = Version
		self.UseManagedFormInOrdinaryApplication = UseManagedFormInOrdinaryApplication
		self.UseOrdinaryFormInManagedApplication = UseOrdinaryFormInManagedApplication
		self.UpdateCatalogAddress = UpdateCatalogAddress

	def get_properties(self):
		return super().get_properties()
		# return super().get_properties() + [
		# 	p.EnumProperty(
		# 		CategoryType.GENERAL,
		# 		self, 'DefaultRunMode', self.DefaultRunMode,
		# 		"Основной режим запуска"),
		# 	p.SimpleTextProperty(
		# 		CategoryType.DEVELOPMENT,
		# 		self, 'Vendor', self.Vendor,
		# 		"Поставщик"),
		# 	p.SimpleTextProperty(
		# 		CategoryType.DEVELOPMENT,
		# 		self,
		# 		'Version', self.Version,
		# 		"Версия"),
		# 	p.SimpleTextProperty(
		# 		CategoryType.DEVELOPMENT,
		# 		self, 'UpdateCatalogAddress', self.UpdateCatalogAddress,
		# 		"Адрес каталога обновлений"),
        #     p.BoolProperty(
		# 		CategoryType.GENERAL,
		# 		self, 'UseManagedFormInOrdinaryApplication', self.UseManagedFormInOrdinaryApplication,
		# 		"Использовать управляемые формы в обычном приложении"),
		# 	p.BoolProperty(
		# 		CategoryType.GENERAL,
		# 		self, 'UseOrdinaryFormInManagedApplication', self.UseOrdinaryFormInManagedApplication,
		# 		"Использовать обычные формы в управляемом приложении"),
		# 	p.BoolProperty(
		# 		CategoryType.HELP,
		# 		self, 'IncludeHelpInContents', self.IncludeHelpInContents,
		# 		"Включать в содержание справки"),
		# 	p.SimpleTextProperty(
		# 		CategoryType.HELP, self, 'HelpHTMLContent', self.HelpHTMLContent,
		# 		"Справка")
		# 	]

	def export(self, dir_path):
		ns = get_mdo_ns()
		mdo = new_mdo_xml(ns)
		content = tostring(mdo)
		with new_file(dir_path, self.name) as f:
			f.write(content)
