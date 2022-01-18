from getpass import getpass
from ..utils.commoncmd import CommonCmd as cmd

class SignerGui:

	def __init__(self, simplewallet, instance):
		self.simplewallet = simplewallet
		self.instance = instance
		# '[1] Create Signature [2] Bulk Create Signatures'

	def option_1(self):
		cmd.clear()
		mode = self.instance.mode
		print('To create a signature, you will need your private key and a message used for signing.')
		print(' ')
		privkey = getpass('Paste your PrivKey and press [enter]: ')
		if privkey == '': cmd.clear(); print('Invalid input, no action taken.'); return
		print(' ')
		message = input('Input the message: ')
		if message == '': cmd.clear(); print('Invalid input, no action taken.'); return

		signer = self.simplewallet.sign_message(privkey, message, mode)
		if signer['status'] != 200:
			cmd.clear(); print(signer['message']); return
		signature = signer['data']['signature']
		addresses = signer['data']['address']
		cmd.clear()
		print('====== Signature ======')
		print(' ')
		print(signature)
		print(' ')
		print('message: {}'.format(message))
		for txin in addresses.keys():
			print('{}: {}'.format(txin, addresses[txin]))
		print(' ')
		input(); cmd.clear(); return

	def option_2(self):
		cmd.clear()
		wd = self.instance.wd
		print('To create bulk signatures, you will need a csv file with the following:')
		print('1. A "privkey" column with all privkeys to create your signatures.')
		print('2. [Optional] A "message" column with all messages use for signing.')
		print('(If no "message" column found, you will be prompt to input a message.)')
		print(' ')
		filename = input('Input the filename: ')
		if filename == '': cmd.clear(); print('Invalid input, no action taken.'); return
		checkmsg = self.simplewallet.parse_wallet_data(filename, colnames=['message'])
		if checkmsg['status'] != 200: cmd.clear(); print(checkmsg['message']); return
		emptymsg = len(checkmsg['data']['message']) == 0
		blankmsg = set(checkmsg['data']['message']) == {''}
		if emptymsg or blankmsg:
			print(' ')
			message = input('Input the message: ')
			if message == '': cmd.clear(); print('Invalid input, no action taken.'); return
		else:
			message = None
		signer = self.simplewallet.sign_bulk(filename, message)
		cmd.clear()
		if signer['status'] == 200:
			print(signer['message'] + ' in ' + wd)
		else:
			print(signer['message'])
		return