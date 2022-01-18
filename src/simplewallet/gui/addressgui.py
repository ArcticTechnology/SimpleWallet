import os
from ..utils.commoncmd import CommonCmd as cmd

class AddressGui:

	def __init__(self, simplewallet, instance):
		self.simplewallet = simplewallet
		self.instance = instance
		# '[1] Quick Create [2] Bulk Create'

	def option_1(self):
		cmd.clear()
		mode = self.instance.mode
		wallet = self.simplewallet.get_wallet(0, mode)
		if wallet['status'] != 200:
			print(wallet['message']); return
		addresses = wallet['data']['address']
		privkey = wallet['data']['privkey']
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

	def option_2(self):
		wd = self.instance.wd
		mode = self.instance.mode
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