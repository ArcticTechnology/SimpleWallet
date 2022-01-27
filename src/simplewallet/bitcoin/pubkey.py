# The following is an implementation of the ECPubkey from
# the Electrum - lightweight Bitcoin client, which is
# subject to the following license.
# 
# Copyright (C) 2011 thomasv@gitorious
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import functools
from typing import Tuple, Optional
from ctypes import (
	byref, cast, c_char_p, c_size_t, create_string_buffer
)
from libsecp256k1_0 import Secp256k1, SECP256K1_EC_UNCOMPRESSED
from ..crypto.ecdsa import Ecdsa
from ..utils.hexxer import Hexxer
from ..utils.conversion import assert_bytes

@functools.total_ordering
class Pubkey(object):

	def __init__(self, b: Optional[bytes]):
		if b is not None:
			assert isinstance(b, (bytes, bytearray)), f'pubkey must be bytes-like, not {type(b)}'
			if isinstance(b, bytearray):
				b = bytes(b)
			self._x, self._y = self._x_and_y_from_pubkey_bytes(b)
		else:
			self._x, self._y = None, None

	def __repr__(self):
		if self.is_at_infinity():
			return f"<ECPubkey infinity>"
		return f"<ECPubkey {self.get_public_key_hex()}>"

	def __mul__(self, other: int):
		if not isinstance(other, int):
			raise TypeError('Error: multiplication not defined for pubkey and {}'.format(type(other)))

		other %= Ecdsa.CURVE_ORDER
		if self.is_at_infinity() or other == 0:
			return INFINITY
		pubkey = self._to_libsecp256k1_pubkey_ptr()

		ret = Secp256k1._libsecp256k1.secp256k1_ec_pubkey_tweak_mul(Secp256k1._libsecp256k1.ctx,
															pubkey, other.to_bytes(32, byteorder="big"))
		if not ret:
			return INFINITY
		return Pubkey._from_libsecp256k1_pubkey_ptr(pubkey)

	def __rmul__(self, other: int):
		return self * other

	def __add__(self, other):
		if not isinstance(other, Pubkey):
			raise TypeError('Error: addition not defined for pubkey and {}'.format(type(other)))
		if self.is_at_infinity(): return other
		if other.is_at_infinity(): return self

		pubkey1 = self._to_libsecp256k1_pubkey_ptr()
		pubkey2 = other._to_libsecp256k1_pubkey_ptr()
		pubkey_sum = create_string_buffer(64)

		pubkey1 = cast(pubkey1, c_char_p)
		pubkey2 = cast(pubkey2, c_char_p)
		array_of_pubkey_ptrs = (c_char_p * 2)(pubkey1, pubkey2)
		ret = Secp256k1._libsecp256k1.secp256k1_ec_pubkey_combine(Secp256k1._libsecp256k1.ctx,
																pubkey_sum, array_of_pubkey_ptrs, 2)
		if not ret:
			return INFINITY
		return Pubkey._from_libsecp256k1_pubkey_ptr(pubkey_sum)

	def __eq__(self, other) -> bool:
		if not isinstance(other, Pubkey):
			return False
		return self.point() == other.point()

	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return hash(self.point())

	def __lt__(self, other):
		if not isinstance(other, Pubkey):
			raise TypeError('Error: comparison not defined for pubkey and {}'.format(type(other)))
		return (self.x() or 0) < (other.x() or 0)

	def is_at_infinity(self):
		return self == INFINITY

	def point(self) -> Tuple[int, int]:
		return self.x(), self.y()

	def x(self) -> int:
		return self._x

	def y(self) -> int:
		return self._y

	def _x_and_y_from_pubkey_bytes(self, pubkey: bytes) -> Tuple[int, int]:
		# Uses libsecp256k1 to extract x and y from pubkey bytes
		assert isinstance(pubkey, bytes), f'Error: pubkey must be bytes, not {type(pubkey)}'
		pubkey_ptr = create_string_buffer(64)
		ret = Secp256k1._libsecp256k1.secp256k1_ec_pubkey_parse(
			Secp256k1._libsecp256k1.ctx, pubkey_ptr, pubkey, len(pubkey))
		if not ret:
			raise InvalidECPointException('Error: public key could not be parsed or is invalid')

		pubkey_serialized = create_string_buffer(65)
		pubkey_size = c_size_t(65)
		Secp256k1._libsecp256k1.secp256k1_ec_pubkey_serialize(
			Secp256k1._libsecp256k1.ctx, pubkey_serialized, byref(pubkey_size), pubkey_ptr, SECP256K1_EC_UNCOMPRESSED)
		pubkey_serialized = bytes(pubkey_serialized)
		assert pubkey_serialized[0] == 0x04, pubkey_serialized
		x = int.from_bytes(pubkey_serialized[1:33], byteorder='big', signed=False)
		y = int.from_bytes(pubkey_serialized[33:65], byteorder='big', signed=False)
		return x, y

	def _to_libsecp256k1_pubkey_ptr(self) -> 'Pubkey':
		# Uses libsecp256k1 to parse pubkey
		pubkey = create_string_buffer(64)
		public_pair_bytes = self.get_public_key_bytes(compressed=False)
		ret = Secp256k1._libsecp256k1.secp256k1_ec_pubkey_parse(
			Secp256k1._libsecp256k1.ctx, pubkey, public_pair_bytes, len(public_pair_bytes))
		if not ret:
			raise Exception('Error: public key could not be parsed or is invalid')
		return pubkey

	@classmethod
	def _from_libsecp256k1_pubkey_ptr(cls, pubkey) -> 'Pubkey':
		# Uses libsecp256k1 to deserialize pubkey
		pubkey_serialized = create_string_buffer(65)
		pubkey_size = c_size_t(65)
		Secp256k1._libsecp256k1.secp256k1_ec_pubkey_serialize(
			Secp256k1._libsecp256k1.ctx, pubkey_serialized, byref(pubkey_size), pubkey, SECP256K1_EC_UNCOMPRESSED)
		return Pubkey(bytes(pubkey_serialized))

	@classmethod
	def _from_sig_string(cls, sig_string: bytes, recid: int, msg_hash: bytes) -> 'Pubkey':
		# Extracts pubkey from sig string with recid and message hash.
		assert_bytes(sig_string)
		if len(sig_string) != 64:
			raise Exception(f'Error: wrong encoding used for signature? len={len(sig_string)} (should be 64)')
		if recid < 0 or recid > 3:
			raise ValueError('Error: recid is {}, but should be 0 <= recid <= 3'.format(recid))
		sig65 = create_string_buffer(65)
		ret = Secp256k1._libsecp256k1.secp256k1_ecdsa_recoverable_signature_parse_compact(
			Secp256k1._libsecp256k1.ctx, sig65, sig_string, recid)
		if not ret:
			raise Exception('Error: failed to parse signature')
		pubkey = create_string_buffer(64)
		ret = Secp256k1._libsecp256k1.secp256k1_ecdsa_recover(Secp256k1._libsecp256k1.ctx, pubkey, sig65, msg_hash)
		if not ret:
			raise InvalidECPointException('Error: failed to recover public key')
		return Pubkey._from_libsecp256k1_pubkey_ptr(pubkey)

	@classmethod
	def from_signature65(cls, sig: bytes, msg_hash: bytes) -> Tuple['Pubkey', bool]:
		# Extracts pubkey from sig string with message hash.
		if len(sig) != 65:
			raise Exception(f'Error: wrong encoding used for signature? len={len(sig)} (should be 65)')
		nV = sig[0]
		if nV < 27 or nV >= 35:
			raise Exception('Error: Deformed signature.')
		if nV >= 31:
			compressed = True
			nV -= 4
		else:
			compressed = False
		recid = nV - 27
		return cls._from_sig_string(sig[1:], recid, msg_hash), compressed

	@classmethod
	def from_secretkey(cls, secretkey: bytes) -> 'Pubkey':
		# Creates pubkey from secretkey
		G = Ecdsa.GENERATOR_POINT
		sk = int.from_bytes(secretkey, byteorder='big', signed=False)
		return Pubkey(G)*sk

	def get_public_key_bytes(self, compressed: bool) -> bytes:
		# Return pubkey in bytes
		if self.is_at_infinity(): raise Exception('Error: point is at infinity')
		x = int.to_bytes(self.x(), length=32, byteorder='big', signed=False)
		y = int.to_bytes(self.y(), length=32, byteorder='big', signed=False)
		if compressed:
			header = b'\x03' if self.y() & 1 else b'\x02'
			return header + x
		else:
			header = b'\x04'
			return header + x + y

	def get_public_key_hex(self, compressed: bool) -> str:
		# Return pubkey in hex
		return Hexxer.bh2u(self.get_public_key_bytes(compressed))

	def verify_message_hash(self, sig_string: bytes, msg_hash: bytes) -> dict:
		# Verify pubkey against sig string and message hash.
		assert_bytes(sig_string)
		if len(sig_string) != 64:
			return {'status': 400, 'message': f'Error: wrong encoding used for signature? len={len(sig_string)} (should be 64)'}
		if not (isinstance(msg_hash, bytes) and len(msg_hash) == 32):
			return {'status': 400, 'message': 'Error: msg_hash must be bytes, and 32 bytes exactly'}

		sig = create_string_buffer(64)
		ret = Secp256k1._libsecp256k1.secp256k1_ecdsa_signature_parse_compact(Secp256k1._libsecp256k1.ctx, sig, sig_string)
		if not ret:
			return {'status': 400, 'message': 'Error: Failed to verify signature.'}

		ret = Secp256k1._libsecp256k1.secp256k1_ecdsa_signature_normalize(Secp256k1._libsecp256k1.ctx, sig, sig)
		pubkey = self._to_libsecp256k1_pubkey_ptr()
		if 1 != Secp256k1._libsecp256k1.secp256k1_ecdsa_verify(Secp256k1._libsecp256k1.ctx, sig, msg_hash, pubkey):
			return {'status': 400, 'message': 'Error: Failed to verify signature.'}

		return {'status': 200, 'message': 'Successfully varified signature.'}

INFINITY = Pubkey(None)

class InvalidECPointException(Exception):
	"""e.g. not on curve, or infinity"""