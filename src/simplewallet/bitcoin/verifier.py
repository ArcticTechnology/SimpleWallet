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
import base64
from .address import Address
from .helper import magic_hd, TXIN_LIST
from .pubkey import Pubkey
from ..utils.conversion import assert_bytes, to_bytes

class Verifier:

	@classmethod
	def reveal_address(self, signature: str, message: str, txin: str, algo=lambda x: magic_hd(x)) -> str:
		# Reveals address with message and signature
		sig65 = base64.b64decode(signature)
		msg = to_bytes(message)
		assert_bytes(msg)
		msg_hash = algo(msg)
		pubkey, compressed = Pubkey.from_signature65(sig65, msg_hash)
		pubkeybytes = pubkey.get_public_key_bytes(compressed)
		return Address.from_pubkey(pubkeybytes, txin)

	@classmethod
	def with_signature(self, address: str, signature: str, message: str, algo=lambda x: magic_hd(x)) -> dict:
		# Verify address with message and signature
		if address == '' and signature == '' and message == '':
			return {'status': 401, 'message': 'Error: Empty address, signature, and message.', 'matched': None}

		if address == '':
			return {'status': 400, 'message': 'Error: Address cannot be blank.', 'matched': None}

		if signature == '' or message == '':
			return {'status': 400, 'message': 'Error: Signature/message cannot be blank.', 'matched': None}

		try:
			for txin in TXIN_LIST:
				if address == self.reveal_address(signature, message, txin, algo):
					return {'status': 200, 'message': 'Match found, verification complete.', 'matched': True}
				else:
					pass
			else:
				return {'status': 200, 'message': 'Match NOT found, verification complete.', 'matched': False}
		except:
			return {'status': 400, 'message': 'Error: Invalid signature, verification failed.', 'matched': None}

	@classmethod
	def with_privkey(self, address: str, privkey: str) -> dict:
		# Verify address with privkey
		if address == '' and privkey == '':
			return {'status': 401, 'message': 'Error: Empty address and privkey.', 'matched': None}

		if address == '' or privkey == '':
			return {'status': 400, 'message': 'Error: Address/privkey cannot be blank.', 'matched': None}

		try:
			for txin in TXIN_LIST:
				if address == Address.from_privkey(privkey, txin):
					return {'status': 200, 'message': 'Match found, verification complete.', 'matched': True}
				else:
					pass
			else:
				return {'status': 200, 'message': 'Match NOT found, verification complete.', 'matched': False}
		except:
			return {'status': 400, 'message': 'Error: Invalid private key, verification failed.', 'matched': None}

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
