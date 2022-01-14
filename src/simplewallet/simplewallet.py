import os
from .bitcoin.address import Address
from .bitcoin.helper import TXIN_LIST
from .bitcoin.privkey import Privkey
from .bitcoin.signer import Signer
from .bitcoin.verifier import Verifier
from .dircrawler.datamodder import DataModder
from .dircrawler.filemodder import FileModder
from .utils.commoncmd import CommonCmd as cmd

class SimpleWallet:
	# Simple, secure, transparent. Simple to minimize attack surfaces. Completely open source.

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
			outfile = FileModder.add_rtag('wallet.csv', length=5, spliton='')
			result = DataModder.createcsv(data, outfile)
			return {'status': result['status'], 'message': result['message'], 'data': None}
		except:
			return {'status': 400, 'message': 'Error: Failed to write wallet to CSV file.', 'data': None}

	def sign_message(self, privkey: str, message: str, mode: str = 'p2wpkh') -> dict:
		if mode != 'all' and mode not in TXIN_LIST:
			return {'status': 400, 'message': 'Error: Unsupported address type.', 'data': None}

		data = {'address': {}, 'signature': None}

		signer = Signer.sign_message(privkey,message)
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

	def sign_bulk(self, filepath: str, message: str = None) -> dict:
		try:
			raw_data = DataModder.parsecsv(filepath, colnames=['privkey', 'message'])
			privkeys = raw_data['privkey']
			messages = raw_data['message'] if message == None else [message]
		except:
			return {'status': 400, 'message': 'Error: Unable to read file: {}'.format(filepath)}

		if len(privkeys) <= 0: return {'status': 400, 'message': 'Error: Privkey column cannot be empty.'}

		column = []
		for i, _ in enumerate(privkeys):
			signer = Signer.sign_message(privkeys[i], messages[i] if message == None else message)
			if signer['status'] == 401: column.append('')
			elif signer['status'] == 200: column.append(signer['signature'])
			else: column.append(signer['message'])

		column.insert(0,'signature')
		outpath = FileModder.add_rtag(filepath, length=5, spliton='-s')
		return DataModder.append_col(column, filepath, outpath)

	def verify_visual(self, inputdata: dict, mode: str = 'p2wpkh') -> dict:
		if mode != 'all' and mode not in TXIN_LIST:
			return {'status': 400, 'message': 'Error: Unsupported address type.', 'data': None}

		txins = TXIN_LIST if mode == 'all' else [mode]
		keys = inputdata.keys()
		data = {}

		if 'privkey' in keys:
			try:
				for txin in txins: data[txin] = Address.from_privkey(inputdata['privkey'], txin)
				return {'status': 200, 'message': 'Retrieve address complete.', 'data': data}
			except:
				return {'status': 400, 'message': 'Error: Failed to retieve address, invalid privkey.', 'data': None}

		if 'signature' not in keys or 'message' not in keys:
			return {'status': 400, 'message': 'Error: Failed to retrieve address, invalid signature or message.', 'data': None}
		else:
			signature = inputdata['signature']; message = inputdata['message']

		try:
			for txin in txins: data[txin] = Verifier.reveal_address(signature, message, txin)
			return {'status': 200, 'message': 'Retrieve address complete.', 'data': data}
		except:
			return {'status': 400, 'message': 'Error: Failed to retieve address, invalid signature or message.', 'data': None}

	def verify_bulk(self, filepath: str, method: str = 'signature', message=None):
		if method != 'signature' and method != 'privkey': {'status': 400, 'message': 'Error: Invalid verification method.'}
		try:
			raw_data = DataModder.parsecsv(filepath, colnames=['address', 'privkey', 'signature', 'message'])
			addresses = raw_data['address']
			privkeys = raw_data['privkey']
			signatures = raw_data['signature']
			messages = raw_data['message'] if message == None else [message]
		except:
			return {'status': 400, 'message': 'Error: Unable to read file {}'.format(filepath)}

		if len(addresses) <= 0: return {'status': 400, 'message': 'Error: Could not find address column.'}

		column = []
		for i, _ in enumerate(addresses):
			if method == 'signature':
				verifier = Verifier.with_signature(addresses[i], signatures[i],
								messages[i] if message == None else message)
			else:
				verifier = Verifier.with_privkey(privkeys[i], addresses[i])

			if verifier['status'] == 401: column.append('')
			elif verifier['status'] == 200: column.append(str(verifier['matched']))
			else: column.append(verifier['message'])

		column.insert(0,'verified')
		outpath = FileModder.add_rtag(filepath, length=5, spliton='-v')
		return DataModder.append_col(column, filepath, outpath)

