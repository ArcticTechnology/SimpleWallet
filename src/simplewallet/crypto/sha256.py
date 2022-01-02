import hashlib
from typing import Union
from ..utils.type_conv import to_bytes

class Sha256:

	@classmethod
	def hash(self, x: Union[bytes, str]) -> bytes:
		x = to_bytes(x, 'utf8')
		return bytes(hashlib.sha256(x).digest())

	@classmethod
	def hashd(self, x: Union[bytes, str]) -> bytes:
		x = to_bytes(x, 'utf8')
		out = bytes(self.hash(self.hash(x)))
		return out