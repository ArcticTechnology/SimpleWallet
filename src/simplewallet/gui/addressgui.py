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
from getpass import getpass
from ..utils.commoncmd import CommonCmd as cmd

class AddressGui:

	def __init__(self, simplewallet, instance):
		self.simplewallet = simplewallet
		self.instance = instance

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
		if wd == None:
			cmd.clear()
			print('No working directory set. Please set a working directory in Settings.')
			return
		if os.path.isdir(wd) == False:
			cmd.clear()
			print('Invalid working directory. Please set a valid working directory in Settings.')
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

	def option_3(self):
		cmd.clear()
		mode = self.instance.mode
		print('Use your private key to get your address(es).')
		print(' ')
		privkey = getpass('Paste your private key and press [enter]: ')
		if privkey == '': cmd.clear(); print('Invalid input, no action taken.'); return
		print(' ')
		instructions = {'privkey': privkey}
		verifier = self.simplewallet.verify_visual(instructions, mode)
		if verifier['status'] != 200: cmd.clear(); print(verifier['message']); return
		addresses = verifier['data']
		cmd.clear()
		print('====== Address Details ======')
		print(' ')
		for txin in addresses.keys():
			print('{}: {}'.format(txin, addresses[txin]))
		print(' ')
		print('The private key you provided is tied to the above address(es).')
		input(); cmd.clear(); return