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

from .bitcoin.address import Address
from .bitcoin.helper import TXIN_LIST
from .bitcoin.privkey import Privkey
from .bitcoin.signer import Signer
from .bitcoin.verifier import Verifier
from .dircrawler.datamodder import DataModder
from .dircrawler.filemodder import FileModder
from .utils.commoncmd import CommonCmd as cmd

class SimpleWallet:

	def get_wallet(self, num: int = 0, mode: str = 'p2wpkh') -> dict:
		if mode != 'all' and mode not in TXIN_LIST:
			return {'status': 400, 'message': 'Error: Unsupported address type.', 'data': None}

		if num < 0: num = 1
		if num > 1000: num = 1000
		if num == 0:
			privkey = Privkey.generate()
			address = {}
			if mode == 'all':
				for txin in TXIN_LIST:
					address[txin] = Address.from_privkey(privkey, txin)
			else:
				address[mode] = Address.from_privkey(privkey, mode)

			data = {'address': address, 'privkey': privkey}
			return {'status': 200, 'message': 'Generate address complete.', 'data': data}

		data = {}
		if mode == 'all':
			for txin in TXIN_LIST: data['address-'+txin] = []
		else:
			data['address'] = []
		data['privkey'] = []

		for _ in range(num):
			privkey = Privkey.generate()
			data['privkey'].append(privkey)

			if mode == 'all':
				for txin in TXIN_LIST:
					data['address-'+txin].append(Address.from_privkey(privkey, txin))
			else:
				data['address'].append(Address.from_privkey(privkey, mode))

		try:
			outfile = FileModder.add_randomized_tag('wallet.csv', length=5, spliton='')
			result = DataModder.createcsv(data, outfile)
			return {'status': result['status'], 'message': result['message'], 'data': None}
		except:
			return {'status': 400, 'message': 'Error: Failed to write wallet to CSV file.', 'data': None}

	def sign_message(self, privkey: str, message: str, mode: str) -> dict:
		if mode != 'all' and mode not in TXIN_LIST:
			return {'status': 400, 'message': 'Error: Unsupported address type.', 'data': None}

		data = {'address': {}, 'signature': None}

		signer = Signer.sign_message(privkey, message)
		if signer['status'] != 200:
			return {'status': signer['status'], 'message': signer['message'], 'data': None}

		data['signature'] = signer['signature']
		txins = TXIN_LIST if mode == 'all' else [mode]

		try:
			for txin in txins:
				address = Verifier.reveal_address(data['signature'], message, txin)
				data['address'][txin] = address
			return {'status': 200, 'message': 'Signing complete.', 'data': data}
		except:
			return {'status': 400, 'message': 'Error: Created corrupt signature.', 'data': None}

	def parse_wallet_data(self, filepath: str, colnames: list) -> dict:
		try:
			data = DataModder.parsecsv(filepath, colnames)
			if bool(data) == True:
				return {'status': 200, 'message': 'Read file complete {}'.format(filepath), 'data': data}
			else:
				return {'status': 400, 'message': 'Error: Failed to read file.', 'data': None}
		except:
			return {'status': 400, 'message': 'Error: Unable to read file {}'.format(filepath), 'data': None}

	def sign_bulk(self, filepath: str, message: str = None) -> dict:
		parser = self.parse_wallet_data(filepath, colnames=['privkey', 'message'])
		if parser['status'] != 200: return {'status': 400, 'message': parser['message']}
		privkeys = parser['data']['privkey']
		messages = parser['data']['message']

		if len(privkeys) == 0: return {'status': 400, 'message': 'Error: privkey column missing or empty.'}
		if len(messages) == 0 and message == None: return {'status': 400, 'message': 'Error: Message missing or empty.'}
		if len(privkeys) != len(messages) and message == None:
			return {'status': 400, 'message': 'Error: Number of private keys and messages must be the same.'}

		column = []
		for i, _ in enumerate(privkeys):
			signer = Signer.sign_message(privkeys[i], messages[i] if message == None else message)
			if signer['status'] == 401: column.append('')
			elif signer['status'] == 200: column.append(signer['signature'])
			else: column.append(signer['message'])

		column.insert(0,'signature')
		outpath = FileModder.add_randomized_tag(filepath, length=5, spliton='-s')
		return DataModder.append_col(column, filepath, outpath)

	def verify_visual(self, instructions: dict, mode: str) -> dict:
		if mode != 'all' and mode not in TXIN_LIST:
			return {'status': 400, 'message': 'Error: Unsupported address type.', 'data': None}

		txins = TXIN_LIST if mode == 'all' else [mode]
		keys = instructions.keys()
		data = {}

		if 'privkey' in keys:
			try:
				for txin in txins: data[txin] = Address.from_privkey(instructions['privkey'], txin)
				return {'status': 200, 'message': 'Retrieve address complete.', 'data': data}
			except:
				return {'status': 400, 'message': 'Error: Failed to retieve address, invalid private key.', 'data': None}

		if 'signature' not in keys or 'message' not in keys:
			return {'status': 400, 'message': 'Error: Signature or message missing from input.', 'data': None}
		else:
			signature = instructions['signature']; message = instructions['message']

		try:
			for txin in txins: data[txin] = Verifier.reveal_address(signature, message, txin)
			return {'status': 200, 'message': 'Retrieve address complete.', 'data': data}
		except:
			return {'status': 400, 'message': 'Error: Failed to retieve address, invalid signature.', 'data': None}

	def verify_bulk(self, filepath: str, method: str = 'signature', message: str = None):
		if method != 'signature' and method != 'privkey': return {'status': 400, 'message': 'Error: Invalid verification method.'}
		parser = self.parse_wallet_data(filepath, colnames=['address', 'privkey', 'signature', 'message'])
		if parser['status'] != 200: return {'status': 400, 'message': parser['message']}
		addresses = parser['data']['address']
		privkeys = parser['data']['privkey']
		signatures = parser['data']['signature']
		messages = parser['data']['message']

		if len(addresses) == 0: return {'status': 400, 'message': 'Error: Address column missing or empty.'}

		if method == 'signature':
			if len(signatures) == 0: return {'status': 400, 'message': 'Error: Signature column missing or empty.'}
			if len(messages) == 0 and message == None: return {'status': 400, 'message': 'Error: Message missing or empty.'}
			if len(addresses) != len(signatures):
				return {'status': 400, 'message': 'Error: Number of addresses and signatures must be the same.'}
			if len(signatures) != len(messages) and message == None:
				return {'status': 400, 'message': 'Error: Number of signatures and messages must be the same.'}

		if method == 'privkey':
			if len(privkeys) == 0: return {'status': 400, 'message': 'Error: privkey column missing or empty.'}
			if len(addresses) != len(privkeys):
				return {'status': 400, 'message': 'Error: Number of addresses and private keys must be the same.'}

		column = []
		for i, _ in enumerate(addresses):
			if method == 'signature':
				verifier = Verifier.with_signature(addresses[i], signatures[i],
													messages[i] if message == None else message)
			else:
				verifier = Verifier.with_privkey(addresses[i], privkeys[i])

			if verifier['status'] == 401: column.append('')
			elif verifier['status'] == 200: column.append(str(verifier['matched']))
			else: column.append(verifier['message'])

		column.insert(0,'verified-{}'.format(method))
		outpath = FileModder.add_randomized_tag(filepath, length=5, spliton='-v')
		return DataModder.append_col(column, filepath, outpath)

