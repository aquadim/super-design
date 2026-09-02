import properties as p
from .xmltools import (
	get_mdo_ns,
	new_file,
	tostring,
	new_mdo_xml,
)
from .enums import NodeType
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
		UseOrdinaryFormInManagedApplication,
		ScriptVariant,):

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
		self.ManagedApplicationModule = None
		self.SessionModule = None
		self.DefaultLanguage = None
		self.ScriptVariant = ScriptVariant

	def get_properties(self, configuration):
		return super().get_properties(configuration) + [
			p.SourceCode("ManagedApplicationModule", self, self.ManagedApplicationModule),
			p.SourceCode("SessionModule", self, self.SessionModule),
			p.SourceCode("ExternalConnectionModule", self, self.ExternalConnectionModule),
			p.Text("Vendor", self, self.Vendor),
			p.Text("Version", self, self.Version),
			p.Text("UpdateCatalogAddress", self, self.UpdateCatalogAddress),
			p.Enum("DefaultRunMode", self, self.DefaultRunMode),
			p.Object("DefaultLanguage", self, self.DefaultLanguage, self.store_lang, True),
			p.Enum("ScriptVariant", self, self.ScriptVariant),
		]

	def export(self, dir_path):
		ns = get_mdo_ns()
		mdo = new_mdo_xml(ns)
		content = tostring(mdo)
		with new_file(dir_path, self.name) as f:
			f.write(content)
