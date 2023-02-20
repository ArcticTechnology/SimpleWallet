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
from ctypes import Array, create_string_buffer
from typing import Tuple
from libsecp256k1_0 import Secp256k1
from .helper import magic_hd
from .privkey import Privkey
from .verifier import Verifier
from ..utils.conversion import to_bytes

class Signer:

	@classmethod
	def _sig_string_from_r_and_s(self, r: int, s: int) -> bytes:
		# Gets signature from r and s
		sig_string = (int.to_bytes(r, length=32, byteorder="big") +
						int.to_bytes(s, length=32, byteorder="big"))
		sig = create_string_buffer(64)
		ret = Secp256k1._libsecp256k1.secp256k1_ecdsa_signature_parse_compact(Secp256k1._libsecp256k1.ctx, sig, sig_string)
		if not ret:
			raise Exception('Error: Deformed signature.')
		ret = Secp256k1._libsecp256k1.secp256k1_ecdsa_signature_normalize(Secp256k1._libsecp256k1.ctx, sig, sig)
		compact_signature = create_string_buffer(64)
		Secp256k1._libsecp256k1.secp256k1_ecdsa_signature_serialize_compact(Secp256k1._libsecp256k1.ctx, compact_signature, sig)
		return bytes(compact_signature)

	@classmethod
	def _sign_with_extra_entropy(self, sig: Array, secretkey: bytes, msg_hash: bytes,
								nonce_function, extra_entropy) -> Tuple[int, int]:
		# Add extra entropy to signature
		ret = Secp256k1._libsecp256k1.secp256k1_ecdsa_sign(
			Secp256k1._libsecp256k1.ctx, sig, msg_hash, secretkey,
			nonce_function, extra_entropy)
		if not ret:
			raise Exception('Error: the nonce generation function failed, or the private key was invalid')
		compact_signature = create_string_buffer(64)
		Secp256k1._libsecp256k1.secp256k1_ecdsa_signature_serialize_compact(Secp256k1._libsecp256k1.ctx, compact_signature, sig)
		r = int.from_bytes(compact_signature[:32], byteorder="big")
		s = int.from_bytes(compact_signature[32:], byteorder="big")
		return r, s

	@classmethod
	def _sign(self, secretkey: bytes, msg_hash: bytes, sigencode=None) -> bytes:
		# Create signature with secretkey and message hash.
		if not (isinstance(msg_hash, bytes) and len(msg_hash) == 32):
			raise Exception('Error: msg_hash to be signed must be bytes, and 32 bytes exactly')
		if sigencode is None:
			sigencode = self._sig_string_from_r_and_s

		sig = create_string_buffer(64)
		nonce_function=None
		extra_entropy=None
		r, s = self._sign_with_extra_entropy(sig=sig, secretkey=secretkey, msg_hash=msg_hash,
								nonce_function=nonce_function, extra_entropy=extra_entropy)

		counter = 0
		# Grind for a low r value. See link for details: https://github.com/bitcoin/bitcoin/pull/13666.
		while r >= 2**255:
			counter += 1
			extra_entropy = counter.to_bytes(32, byteorder="little")
			r, s = self._sign_with_extra_entropy(sig=sig, secretkey=secretkey, msg_hash=msg_hash,
								nonce_function=nonce_function, extra_entropy=extra_entropy)

		sig_string = self._sig_string_from_r_and_s(r, s)

		verify = Verifier.verify_hash_with_sk(secretkey=secretkey,
											sig_string=sig_string, msg_hash=msg_hash)
		if verify['status'] != 200:
			raise Exception(verify['message'])

		sig = sigencode(r, s)
		return sig

	@classmethod
	def _construct_sig65(self, sig_string: bytes, recid: int, is_compressed: bool) -> bytes:
		# Create sig65 from sig_string
		comp = 4 if is_compressed else 0
		return bytes([27 + recid + comp]) + sig_string

	@classmethod
	def _bruteforce_recid(self, secretkey: bytes, message: bytes, sig_string: bytes,
						is_compressed: bool, algo) -> Tuple[bytes, int]:
		# Bruteforce recid to create sig65
		for recid in range(4):
			sig65 = self._construct_sig65(sig_string, recid, is_compressed)
			verify = Verifier.verify_sig_with_sk(secretkey=secretkey, sig65=sig65,
													message=message, algo=algo)
			if verify['status'] == 200:
				return sig65, recid
			else:
				continue
		else:
			raise Exception('Error: Cannot sign message, no recid fits')

	@classmethod
	def _sign_message_with_sk(self, secretkey: bytes, message: str, compressed: bool, algo=lambda x: magic_hd(x)) -> bytes:
		# Sign message with secretkey
		msg_bytes = to_bytes(message, 'utf8')
		msg_hash = algo(msg_bytes)
		sig_string = self._sign(secretkey, msg_hash, sigencode=self._sig_string_from_r_and_s)
		sig65, _ = self._bruteforce_recid(secretkey, msg_bytes, sig_string, compressed, algo)
		return sig65

	@classmethod
	def sign_message(self, privkey: str, message: str, algo=lambda x: magic_hd(x)) -> dict:
		#Put sign message into Signer and change secretkey to privkey
		if privkey == '' and message == '':
			return {'status': 401, 'message': 'Error: Empty privkey and message.', 'signature': None}

		if privkey == '':
			return {'status': 400, 'message': 'Error: Privkey cannot be blank.', 'signature': None}

		if message == '':
			return {'status': 400, 'message': 'Error: Message cannot be blank.', 'signature': None}

		try:
			secretkey, compressed = Privkey.deserialize(privkey)
		except:
			return {'status': 400, 'message': 'Error: Invalid privkey, no action taken.', 'signature': None}

		try:
			raw_signature = Signer._sign_message_with_sk(secretkey, message, compressed, algo)
			signature = base64.b64encode(raw_signature).decode('ascii')
			return {'status': 200, 'message': 'Successfully created signature.', 'signature': signature}
		except:
			return {'status': 400, 'message': 'Error: Failed to create signature.', 'signature': None}