class SimpleWalletGUI:

	def __init__(self, simplewallet, instance):
		self.simplewallet = simplewallet
		self.instance = instance

	def splashscreen(self):
		cmd.clear()
		print('Welcome to the Simple Wallet!')

	def optionscreen(self):
		print(' ')
		print('What would you like to do?')
		print('(c) Create Wallet (s) Sign (v) Verify Address (t) Transact (st) Settings (q) Quit')

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

	def option_s(self):
		print(' ')
		print('What directory do you want to set as your working directory?')
		raw_wd = input()
		cmd.clear()
		setwd = self.instance.set_wd(raw_wd)
		print(setwd['message'])
		return

	def option_st(self):
		cmd.clear()
		print('Working directory: {}'.format(self.instance.wd))
		print('[s] Set directory')
		print(' ')
		print('Default address type: {}'.format(self.instance.mode))
		print('[1] p2pkh [2] p2wpkh [3] all')
		print(' ')
		print('Change these settings or press [enter] to exit.')
		select = input()
		if select == 's':
			cmd.clear()
			self.option_s()
			return

		if select == '1': mode = 'p2pkh'
		elif select == '2': mode = 'p2wpkh'
		elif select == '3': mode = 'all'
		else:
			cmd.clear()
			print('Exited, no action taken.'); return

		cmd.clear()
		setmode = self.instance.set_mode(mode)
		print(setmode['message'])
		return

	def option_c(self):
		cmd.clear()
		print(' ')
		print('How do you want to create your wallet?')
		print('[1] Quick Create [2] Bulk Create')
		select = input()
		mode = self.instance.mode
		if select == '1':
			wallet = self.simplewallet.get_wallet(0, mode)
			if wallet['status'] != 200:
				cmd.clear(); print(wallet['message']); return
			addresses = wallet['data']['address']
			privkey = wallet['data']['privkey']
			cmd.clear()
			print('====== Wallet Details ======')
			print(' ')
			for txin in addresses.keys():
				print('{}: {}'.format(txin, addresses[txin]))
			print(' ')
			print('key: {}'.format(privkey))
			print(' ')
			print('This key was cryptographically generated via: https://en.bitcoin.it/wiki/Secp256k1.')
			print('Please copy it down, once you press [enter] it will be gone forever.')
			input(); cmd.clear(); return
		elif select == '2':
			wd = self.instance.wd
			if os.path.isdir(wd) == False or wd == None:
				cmd.clear()
				print('No working directory set. Please set working directory in Settings.')
				return
			print(' ')
			print('How many addresses would you like to create? (up to 1000)')
			try:
				number = int(input())
			except:
				cmd.clear(); print('Invalid input, no action taken.'); return
			wallet = self.simplewallet.get_wallet(number, mode)
			cmd.clear()
			if wallet['status'] == 200:
				print(wallet['message'] + ' in ' + wd)
			else:
				print(wallet['message'])
			return
		else:
			cmd.clear(); print('Invalid input, no action taken.'); return

	def run(self):
		cmd.clear()
		self.splashscreen()

		while True:
			self.optionscreen()
			select = input()

			if select not in ('pwd','ls','c','v','s','t','st','q'):
				#'(c) Create Wallet (v) Verify Address (s) Signature (t) Transact (st) Settings (q) Quit'
				cmd.clear(); print('Invalid selection. Try again.')

			if select == 'q':
				cmd.clear()
				break

			if select == 'pwd':
				self.option_pwd()

			if select == 'ls':
				self.option_ls()

			if select == 'st':
				self.option_st()

			if select == 'c':
				self.option_c()

