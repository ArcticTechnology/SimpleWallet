# Simple Wallet
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

import os
from ..bitcoin.helper import TXIN_LIST
from ..dircrawler.crawler import Crawler
from ..utils.commoncmd import CommonCmd as cmd

class Instance:

	def __init__(self, configloader):
		self.configloader = configloader
		self.wd = None
		self.default_mode = 'p2wpkh'
		self.possible_modes = [txin for txin in TXIN_LIST]
		self.possible_modes.append('all')
		self.mode = self.default_mode
		self.load_config()

	def load_config(self):
		parser = self.configloader.parse()
		if parser['status'] != 200:
			return {'status': 400, 'message': 'Error: Failed to load config file.'}

		data = parser['data']
		try:
			wd = cmd.pwd()
			if os.path.isdir(wd) == True:
				self.wd = wd
			else:
				self.wd = None

			mode = data['mode']
			if mode in self.possible_modes:
				self.mode = mode
			else:
				self.mode = self.default_mode

			return {'status': 200, 'message': 'Load config file complete.'}
		except:
			return {'status': 400, 'message': 'Error: Failed to read config.'}

	def _update_config(self):
		wd = str(self.wd) if self.wd == None else self.wd
		data = {'wd': wd, 'mode': self.mode}
		write = self.configloader.update(data)
		self.configloader.load()
		return write

	def clear_wd(self):
		self.wd = None
		self._update_config()
		return {'status': 200, 'message': 'Working directory cleared.'}

	def set_wd(self, raw_wd: str):
		if raw_wd == '': return {'status': 400,
					'message': 'Invalid input, no action taken.'}
		wd = Crawler.posixize(raw_wd)
		if os.path.isdir(wd) == False:
			return {'status': 400, 'message': 'Invalid input, no action taken.'}
		self.wd = wd
		os.chdir(wd)
		self._update_config()
		return {'status': 200, 'message': 'Working directory set: {}'.format(wd)}

	def set_cwd_as_wd(self):
		curr_dir = cmd.pwd()
		wd = Crawler.posixize(curr_dir)
		if os.path.isdir(wd) == False:
			return {'status': 400, 'message': 'Invalid input, no action taken.'}
		self.wd = wd
		self._update_config()
		return {'status': 200, 'message': 'Working directory set: {}'.format(wd)}

	def clear_mode(self):
		self.mode = self.default_mode
		self._update_config()
		return {'status': 200, 'message': 'Address type set to default: p2wpkh.'}

	def set_mode(self, raw_mode: str):
		if raw_mode not in self.possible_modes: return {'status': 400, 'message': 'Invalid input, no action taken.'}
		self.mode = raw_mode
		self._update_config()
		return {'status': 200, 'message': 'Address type set: {}'.format(self.mode)}

