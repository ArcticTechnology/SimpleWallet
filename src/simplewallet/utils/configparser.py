import os; import sys; import json
from ..dircrawler.crawler import Crawler
from ..dircrawler.filemodder import FileModder

class ConfigParser:

	def __init__(self):
		self.build_loc = 'simplewallet/config'
		self.dev_loc = 'config'
		self.filename = 'config.json'
		self.path_type = None
		self.rootpath = None
		self.filepath = None
		self.update()

	def _find(self):
		build_rootpath = Crawler.joinpath(sys.prefix, self.build_loc)
		build_filepath = Crawler.joinpath(build_rootpath, self.filename)
		build_exists = os.path.exists(build_filepath)

		dev_rootpath = Crawler.joinpath(os.path.dirname(
			os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
			self.dev_loc)
		dev_filepath = Crawler.joinpath(dev_rootpath, self.filename)
		dev_exists = os.path.exists(dev_filepath)

		if build_exists == True:
			self.path_type = 'build'
			self.rootpath = build_rootpath
			self.filepath = build_filepath
		elif dev_exists == True:
			self.path_type = 'dev'
			self.rootpath = dev_rootpath
			self.filepath = dev_filepath
		else:
			self.path_type = 'build'
			self.rootpath = build_rootpath
			self.filepath = None
			self.filename = None

	def hasContent(self):
		if self.filepath == None: return False
		if os.stat(self.filepath).st_size > 0:
			return True
		else:
			return False

	def update(self):
		self._find()
		has_content = self.hasContent()
		if has_content == True:
			return {'status': 200,
					'message': 'Update config file complete.'}
		else:
			return {'status': 400,
					'message': 'Error: config file not found or empty.'}

	def parse(self):
		try:
			file_content = ''.join(FileModder.read_file(self.filepath))
		except:
			return {'status': 400,
						'message': 'Error: config file could not be read.', 'output': None}

		try:
			result = json.loads(file_content)
			return {'status': 200, 'message': 'Read config file complete.',
					'output': result}
		except:
			return {'status': 400,
				'message': 'Error: config file not structured correctly.',
				'output': None}

	def write(self, data):
		if self.filepath == None:
			return {'status': 400,
						'message': 'Error: config file could not be written to.'}
		try:
			with open(self.filepath, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=4)
			return {'status': 200,
						'message': 'Write config file complete.'}
		except:
			return {'status': 400,
						'message': 'Error: config file could not be written to.'}