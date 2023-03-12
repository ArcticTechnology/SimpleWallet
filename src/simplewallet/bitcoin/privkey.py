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

import secrets
from typing import Tuple, Union
from .helper import BitcoinMainnet, Wif, TXIN_LIST
from ..crypto.base import Base
from ..crypto.ecdsa import Ecdsa
from ..crypto.sha256 import Sha256

class Privkey:

	@classmethod
	def generate(self, compressed: bool = True) -> str:
		# Generates privkey with the python secrets module, which is designed to
		# create secure random data using synchronization methods so that no two
		# processes can replicate the same data. In accordance with ECDSA, this
		# function produces a cryptographically safe random integer k between the
		# uniformly distributed range 1 <= k < bound, with the bound being the
		# curve order. References below:
		# ECDSA Summary: https://bitcoin.stackexchange.com/a/98530
		# ECDSA Specs: https://en.bitcoin.it/wiki/Secp256k1
		# Secrets Summary: https://pynative.com/python-secrets-module/
		# Secrets Module: https://github.com/python/cpython/blob/3.6/Lib/secrets.py
		bound = Ecdsa.CURVE_ORDER
		randint = secrets.randbelow(bound - 1) + 1
		secretkey = int.to_bytes(randint, length=32, byteorder='big', signed=False)
		privkey, _ = self.serialize(secretkey, compressed)
		return privkey

	@classmethod
	def serialize(self, secretkey: bytes, compressed: bool) -> Tuple[str, bool]:
		# Serialize privkey from secretkey
		if not Ecdsa.isValid(secretkey): raise Exception('Error: Invalid secret byte.')
		secret = Ecdsa.normalize(secretkey)
		prefix = bytes([BitcoinMainnet.WIF_PREFIX])
		suffix = b'\01' if compressed else b''
		vchIn = prefix + secret + suffix
		hash = Sha256.hashd(vchIn)
		privkey = Base.encode(vchIn + hash[0:4], base=58)
		return privkey, compressed

	@classmethod
	def deserialize(self, privkey: str) -> Tuple[bytes, bool]:
		# Deserialize privkey to (secretkey, compressed)
		if self.isMinikey(privkey) == True:
			return self.minikey_to_sk(privkey), False

		try:
			vch = self._decodeBase58(privkey)
		except:
			raise Exception('Error: Failed to deserialize deformed privkey.')

		#Checking if extracted txin is allowed
		txin = self._get_txin(vch)
		if txin not in TXIN_LIST:
			raise Exception('Error: Unsupported address type.')

		if len(vch) not in [33, 34]:
			raise Exception('Error: Invalid vch, unsupported length for WIF.')

		compressed = False

		if len(vch) == 34:
			if vch[33] == 0x01:
				compressed = True
			else:
				raise Exception('Error: Invalid vch, deformed WIF.')

		if txin in Wif.SEGWIT_TYPES and not compressed:
			raise Exception('Error: Invalid vch, only compressed public keys can be used in segwit')

		raw_secret_bytes = vch[1:33]
		# Can accept secrets outside the curve order, normalize here:
		secret_bytes = Ecdsa.normalize(raw_secret_bytes)
		return secret_bytes, compressed

	@classmethod
	def _decodeBase58(self, psz: Union[bytes, str]) -> bytes:
		vchRet = Base.decode(psz, base=58)
		payload = vchRet[0:-4]
		csum_found = vchRet[-4:]
		csum_calculated = Sha256.hashd(payload)[0:4]
		if csum_calculated != csum_found:
			raise Exception('Error: Invalid checksum found when decoding privkey.')
		else:
			return payload

	@classmethod
	def _get_txin(self, vch: bytes) -> str:
		if vch[0] != BitcoinMainnet.WIF_PREFIX:
			raise Exception('Error: Invalid privkey, deformed prefix for WIF.')

		prefix = vch[0] - BitcoinMainnet.WIF_PREFIX
		try:
			return Wif.WIF_SCRIPT_TYPES_INV[prefix]
		except:
			raise Exception('Error: Invalid privkey, deformed prefix for WIF.')

	@classmethod
	def isMinikey(self, privkey: str) -> bool:
		# Minikeys is a type of p2pkh address that are typically 22 or 30
		# characters, but this routine permits any length of 20 or more
		# provided the minikey is valid. A valid minikey must begin with 
		# an 'S', be in base58, and when suffixed with '?' have its SHA256
		# hash begin with a zero byte. They are widely used in Casascius
		# physical bitcoins.
		return (len(privkey) >= 20 and privkey[0] == 'S'
			and all(ord(c) in Base.__b58chars for c in privkey)
			and Sha256.hash(privkey + '?')[0] == 0x00)

	@classmethod
	def minikey_to_sk(self, privkey: str) -> bytes:
		return Sha256.hash(privkey)