from .bitcoin.address import Address
from .bitcoin.helper import TXIN_LIST
from .bitcoin.privkey import Privkey
from .bitcoin.signer import Signer
from .bitcoin.verifier import Verifier
from .dircrawler.instance import Instance
from .dircrawler.datamodder import DataModder
from .dircrawler.filemodder import FileModder

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
			data['address-'+mode] = []
		data['privkey'] = []

		for _ in range(num):
			privkey = Privkey.generate()
			data['privkey'].append(privkey)

			if mode == 'all':
				for txin in TXIN_LIST:
					data['address-'+txin].append(Address.from_privkey(privkey, txin))
			else:
				data['address-'+mode].append(Address.from_privkey(privkey, mode))

		outfile = FileModder.add_rtag('wallet.csv', length=5, spliton='')
		result = DataModder.createcsv(data, outfile)
		return {'status': result['status'], 'message': result['message'], 'data': None}

	def sign_message(self, privkey: str, message: str, mode: str = 'p2wpkh') -> dict:
		if mode != 'all' and mode not in TXIN_LIST:
			return {'status': 400, 'message': 'Error: Unsupported address type.', 'data': None}

		data = {'address': {}, 'signature': None}
		signature = Signer.sign_message(privkey,message)
		if mode == 'all':
			for txin in TXIN_LIST:
				verify = Verifier.reveal_address(signature,message,txin)
				data['address'][txin] = verify['address']
		else:
			verify = Verifier.reveal_address(signature,message,mode)
			data['address'][mode] = verify

		data['signature'] = signature
		return {'status': 200, 'message': 'Signing complete.', 'data': data}

	def sign_bulk(self, filepath: str, message: str = None) -> dict:
		raw_data = DataModder.parsecsv(filepath, colnames=['privkey', 'message'])
		privkeys = raw_data['privkey']

		if message == None:
			messages = raw_data['message']
			column = [Signer.sign_message(privkeys[i],messages[i]) for i, _ in enumerate(privkeys)]
		else:
			column = [Signer.sign_message(privkey,message) for privkey in privkeys]

		column.insert(0,'signature')
		outpath = FileModder.add_rtag(filepath, length=5, spliton='-s')
		return DataModder.append_col(column, filepath, outpath)

# verify_visual(data={}, mode) #1 -> reveal, 2 -> Address.from_privkey
# verify_bulk(filepath, message=None)

#### message can be 'message':[] or 'message':'hello'

# {'address':[], 'privkey':[],'signature':[], 'message':[]}

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
		#result = DataModder.createcsv(data, outfile='test.csv')
		#result = DataModder.append_col(column, filename='test.csv', outfile='test-output.csv')
		#return self.get_wallet(num = 100, mode = 'p2wpkh')
		#return self.sign_message('L5n7fimTf7VTR3JF1zopA6YDuTzNVGvLzk59kaFq1WjW6So5c4YB', 'hello world message', mode='p2wpkh')
		return self.sign_bulk('walletKG46Q.csv', message=None)

		# {'address':[], 'privkey':[],'signature':[], 'message':[]}

		#with open('testwallet.txt', 'r') as csv_file:
		#	csv_reader = csv.DictReader(csv_file)

		#	for line in csv_reader:
		#		print(line['address'])

		#return (address, privkey, signature)

#x Pull out all relevant columns
#x Update CSV with new column (how to add a column to the end of the file)
# Do calculation with the columns

