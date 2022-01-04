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

from ctypes import Array, create_string_buffer
from typing import Tuple
from .protocol import hashd_msg
from .pubkey import Pubkey
from ..crypto.secp256k1 import _libsecp256k1
from ..utils.conversion import assert_bytes, to_bytes

class Signer:

	@classmethod
	def _sig_string_from_r_and_s(self, r: int, s: int) -> bytes:
		sig_string = (int.to_bytes(r, length=32, byteorder="big") +
						int.to_bytes(s, length=32, byteorder="big"))
		sig = create_string_buffer(64)
		ret = _libsecp256k1.secp256k1_ecdsa_signature_parse_compact(_libsecp256k1.ctx, sig, sig_string)
		if not ret:
			raise Exception("Bad signature")
		ret = _libsecp256k1.secp256k1_ecdsa_signature_normalize(_libsecp256k1.ctx, sig, sig)
		compact_signature = create_string_buffer(64)
		_libsecp256k1.secp256k1_ecdsa_signature_serialize_compact(_libsecp256k1.ctx, compact_signature, sig)
		return bytes(compact_signature)

	@classmethod
	def _sign_with_extra_entropy(self, sig: Array, secretkey: bytes, msg_hash: bytes,
								nonce_function, extra_entropy) -> Tuple[int, int]:
		ret = _libsecp256k1.secp256k1_ecdsa_sign(
			_libsecp256k1.ctx, sig, msg_hash, secretkey,
			nonce_function, extra_entropy)
		if not ret:
			raise Exception('the nonce generation function failed, or the private key was invalid')
		compact_signature = create_string_buffer(64)
		_libsecp256k1.secp256k1_ecdsa_signature_serialize_compact(_libsecp256k1.ctx, compact_signature, sig)
		r = int.from_bytes(compact_signature[:32], byteorder="big")
		s = int.from_bytes(compact_signature[32:], byteorder="big")
		return r, s

	@classmethod
	def _verify_hash_with_sk(self, secretkey: bytes, sig_string: bytes, msg_hash: bytes) -> dict:
		pubkey_from_sk = Pubkey.from_secretkey(secretkey)
		return pubkey_from_sk.verify_message_hash(sig_string=sig_string, msg_hash=msg_hash)

	@classmethod
	def sign(self, secretkey: bytes, msg_hash: bytes, sigencode=None) -> bytes:
		if not (isinstance(msg_hash, bytes) and len(msg_hash) == 32):
			raise Exception('msg_hash to be signed must be bytes, and 32 bytes exactly')
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

		verify = self._verify_hash_with_sk(secretkey=secretkey, sig_string=sig_string, msg_hash=msg_hash)
		if verify['status'] != 200:
			raise Exception(verify['message'])

		sig = sigencode(r, s)
		return sig

	@classmethod
	def _construct_sig65(self, sig_string: bytes, recid: int, is_compressed: bool) -> bytes:
		comp = 4 if is_compressed else 0
		return bytes([27 + recid + comp]) + sig_string

	@classmethod
	def _verify_message_for_address(self, secretkey: bytes, sig65: bytes, message: bytes, algo=lambda x: hashd_msg(x)) -> dict:
		assert_bytes(message)
		h = algo(message)
		pubkey_from_sk = Pubkey.from_secretkey(secretkey)
		pubkey_from_sig, _ = Pubkey.from_signature65(sig65, h)

		if pubkey_from_sig != pubkey_from_sk:
			return {'status': 400, 'message': 'Error: Bad signature'}

		return pubkey_from_sig.verify_message_hash(sig_string=sig65[1:], msg_hash=h)

	@classmethod
	def _bruteforce_recid(self, secretkey: bytes, message: bytes, sig_string: bytes,
						is_compressed: bool, algo) -> Tuple[bytes, int]:
		for recid in range(4):
			sig65 = self._construct_sig65(sig_string, recid, is_compressed)
			verify = self._verify_message_for_address(secretkey=secretkey, sig65=sig65, message=message, algo=algo)
			if verify['status'] == 200:
				return sig65, recid
			else:
				continue
		else:
			raise Exception('Error: cannot sign message. no recid fits..')

	@classmethod
	def sign_message(self, secretkey: bytes, message: str, is_compressed: bool, algo=lambda x: hashd_msg(x)) -> bytes:
		msg_bytes = to_bytes(message, 'utf8')
		msg_hash = algo(msg_bytes)
		sig_string = self.sign(secretkey, msg_hash, sigencode=self._sig_string_from_r_and_s)
		sig65, _ = self._bruteforce_recid(secretkey, msg_bytes, sig_string, is_compressed, algo)
		return sig65