class SimpleWalletGUI:

	def __init__(self, simplewallet, instance, addressgui, signergui, verifiergui):
		self.simplewallet = simplewallet
		self.instance = instance
		self.addressgui = addressgui
		self.signergui = signergui
		self.verifiergui = verifiergui

	def splashscreen(self):
		cmd.clear()
		print('Welcome to the Simple Wallet!')

	def optionscreen(self):
		print(' ')
		print('What would you like to do?')
		print('(w) Wallet, (s) Signature, (v) Verify, (i) Settings, (q) Quit')

	def comingsoon(self):
		cmd.clear()
		print('Feature not yet available, no action taken.')

	def option_pwd(self):
		cmd.clear()
		if self.instance.wd == None:
			print('No working directory set. Please set working directory in Settings.'); return
		else:
			print('Working directory: {}'.format(cmd.pwd())); return

	def option_ls(self):
		cmd.clear()
		if self.instance.wd == None:
			print('No working directory set. Please set working directory in Settings.'); return

		ls = cmd.ls()

		if len(ls) == 0:
			print('Working directory is empty.'); return
		else:
			print(' '.join(ls)); return

	def option_i(self):
		cmd.clear()
		print('Working directory: {}'.format(self.instance.wd))
		print('[s] Set directory')
		print(' ')
		print('Address type: {}'.format(self.instance.mode))
		print('[1] p2pkh [2] p2wpkh [3] all')
		print(' ')
		print('You may change the above settings or press [enter] to exit.')
		select = input()
		if select == 's':
			cmd.clear()
			print(' ')
			print('What directory do you want to set as your working directory?')
			raw_wd = input()
			cmd.clear()
			setwd = self.instance.set_wd(raw_wd)
			print(setwd['message'])
			return

		cmd.clear()
		if select == '1': mode = 'p2pkh'
		elif select == '2': mode = 'p2wpkh'
		elif select == '3': mode = 'all'
		else:
			print('Exited, no action taken.'); return

		setmode = self.instance.set_mode(mode)
		print(setmode['message'])
		return

	def option_w(self):
		cmd.clear()
		print(' ')
		print('How do you want to create your wallet?')
		print('[1] Single [2] Bulk [3] Use Private Key')
		select = input()
		if select == '1': self.addressgui.option_1(); return
		elif select == '2': self.addressgui.option_2(); return
		elif select == '3': self.addressgui.option_3(); return
		else:
			cmd.clear(); print('Invalid input, no action taken.'); return

	def option_s(self):
		cmd.clear()
		print(' ')
		print('How do you want to create your signature?')
		print('[1] Single [2] Bulk')
		select = input()
		if select == '1': self.signergui.option_1(); return
		if select == '2': self.signergui.option_2(); return
		else:
			cmd.clear(); print('Invalid input, no action taken.'); return

	def option_v(self):
		cmd.clear()
		print(' ')
		print('How do you want to verify your addresses?')
		print('[1] Signature [2] Private Key [3] Bulk Signatures [4] Bulk Private Keys')
		select = input()
		if select == '1': self.verifiergui.option_1(); return
		elif select == '2': self.verifiergui.option_2(); return
		elif select == '3': self.verifiergui.option_3(); return
		elif select == '4': self.verifiergui.option_4(); return
		else:
			cmd.clear(); print('Invalid input, no action taken.'); return

	def run(self):
		self.splashscreen()

		while True:
			self.optionscreen()
			select = input()

			if select not in ('pwd','ls','w','s','v','i','q'):
				#'(w) Wallet, (s) Signature, (v) Verify, (i) Settings, (q) Quit'
				cmd.clear(); print('Invalid selection. Try again.')

			if select == 'pwd':
				self.option_pwd()

			if select == 'ls':
				self.option_ls()

			if select == 'w':
				self.option_w()

			if select == 's':
				self.option_s()

			if select == 'v':
				self.option_v()

			if select == 'i':
				self.option_i()

			if select == 'q':
				cmd.clear()
				break