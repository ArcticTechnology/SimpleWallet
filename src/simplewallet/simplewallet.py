from .bitcoin.address import Address
from .bitcoin.helper import TXIN_LIST
from .bitcoin.privkey import Privkey
from .bitcoin.signer import Signer
from .bitcoin.verifier import Verifier
from .dircrawler.instance import Instance
from .dircrawler.datamodder import DataModder
from .dircrawler.filemodder import FileModder
from .utils.commoncmd import CommonCmd as cmd

class SimpleWallet:
	# Simple, secure, transparent. Simple to minimize attack surfaces. Completely open source.

	def get_wallet(self, num: int = 0, mode: str = 'p2wpkh') -> dict:
		if mode != 'all' and mode not in TXIN_LIST:
			return {'status': 400, 'message': 'Error: Unsupported address type.', 'data': None}

		if num > 1000: num = 1000
		if num <= 0:
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

	def test(self):
		message = 'hello world message'
		txin = 'p2wpkh'
		privkey = Privkey.generate()
		address = Address.from_privkey(privkey, txin)
		signature = Signer.sign_message(privkey, message)
		instance = Instance()
		wd = instance.set_wd('C:/Users/username/Documents/My_Public_Repos/xSandbox')
		testwallet = 'testwallet.txt'
		testcols = ['address', 'privkey', 'signature']
		#data = DataParser.parsecsv(testwallet, testcols)
		# {'output': ['test','test2','test3']}
		#colname = 'output'
		#data = ['test1', 'test2', 'test3']
		data = {'address': ['bc1qf09trvgwx966kxn622z8zedctruh50gur7pds7',
							'bc1qz0vu62dd0feeeszhgu853xs3kp44cwv6vd998l'],
				'privkey': ['L4epCqLBx5RQ4iazoLXy5b4kYgkqw1h1LwYB5vM1e7a3uPwvLGjN',
							'L5n7fimTf7VTR3JF1zopA6YDuTzNVGvLzk59kaFq1WjW6So5c4YB','test-privkey']}
		column = ['signature','sig1','sig2']
		filepath = 'walletKG46Q-signed.csv'
		#result = DataModder.createcsv(data, outfile='test.csv')
		#result = DataModder.append_col(column, filename='test.csv', outfile='test-output.csv')
		#return self.get_wallet(num = 100, mode = 'p2wpkh')
		#return self.sign_message('L5n7fimTf7VTR3JF1zopA6YDuTzNVGvLzk59kaFq1WjW6So5c4YB', 'hello world message', mode='p2wpkh')
		#return self.sign_bulk(filepath, message=None)
		#return DataModder.parsecsv(filepath, colnames=['privkey', 'message'])
		signature = 'IFhyz0lkBNbXvQ2pasVsiIYi78XhRrQl/Hwn2yZKgxWqUNElaC5HudhzbKGxnMj4/19J7xMkUsiAGxmmX8U+pDY='
		message = 'afsdlja'
		#return self.verify_visual({'signature': signature, 'message': message }, 'all')
		return self.verify_bulk(filepath, method='signature', message=None)

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
		print('(s) Set Dir (c) Create Wallet (v) Verify Address (sg) Sign (t) Transact (o) Options (q) Quit')

	def comingsoon(self):
		cmd.clear()
		print('Feature not yet available, no action taken.')

	def option_pwd(self):
		cmd.clear()
		if self.instance.wd == None:
			print('Error: No working directory set. Please set working directory first.'); return
		else:
			print('Working directory: {}'.format(cmd.pwd())); return

	def option_ls(self):
		cmd.clear()
		if self.instance.wd == None:
			print('Error: No working directory set. Please set working directory first.'); return

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

	def run(self):
		cmd.clear()
		self.splashscreen()

		while True:
			self.optionscreen()
			select = input()

			if select not in ('pwd','ls','s','c','v','sg','t','o','q'):
				#'(s) Set Dir (c) Create Wallet (v) Verify Address (sg) Sign (t) Transact (o) Options (q) Quit'
				cmd.clear(); print('Invalid selection. Try again.')

			if select == 'q':
				cmd.clear()
				break

			if select == 'pwd':
				self.option_pwd()

			if select == 'ls':
				self.option_ls()

			if select == 's':
				self.option_s()
