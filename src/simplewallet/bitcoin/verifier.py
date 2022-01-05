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

from .address import Address
from .helper import magic_hd, TXIN_LIST
from .pubkey import Pubkey
from ..utils.conversion import assert_bytes
from electrum.ecc import verify_message_with_address, ECPubkey
from electrum.bitcoin import pubkey_to_address

class Verifier:

	@classmethod
	def reveal_address(self, txin: str, sig65: bytes, message: bytes, algo=lambda x: magic_hd(x)) -> str:
		assert_bytes(message)
		msg_hash = algo(message)
		pubkey, _ = Pubkey.from_signature65(sig65, msg_hash)
		return Address.from_pubkey(pubkey, txin)

	@classmethod
	def verify_address(self, address: str, txin: str, sig65: bytes, message: bytes, algo=lambda x: magic_hd(x)) -> str:
		assert_bytes(message)
		msg_hash = algo(message)
		pubkey, _ = Pubkey.from_signature65(sig65, msg_hash)
		address_from_sig = Address.from_pubkey(pubkey, txin)

		if address != address_from_sig:
			return {'status': 400, 'message': 'Error: Failed to verify signature.'}

		return pubkey.verify_message_hash(sig_string=sig65[1:], msg_hash=msg_hash)

	@classmethod
	def reveal_address_electrum(self, txin: str, sig65: bytes, message: bytes, algo=lambda x: magic_hd(x)) -> str:
		if txin not in TXIN_LIST: return {'status': 400, 'message': 'Error: Unsupported txin.'}
		assert_bytes(message)
		msg_hash = algo(message)
		pubkey, _ = ECPubkey.from_signature65(sig65, msg_hash)
		pubkey_hex = pubkey.get_public_key_hex()
		return pubkey_to_address(txin, pubkey_hex)

	@classmethod
	def verify_address_electrum(self, address: str, txin: str, sig65: bytes, message: bytes, algo=lambda x: magic_hd(x)) -> str:
		if txin not in TXIN_LIST: return {'status': 400, 'message': 'Error: Unsupported txin.'}
		assert_bytes(message)
		electrum_verify = verify_message_with_address(address, sig65, message)
		if electrum_verify == True:
			return {'status': 400, 'message': 'Successfully verified signature.'}
		else:
			return {'status': 400, 'message': 'Error: Failed to verify signature.'}

	@classmethod
	def verify_sig_with_sk(self, secretkey: bytes, sig65: bytes, message: bytes, algo=lambda x: magic_hd(x)) -> dict:
		assert_bytes(message)
		h = algo(message)
		pubkey_from_sk = Pubkey.from_secretkey(secretkey)
		pubkey_from_sig, _ = Pubkey.from_signature65(sig65, h)

		if pubkey_from_sig != pubkey_from_sk:
			return {'status': 400, 'message': 'Error: Failed to verify signature.'}

		return pubkey_from_sig.verify_message_hash(sig_string=sig65[1:], msg_hash=h)

	@classmethod
	def verify_hash_with_sk(self, secretkey: bytes, sig_string: bytes, msg_hash: bytes) -> dict:
		pubkey_from_sk = Pubkey.from_secretkey(secretkey)
		return pubkey_from_sk.verify_message_hash(sig_string=sig_string, msg_hash=msg_hash)