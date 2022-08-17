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

from typing import Union

class Ecdsa:

	CURVE_ORDER = 0xFFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFE_BAAEDCE6_AF48A03B_BFD25E8C_D0364141
	GENERATOR_POINT = bytes.fromhex('0479be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'
						'483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8')
	GENERATOR_POINT_COMPRESSED = bytes.fromhex('0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798')

	@classmethod
	def isValid(self, secretbytes: Union[int, bytes]) -> bool:
		if isinstance(secretbytes, bytes):
			secret = int.from_bytes(secretbytes, byteorder='big', signed=False)
		else:
			secret = secretbytes
		return 0 < secret < self.CURVE_ORDER

	@classmethod
	def normalize(self, secretbytes: bytes) -> bytes:
		string_to_number = int.from_bytes(secretbytes, byteorder='big', signed=False)
		scalar = string_to_number % self.CURVE_ORDER
		if scalar == 0:
			raise Exception('invalid EC private key scalar: zero')
		privkey_32bytes = int.to_bytes(scalar, length=32, byteorder='big', signed=False)
		return privkey_32bytes