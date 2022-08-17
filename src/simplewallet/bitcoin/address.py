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

from .helper import BitcoinMainnet
from .privkey import Privkey
from .pubkey import Pubkey
from ..crypto.bech32 import Bech32
from ..crypto.hash160 import Hash160
from ..utils.conversion import powbase2

class Address:

	@classmethod
	def from_privkey(self, privkey: str, txin: str, *, net=None) -> str:
		# Gets address from privkey
		if net == None: net = BitcoinMainnet
		secretkey, compressed = Privkey.deserialize(privkey)
		pubkey = Pubkey.from_secretkey(secretkey)
		pubkeybytes = pubkey.get_public_key_bytes(compressed=compressed)
		return Address.from_pubkey(pubkeybytes, txin, net=net)

	@classmethod
	def from_pubkey(self, pubkeybytes: bytes, txin: str, *, net=None) -> str:
		# Gets address from pubkey
		if net == None: net = BitcoinMainnet
		if txin == 'p2pkh':
			return P2pkh.public_key_to_p2pkh(pubkeybytes, net=net)
		elif txin == 'p2wpkh':
			return P2wpkh.public_key_to_p2wpkh(pubkeybytes, net=net)
		else:
			raise NotImplementedError(txin)

class P2pkh:

	@classmethod
	def hash160_to_p2pkh(self, h160: bytes, *, net=None) -> str:
		if net == None: net = BitcoinMainnet
		return Hash160.hash160_to_b58_address(h160, net.ADDRTYPE_P2PKH)

	@classmethod
	def public_key_to_p2pkh(self, public_key: bytes, *, net=None) -> str:
		if net == None: net = BitcoinMainnet
		return self.hash160_to_p2pkh(Hash160.hash(public_key), net=net)

class P2wpkh:

	@classmethod
	def _segwit_encode(self, hrp, witver, witprog):
		# Encode a segwit address.
		ret = Bech32.encode(hrp, [witver] + powbase2(witprog, 8, 5))
		assert self._segwit_decode(hrp, ret) != (None, None)
		return ret

	@classmethod
	def _segwit_decode(self, hrp, addr):
		# Decode a segwit address.
		if addr is None:
			return (None, None)
		hrpgot, data = Bech32.decode(addr)
		if hrpgot != hrp:
			return (None, None)
		decoded = powbase2(data[1:], 5, 8, False)
		if decoded is None or len(decoded) < 2 or len(decoded) > 40:
			return (None, None)
		if data[0] > 16:
			return (None, None)
		if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
			return (None, None)
		return (data[0], decoded)

	@classmethod
	def hash160_to_segwit_addr(self, h: bytes, witver: int, *, net=None) -> str:
		if net is None: net = BitcoinMainnet
		return self._segwit_encode(net.SEGWIT_HRP, witver, h)

	@classmethod
	def public_key_to_p2wpkh(self, public_key: bytes, *, net=None) -> str:
		if net is None: net = BitcoinMainnet
		return self.hash160_to_segwit_addr(Hash160.hash(public_key), witver=0, net=net)