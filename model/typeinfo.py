# Строка
class String:
	__slots__ = ("Length","AllowedLength")
	def __init__(self,Length,AllowedLength):
		self.Length = Length
		self.AllowedLength = AllowedLength


# Число
class Number:
	__slots__ = ("Digits","FractionDigits","NonNegative")
	def __init__(self,Digits,FractionDigits,NonNegative):
		self.Digits = Digits
		self.FractionDigits = FractionDigits
		self.NonNegative = NonNegative


# Ссылка
# ObjectName - имя объекта конфигурации на который указывает ссылка
class Reference:
	__slots__ = ("ObjectName", "RefType")
	def __init__(self,ObjectName,RefType):
		self.ObjectName = ObjectName
		self.RefType = RefType


# Хранилище типов
class TypeStorage:
	def __init__(self):
		self.numbers = {}
		self.strings = {}
		self.refs = {}

	def get_number_type(self, digits, fraction_digits, non_negative):
		key = f"{digits}.{fraction_digits}.{non_negative}"
		if key in self.numbers:
			return self.numbers[key]

		num = Number(digits, fraction_digits, non_negative)
		self.numbers[key] = num
		return num
