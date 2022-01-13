import os
from ..bitcoin.helper import TXIN_LIST
from ..dircrawler.crawler import Crawler

class Instance:

	def __init__(self, configparser):
		self.configparser = configparser
		self.wd = None
		self.default_mode = 'p2wpkh'
		self.possible_modes = [txin for txin in TXIN_LIST]
		self.possible_modes.append('all')
		self.mode = self.default_mode
		self.load_config()

	def load_config(self):
		parser = self.configparser.parse()
		if parser['status'] != 200:
			return {'status': 400, 'message': 'Error: Failed to load config file.'}

		data = parser['output']
		try:
			wd = data['wd']
			mode = data['mode']
			self.wd = wd if wd != "None" or wd != "" else None
			if mode in self.possible_modes: self.mode = mode
			return {'status': 200, 'message': 'Load config file complete.'}
		except:
			return {'status': 400, 'message': 'Error: Failed to read config.'}

	def _update_config(self):
		wd = str(self.wd) if self.wd == None else self.wd
		data = {'wd': wd, 'mode': self.mode}
		write = self.configparser.write(data)
		self.configparser.update()
		return write

	def clear_wd(self):
		self.wd = None
		self._update_config()
		return {'status': 200, 'message': 'Working directory cleared.'}

	def set_wd(self, raw_wd: str):
		if raw_wd == '': return {'status': 400,
					'message': 'Invalid input, no action taken.'}
		wd = Crawler.stdpath(raw_wd)
		if os.path.isdir(wd) == False:
			return {'status': 400, 'message': 'Invalid input, no action taken.'}
		self.wd = wd
		os.chdir(wd)
		self._update_config()
		return {'status': 200, 'message': 'Working directory set: {}'.format(wd)}

	def set_cwd_as_wd(self):
		curr_dir = os.getcwd()
		wd = Crawler.stdpath(curr_dir)
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

