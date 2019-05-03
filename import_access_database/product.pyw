class Nutrient:
	def __init__(self, db_row, empty):
		if not empty:
			self.nutrient_type = db_row.Nutrient_Name
			self.nutrient_code = int(db_row.Nutrient_Code)
			self.derivation_code = db_row.Derivation_Code
			self.value = float(db_row.Output_Value)
			self.unit = db_row.Output_UOM
		else:
			self.nutrient_type = ""
			self.nutrient_code = 0
			self.derivation_code = ""
			self.value = 0.0
			self.unit = ""
	
	def convert_to_json(self):
		return [self.nutrient_type, self.nutrient_code, self.derivation_code, self.value, self.unit]

class Product:
	def __init__(self, init_row, empty):
		if not empty:
			self.id = int(init_row.NDB_No)
			self.nutrients = dict()
			self.nutrients[init_row.Nutrient_Code] = Nutrient(init_row, False)
			self.name = ""
			self.unique_code = ""
			self.manufacturer = ""
			self.ingredients = ""
			#self.ingredients = []
		else:
			self.id = 0
			self.nutrients = dict()
			self.name = ""
			self.unique_code = ""
			self.manufacturer = ""
			self.ingredients = ""

	def add_nutrient(self, new_row):
		self.nutrients[new_row.Nutrient_Code] = Nutrient(new_row, False)

	def add_product_info(self, new_row):
		self.name = new_row.long_name
		self.unique_code = new_row.gtin_upc
		self.manufacturer = new_row.manufacturer
		#str_ingredients = new_row.ingredients_english
		#self.ingredients = str_ingredients.split()
		self.ingredients = new_row.ingredients_english

	def convert_to_json(self):
		json_format = []
		json_nutrients = []

		json_format.append(self.id)
		nutrients_values = self.nutrients.values()
		for i in range(len(nutrients_values)):
			json_nutrients.append(nutrients_values[i].convert_to_json())
		json_format.append(json_nutrients)
		json_format.append(self.name)
		json_format.append(self.unique_code)
		json_format.append(self.manufacturer)
		json_format.append(self.ingredients)
		return json_format

	def convert_from_json(self):
		print