import csv

class DataModder:

	@classmethod
	def parsecsv(self, filename: str, colnames: list) -> dict:
		# returns {'column_name1': ['item1','item2','item3'], ...}
		if len(colnames) <= 0: return {}
		result = {}
		for col in colnames: result[col] = []

		try:
			with open(filename, 'r') as f:
				file = csv.DictReader(f)
				for line in file:
					for col in colnames:
						result[col].append(line[col])
			return result
		except:
			return {}

	@classmethod
	def createcsv(self, data: dict, outfile: str) -> dict:
		# data = {'column_name1': ['item1','item2','item3'], ...}
		keys = list(data.keys()); values = list(data.values())
		if len(keys) == 0 or len(values) == 0:
			return {'status': 400, 'message': 'Error: input keys/values cannot be empty.'}
		max_key = max(data, key= lambda x: len(set(data[x])))
		new_data = [keys]
		try:
			for i, _ in enumerate(data[max_key]):
				row = []
				for j, _ in enumerate(keys):
					try:
						key = keys[j]
						row.append(data[key][i])
					except:
						row.append('')
				new_data.append(row)
		except:
			return {'status': 400, 'message': 'Error: failed to parse data from input.'}

		try:
			with open(outfile, mode='w', newline='') as f:
				csv.writer(f).writerows(new_data)
			return {'status': 200, 'message': 'File created: {}.'.format(outfile)}
		except:
			return {'status': 400, 'message': 'Error: failed to write data to {}.'.format(outfile)}

	@classmethod
	def append_col(self, column: list, filename: str, outfile: str) -> dict:
		# column = ['column_name1','item1','item2','item3']
		new_data = []

		try:
			with open(filename, mode='r') as f:
				file = csv.reader(f)
				for i, item in enumerate(file):
					try:
						item.append(column[i])
					except IndexError:
						item.append('N/A')
					new_data.append(item)
		except:
			return {'status': 400, 'message': 'Error: failed to parse data from {}.'.format(filename)}

		try:
			with open(outfile, mode='w', newline='') as f:
				csv.writer(f).writerows(new_data)
			return {'status': 200, 'message': 'File created: {}.'.format(outfile)}
		except:
			return {'status': 400, 'message': 'Error: failed to write data to {}.'.format(outfile)}

# What to do with Excel files?
#	{'address': ['bc1qf09trvgwx966kxn622z8zedctruh50gur7pds7'],
#	'privkey': ['L4epCqLBx5RQ4iazoLXy5b4kYgkqw1h1LwYB5vM1e7a3uPwvLGjN']}
