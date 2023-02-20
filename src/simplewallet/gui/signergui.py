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

class SignerGui:

	def __init__(self, simplewallet, instance):
		self.simplewallet = simplewallet
		self.instance = instance

	def option_1(self):
		cmd.clear()
		mode = self.instance.mode
		print('To create a signature, you will need your private key and a message used for signing.')
		print(' ')
		privkey = getpass('Paste your private key and press [enter]: ')
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
		if wd == None:
			cmd.clear()
			print('No working directory set. Please set a working directory in Settings.')
			return
		if os.path.isdir(wd) == False:
			cmd.clear()
			print('Invalid working directory. Please set a valid working directory in Settings.')
			return

		print('To create bulk signatures, you will need a csv file with the following:')
		print('1. A "privkey" column with all private keys to create your signatures.')
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