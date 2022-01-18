from getpass import getpass
from ..utils.commoncmd import CommonCmd as cmd

class VerifierGui:

	def __init__(self, simplewallet, instance):
		self.simplewallet = simplewallet
		self.instance = instance
		# '[1] Signature [2] PrivKey [3] Bulk Signatures [4] Bulk PrivKeys'

	def option_1(self):
		cmd.clear()
		mode = self.instance.mode
		print('Use your signature and message to verify your address(es).')
		print(' ')
		signature = input('Input your signature: ')
		if signature == '': cmd.clear(); print('Invalid input, no action taken.'); return
		print(' ')
		message = input('Input the message: ')
		if message == '': cmd.clear(); print('Invalid input, no action taken.'); return
		print(' ')
		instructions = {'signature': signature, 'message': message}
		verifier = self.simplewallet.verify_visual(instructions, mode)
		if verifier['status'] != 200: cmd.clear(); print(verifier['message']); return
		addresses = verifier['data']
		cmd.clear()
		print('====== Visual Verification ======')
		print(' ')
		print('message: {}'.format(message))
		for txin in addresses.keys():
			print('{}: {}'.format(txin, addresses[txin]))
		print(' ')
		print('Verify that your message and address(es) match the above.')
		input(); cmd.clear(); return

	def option_2(self):
		cmd.clear()
		mode = self.instance.mode
		print('Use your private key to verify your address(es).')
		print(' ')
		privkey = getpass('Paste your PrivKey and press [enter]: ')
		if privkey == '': cmd.clear(); print('Invalid input, no action taken.'); return
		print(' ')
		instructions = {'privkey': privkey}
		verifier = self.simplewallet.verify_visual(instructions, mode)
		if verifier['status'] != 200: cmd.clear(); print(verifier['message']); return
		addresses = verifier['data']
		cmd.clear()
		print('====== Visual Verification ======')
		print(' ')
		for txin in addresses.keys():
			print('{}: {}'.format(txin, addresses[txin]))
		print(' ')
		print('Verify that your address(es) match the above.')
		input(); cmd.clear(); return

	def option_3(self):
		cmd.clear()
		wd = self.instance.wd
		print('To bulk verify addresses, you will need a csv file with the following:')
		print('1. An "address" column of all the addresses you want to verify.')
		print('2. A "signature" column with the signatures of those addresses.')
		print('3. [Optional] A "message" column with the messages used in signing.')
		print('(If no "message" column found, you will be prompt to input the message.)')
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
		verifier = self.simplewallet.verify_bulk(filename, method='signature', message=message)
		cmd.clear()
		if verifier['status'] == 200:
			print(verifier['message'] + ' in ' + wd)
		else:
			print(verifier['message'])
		return

	def option_4(self):
		cmd.clear()
		wd = self.instance.wd
		print('To bulk verify addresses, you will need a csv file with the following:')
		print('1. An "address" column of all the addresses you want to verify.')
		print('2. A "privkey" column with the private keys of those addresses.')
		print(' ')
		filename = input('Input the filename: ')
		if filename == '': cmd.clear(); print('Invalid input, no action taken.'); return
		verifier = self.simplewallet.verify_bulk(filename, method='privkey')
		cmd.clear()
		if verifier['status'] == 200:
			print(verifier['message'] + ' in ' + wd)
		else:
			print(verifier['message'])
		return