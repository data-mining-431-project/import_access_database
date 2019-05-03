import pyodbc, json
from product import Product, Nutrient

conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=C:\Users\Mac\OneDrive\Documents\OneDrive\School\ICSI 431\Course Project\import_access_database\import_access_database\BFPD_07132018.accdb;'
    )
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()

python_database_filename = "nutrition_database.json"

# Writes a list of Objects to a File in JSON format
def writeJSON(objList, fileName, flagAppend = False):
	print "Writing to File"
	items_processed = 0.0
	total_items = len(objList)
	if flagAppend == False:
		f = open(fileName, 'w+')
	else:
		f = open(fileName, 'a+')
	for obj in objList:
		json.dump(obj, f)
		f.write('\n')
		# Progress Indicator
		items_processed = items_processed + 1
		progress_percent = (items_processed/total_items)*100.0
		if items_processed%10000 == 0:
			print ("%05.2f%%" % progress_percent)
	print "Done\n"
	f.close()

# Reads JSON strings from a File and returns a List of Objects that the JSON strings represented
def readJSON(fileName):
	f = open(fileName, 'r+')
	objList = []
	for line in f.readlines():
		objList.append(json.loads(line))
	f.close()
	return objList

def print_access_nutrient_database(nutrient_access_database):
	for row in nutrient_access_database:
		print('Product Number: %s\nNutrient Code: %s\nNutrient Name: %s\nDerivation Code: %s\nOutput Value: %s\nOutput UOM: %s\n' % (row.NDB_No, row.Nutrient_Code, row.Nutrient_Name, row.Derivation_Code, row.Output_Value, row.Output_UOM))

def print_python_database(python_database):
	for product_id, product in python_database:
		print('Product Number: %s\n' % product_id)
		print('Product Name: %s\n' % product.name)
		for nut_code, nutrient in product.nutrients.items():
			print('Nutrient Code: %s\nNutrient Name: %s\n' % (nut_code, nutrient.nutrient_type))
		print product.ingredients

def process_database(nutrient_access_database, product_access_database, processNutrientDatabase = True, processProductDatabase = True):
	
	python_database = dict()
	items_processed = 0.0
	progress_percent = 0.0

	# Processing Nutrient Database
	if processNutrientDatabase:
		print "Processing Nutrient Database"
		total_nutrient_items = float(len(nutrient_access_database))

		python_database[nutrient_access_database[0].NDB_No] = Product(nutrient_access_database[0], False)
		i = 0
		while i < len(nutrient_access_database):
			try:
				if(nutrient_access_database[i].NDB_No == nutrient_access_database[i+1].NDB_No):
					python_database[nutrient_access_database[i].NDB_No].add_nutrient(nutrient_access_database[i])
				else:
					python_database[nutrient_access_database[i].NDB_No].add_nutrient(nutrient_access_database[i])
					python_database[nutrient_access_database[i+1].NDB_No] = Product(nutrient_access_database[i], False)
			except:
				python_database[nutrient_access_database[i].NDB_No].add_nutrient(nutrient_access_database[i])
			# Progress Indicator
			items_processed = items_processed + 1
			progress_percent = (items_processed/total_nutrient_items)*100.0
			if items_processed%100000 == 0:
				print("%05.2f%%" % progress_percent)
			i = i+1

		print "Done\n"

		# Saving Existing Progress...
		print "Saving Stage 1..."
		writeJSON(python_database, python_database_filename)
		print "Done\n"

	# Processing Product Database
	if processProductDatabase:
		print "Processing Product Database"
		total_product_items = float(len(product_access_database))
		items_processed = 0.0
		progress_percent = 0.0

		for row in product_access_database:
			try:
				python_database[row.NDB_Number].add_product_info(row)
			except:
				pass
			# Progress Indicator
			items_processed = items_processed + 1
			progress_percent = (items_processed/total_product_items)*100.0
			if items_processed%10000 == 0:
				print ("%05.2f%%" % progress_percent)

		print "Done\n"
	
	# Saving to file...
	print "Saving to file..."
	writeJSON(python_database, python_database_filename)

	return python_database

def convert_to_json(python_database):
	print "Converting to Json..."
	items_processed = 0.0
	total_items = len(python_database.values())
	json_database = []
	products = python_database.values()
	for i in range(len(products)):
		json_database.append(products[i].convert_to_json())
		# Progress Indicator
		items_processed = items_processed + 1
		progress_percent = (items_processed/total_items)*100.0
		if items_processed%10000 == 0:
			print ("%05.2f%%" % progress_percent)
	print "Done\n"
	return json_database

def convert_from_json(json_database):
	print "Converting from Json..."
	python_database = dict()
	items_processed = 0.0
	total_items = len(json_database)
	for i in range(total_items):
		product = json_database[i]
		id = product[0]
		python_database[id] = Product(None, True)
		python_database[id].id = product[0]

		python_nutrients_list = []
		json_nutrients_list = product[1]
		for json_nutrient in json_nutrients_list:
			nutrient = Nutrient(None, True)
			nutrient.nutrient_type = json_nutrient[0]
			nutrient.nutrient_code = json_nutrient[1]
			nutrient.derivation_code = json_nutrient[2]
			nutrient.value = json_nutrient[3]
			nutrient.unit = json_nutrient[4]
			python_nutrients_list.append(nutrient)
		python_nutrients_dict = dict()
		for nutrient in python_nutrients_list:
			python_nutrients_dict[nutrient.nutrient_code] = nutrient
		python_database[id].nutrients = python_nutrients_dict

		python_database[id].name = product[2]
		python_database[id].unique_code = product[3]
		python_database[id].manufacturer = product[4]
		python_database[id].ingredients = product[5]

		# Progress Indicator
		items_processed = items_processed + 1
		progress_percent = (items_processed/total_items)*100.0
		if items_processed%10000 == 0:
			print ("%05.2f%%" % progress_percent)
	print "Done\n"

def main():
	print "Loading Access Databases"
	nutrient_db = cursor.execute("select NDB_No, Nutrient_Code, Nutrient_Name, Derivation_Code, Output_Value, Output_UOM from Nutrient").fetchall()
	product_db = cursor.execute("select NDB_Number, long_name, gtin_upc, manufacturer, ingredients_english from Products").fetchall()
	print "Done\n"

	#print_access_nutrient_database(nutrient_db)
	python_database = process_database(nutrient_db, product_db)
	writeJSON(convert_to_json(python_database), python_database_filename)
	python_database = convert_from_json(readJSON(python_database_filename))
	#print_python_database(python_database)

if __name__ == '__main__':
	main()
