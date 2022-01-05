# Simple Wallet
# Copyright (c) 2022 Arctic Technology LLC

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
from .helper import BitcoinMainnet
from ..crypto.ecdsa import Ecdsa
from ..crypto.sha256 import Sha256
from ..utils.base_encoder import BaseEncoder

class PrivKey:

	def generate(self) -> str:
		# Generates privkey using python secrets module designed to generate
		# cryptographically secure random data using synchronization methods to
		# ensure that no two processes can be replicate the same data. In accordance
		# with ECDSA this function creates a random integer k between a uniformly
		# distributed range such that 1 <= k < bound, with the bound being the
		# curve order as per ECDSA. References below:
		# ECDSA Summary: https://bitcoin.stackexchange.com/a/98530
		# ECDSA Specs: https://en.bitcoin.it/wiki/Secp256k1
		# ECDSA Paper: https://www.secg.org/sec2-v2.pdf.
		# Secrets Module: https://pynative.com/python-secrets-module/
		bound = Ecdsa.CURVE_ORDER
		randint = secrets.randbelow(bound - 1) + 1
		secretkey = int.to_bytes(randint, length=32, byteorder='big', signed=False)
		return self.get_privkey(secretkey)

	@classmethod
	def get_privkey(self, secretkey: bytes, compressed: bool = False) -> str:
		# Serialize privkey from secretkey
		if not Ecdsa.isValid(secretkey): raise Exception('Error: Invalid secret byte.')
		secret = Ecdsa.normalize(secretkey)
		prefix = bytes([BitcoinMainnet.WIF_PREFIX])
		suffix = b'\01' if compressed else b''
		vchIn = prefix + secret + suffix
		hash = Sha256.hashd(vchIn)
		return BaseEncoder.encode(vchIn + hash[0:4], base=58)

	def get_secretkey(self, privkey: str) -> Tuple[bytes, bool]:
		# Deserialize privkey to (secretkey, compressed)
		if self.isMinikey(privkey) == True:
			return self.minikey_to_sk(privkey), False
		txin = None

		try:
			vch = self._decodeBase58(privkey)
		except:
			raise Exception('Error: Failed to deserialize deformed privkey.')


		#Check to see if extracted txin is allowed


		return

	def _decodeBase58(psz: Union[bytes, str]) -> bytes:
		vchRet = BaseEncoder.decode(psz, base=58)
		payload = vchRet[0:-4]
		csum_found = vchRet[-4:]
		csum_calculated = Sha256.hashd(payload)[0:4]
		if csum_calculated != csum_found:
			raise Exception('Error: Invalid checksum found when decoding privkey.')
		else:
			return payload

	def isMinikey(self, privkey: str) -> bool:
		# Minikeys is a type of p2pkh address that are typically 22 or 30
		# characters, but this routine permits any length of 20 or more
		# provided the minikey is valid. A valid minikey must begin with 
		# an 'S', be in base58, and when suffixed with '?' have its SHA256
		# hash begin with a zero byte. They are widely used in Casascius
		# physical bitcoins.
		return (len(privkey) >= 20 and privkey[0] == 'S'
			and all(ord(c) in BaseEncoder.__b58chars for c in privkey)
			and Sha256.hash(privkey + '?')[0] == 0x00)

	def minikey_to_sk(self, privkey: str) -> bytes:
		return Sha256.hash(privkey)