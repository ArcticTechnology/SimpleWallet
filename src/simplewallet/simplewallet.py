import secrets
from electrum.ecc import ECPubkey
from electrum.bitcoin import public_key_to_p2pkh, public_key_to_p2wpkh
from .crypto.sha256 import Sha256
from .crypto.ecdsa import Ecdsa
from .utils.base_encoder import BaseEncoder

class SimpleWallet:

	def __init__(self):
		self.txin_list = ['p2pkh','p2wpkh']

	def generate_secretbyte(self) -> bytes:
		"""
		Generates privkey using python secrets package by creating a
		random integer k between a uniformly distributed range such that
		1 <= k < bound, with the bound being the curve order as per ECDSA.
		Summary: https://bitcoin.stackexchange.com/a/98530
		Wiki: https://en.bitcoin.it/wiki/Secp256k1
		Detailed: https://www.secg.org/sec2-v2.pdf.
		"""
		bound = Ecdsa.CURVE_ORDER
		randint = secrets.randbelow(bound - 1) + 1
		return int.to_bytes(randint, length=32, byteorder='big', signed=False)

	def get_privkey(self, secretbyte: bytes) -> str:
		if not Ecdsa.isValid(secretbyte): raise Exception('Error: Invalid secret byte.')
		hash = Sha256.hashd(secretbyte)
		return BaseEncoder.enc(secretbyte + hash[0:4], base=58)

	def get_pubkeybyte(self, secretbyte: bytes) -> bytes:
		if not Ecdsa.isValid(secretbyte): raise Exception('Error: Invalid secret byte.')
		b = bytes.fromhex('0479be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'
							'483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8')
		ecpubkey = ECPubkey(b) * int.from_bytes(secretbyte, byteorder='big', signed=False)
		return ecpubkey.get_public_key_bytes(compressed=False)

	def get_address(self, pubkeybyte: bytes, txin: str, *, net=None) -> str:
		if txin == 'p2pkh':
			return public_key_to_p2pkh(pubkeybyte, net=net)
		elif txin == 'p2wpkh':
			return public_key_to_p2wpkh(pubkeybyte, net=net)
		else:
			raise NotImplementedError(txin)

	def test(self):
		secretbyte = self.generate_secretbyte()
		pubkeybyte = self.get_pubkeybyte(secretbyte)
		return self.get_address(pubkeybyte,'p2wpkh')

