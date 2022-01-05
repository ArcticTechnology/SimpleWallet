import secrets
import base64
from .bitcoin.address import Address
from .bitcoin.pubkey import Pubkey
from .bitcoin.signer import Signer
from .bitcoin.helper import BitcoinMainnet
from .bitcoin.verifier import Verifier
from .crypto.sha256 import Sha256
from .crypto.ecdsa import Ecdsa
from .utils.base_encoder import BaseEncoder
from .utils.conversion import to_bytes


class SimpleWallet:

#	def get_pubkey(self, secretkey: bytes) -> bytes:
#		if not Ecdsa.isValid(secretkey): raise Exception('Error: Invalid secret byte.')
#		ecpubkey = Pubkey.from_secretkey(secretkey)
#		return ecpubkey.get_public_key_bytes(compressed=False)

	def sign_message(self, secretkey: bytes, message: str) -> str: #Put sign message into Signer and change secretkey to privkey
		signature = Signer.sign_message_with_sk(secretkey, message, is_compressed=compressed)
		return base64.b64encode(signature).decode('ascii')

	def verify_with_sig(self, txin: str, signature: str, message: str, 
							bulk: bool = False, electrum: bool = False) -> dict:
		sig = base64.b64decode(signature)
		msg = to_bytes(message)
		if bulk == True and electrum == False:
			#address
			#Verifier.verify_address(address, txin, sig, msg)
			return {'status': 400, 'message': 'Error: This feature is still under construction.', 'data': None}

		elif bulk == True and electrum == True:
			#address
			#Verifier.verify_address_electrum(address, txin, sig, msg)
			return {'status': 400, 'message': 'Error: This feature is still under construction.', 'data': None}

		elif bulk == False and electrum == True:
			data = Verifier.reveal_address_electrum(txin, sig, msg)
			return {'status': 200, 'message': 'Verify complete.', 'data': data}

		else:
			data = Verifier.reveal_address(txin, sig, msg)
			return {'status': 200, 'message': 'Verify complete.', 'data': data}

	def verify_with_privkey(self, txin: str, signature: str, message: str, 
							bulk: bool = False, electrum: bool = False) -> dict:



	def test(self):
		message_str = 'hello world message'
		secretkey = self.generate_secretkey()
		privkey = self.get_privkey(secretkey)
		address = self.get_address(pubkey,'p2pkh')
		signature = self.sign_message(secretkey,message_str)
		return (address, privkey, signature)
		#return self.verify_message(address='bc1qpng98nyxc70n92uussjmnjdhqvs8vqrfqn5j7n',
		#			signature='G2gWQwaOwLa5xCeY+FokzBHxqk07nBVwgH+bqU+WwtMcE76O8zoIYYkhnvqiNPmTOSbN6USX2dZHllbhF5PMIkA=',
		#			message='hello world message')




