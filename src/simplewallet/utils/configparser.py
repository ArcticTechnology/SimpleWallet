import os
import sys
import json
import importlib.resources

class ConfigParser:

	@classmethod
	def get_config(self):
		build_file = os.path.abspath(os.path.join(
			sys.prefix, 'PythonStarterPackage/config', 'config.json'))
		build_exists = os.path.exists(build_file)

		dev_file = os.path.abspath(os.path.join(os.path.dirname(
			os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
			'config', 'config.json'))
		dev_exists = os.path.exists(dev_file)

		if build_exists == True:
			file = build_file
		elif dev_exists == True:
			file = dev_file
		else:
			return {'status': 400, 'message': 'Could not find config file.', 'output': None}

		output = self.read_file(file)
		return {'status': 200, 'message': 'Read config file complete.', 'output': output}

	@classmethod
	def read_file(self, file):
		with open(file, 'r') as f:
			return json.load(f)