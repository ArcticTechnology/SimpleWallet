import secrets
import base64
from .bitcoin.address import P2pkh, P2wpkh
from .bitcoin.pubkey import Pubkey
from .bitcoin.signer import Signer
from .bitcoin.protocol import BitcoinMainnet
from .crypto.sha256 import Sha256
from .crypto.ecdsa import Ecdsa
from .utils.base_encoder import BaseEncoder
from .utils.conversion import to_bytes
from electrum.ecc import verify_message_with_address

class SimpleWallet:

	def __init__(self):
		self.txin_list = ('p2pkh','p2wpkh')

	def generate_secretkey(self) -> bytes:
		"""Generates privkey using python secrets module designed to generate
		cryptographically secure random data using synchronization methods to
		ensure that no two processes can be replicate the same data. In accordance
		with ECDSA this function creates a random integer k between a uniformly
		distributed range such that 1 <= k < bound, with the bound being the
		curve order as per ECDSA. References below:
		ECDSA Summary: https://bitcoin.stackexchange.com/a/98530
		ECDSA Specs: https://en.bitcoin.it/wiki/Secp256k1
		ECDSA Paper: https://www.secg.org/sec2-v2.pdf.
		Secrets Module: https://pynative.com/python-secrets-module/"""
		bound = Ecdsa.CURVE_ORDER
		randint = secrets.randbelow(bound - 1) + 1
		return int.to_bytes(randint, length=32, byteorder='big', signed=False)

	def get_privkey(self, secretkey: bytes, compressed: bool = False) -> str:
		if not Ecdsa.isValid(secretkey): raise Exception('Error: Invalid secret byte.')
		secret = Ecdsa.normalize(secretkey)
		prefix = bytes([BitcoinMainnet.WIF_PREFIX])
		suffix = b'\01' if compressed else b''
		vchIn = prefix + secret + suffix
		hash = Sha256.hashd(vchIn)
		return BaseEncoder.encode(vchIn + hash[0:4], base=58)

	def get_pubkey(self, secretkey: bytes) -> bytes:
		if not Ecdsa.isValid(secretkey): raise Exception('Error: Invalid secret byte.')
		ecpubkey = Pubkey.from_secretkey(secretkey)
		return ecpubkey.get_public_key_bytes(compressed=False)

	def get_address(self, pubkey: bytes, txin: str, *, net=None) -> str:
		if txin == 'p2pkh':
			return P2pkh.public_key_to_p2pkh(pubkey, net=net)
		elif txin == 'p2wpkh':
			return P2wpkh.public_key_to_p2wpkh(pubkey, net=net)
		else:
			raise NotImplementedError(txin)

	def sign_message(self, secretkey: bytes, message: str) -> str:
		signature = Signer.sign_message(secretkey, message, is_compressed=False)
		return base64.b64encode(signature).decode('ascii')

	def verify_message(self, address, signature, message):
		sig = base64.b64decode(signature)
		msg = to_bytes(message)
		return verify_message_with_address(address, sig, msg)

	def test(self):
		message_str = 'hello world message'
		secretkey = self.generate_secretkey()
		privkey = self.get_privkey(secretkey)
		pubkey = self.get_pubkey(secretkey)
		address = self.get_address(pubkey,'p2pkh')
		signature = self.sign_message(secretkey,message_str)
		return (address, privkey, signature)
		#return self.verify_message(address='bc1qpng98nyxc70n92uussjmnjdhqvs8vqrfqn5j7n',
		#			signature='G2gWQwaOwLa5xCeY+FokzBHxqk07nBVwgH+bqU+WwtMcE76O8zoIYYkhnvqiNPmTOSbN6USX2dZHllbhF5PMIkA=',
		#			message='hello world message')




