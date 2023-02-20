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

class VerifierGui:

	def __init__(self, simplewallet, instance):
		self.simplewallet = simplewallet
		self.instance = instance

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
		print('The signature you provided is tied to the above message and address(es).')
		input(); cmd.clear(); return

	def option_2(self):
		cmd.clear()
		mode = self.instance.mode
		print('Use your private key to verify your address(es).')
		print(' ')
		privkey = getpass('Paste your private key and press [enter]: ')
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
		print('The private key you provided is tied to the above address(es).')
		input(); cmd.clear(); return

	def option_3(self):
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
		if wd == None:
			cmd.clear()
			print('No working directory set. Please set a working directory in Settings.')
			return
		if os.path.isdir(wd) == False:
			cmd.clear()
			print('Invalid working directory. Please set a valid working directory in Settings.')
			return

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