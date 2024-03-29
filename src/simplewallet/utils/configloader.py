# Config Loader (No Encryption)
# Copyright (c) 2023 Arctic Technology

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
from os import stat
from os.path import dirname, exists
from ..dircrawler.crawler import Crawler
from ..dircrawler.filemodder import FileModder

class ConfigLoader:

	def __init__(self):
		self.build_loc = 'simplewallet/config'
		self.dev_loc = 'config'
		self.possible_names = ['config.json']

		self.rootpath = ''
		self.env = ''
		self.configloc = ''
		self.configfile = ''
		self.load()

	def _get_rootpath(self) -> str:
		return Crawler.posixize(dirname(dirname(__file__)))

	def _get_env(self) -> str:
		if self.rootpath == '': return ''
		folder = Crawler.get_basename(dirname(self.rootpath))
		if folder == 'site-packages':
			return 'build'
		elif folder == 'src':
			return 'dev'
		else:
			return ''

	def _get_configloc(self) -> str:
		if self.env == 'build':
			return Crawler.joinpath(dirname(dirname(dirname(dirname(self.rootpath)))),
					self.build_loc)
		elif self.env == 'dev':
			return Crawler.joinpath(dirname(dirname(self.rootpath)),
					self.dev_loc)
		else:
			return ''

	def _get_configfile(self, filename: str) -> str:
		if self.configloc == '': return ''
		return Crawler.joinpath(self.configloc, filename)

	def _find(self) -> dict:
		self.rootpath = self._get_rootpath()
		self.env = self._get_env()
		self.configloc = self._get_configloc()

		for filename in self.possible_names:
			self.configfile = self._get_configfile(filename)
			if exists(self.configfile):
				return {'status': 200, 'message': 'Config file found.'}

		return {'status': 400, 'message': 'Warning: Config file not found.'}

	def hasContent(self) -> bool:
		if exists(self.configfile) == False: return False
		if stat(self.configfile).st_size > 0:
			return True
		else:
			return False

	def load(self) -> dict:
		find = self._find()
		if find['status'] == 400:
			return {'status': 400,
					'message': find['message']}
		if self.hasContent():
			return {'status': 200,
					'message': 'Config file successfully loaded.'}
		else:
			return {'status': 400,
					'message': 'Warning: Config file is empty.'}

	def parse(self) -> dict:
		try:
			content = ''.join(FileModder.read_file(self.configfile))
		except:
			return {'status': 400,
						'message': 'Error: config file could not be read.', 'data': None}

		try:
			result = json.loads(content)
			return {'status': 200, 'message': 'Read config file complete.',
					'data': result}
		except:
			return {'status': 400,
				'message': 'Error: Failed to read config, invalid Json format.',
				'data': None}

	def update(self, data):
		if self.configfile == '':
			return {'status': 400,
						'message': 'Error: config file could not be written to.'}
		try:
			with open(self.configfile, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=4)
			return {'status': 200,
						'message': 'Update config file complete.'}
		except:
			return {'status': 400,
						'message': 'Error: config file could not be written to.'}