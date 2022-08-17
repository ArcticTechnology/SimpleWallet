# The following is an implementation of the base encoder from
# the pywallet (https://github.com/jackjack-jj/pywallet), which
# is not subject to any license. Through Simple Wallet, this is
# subject to the following license.

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

from typing import Optional, Union
from ..utils.conversion import assert_bytes, to_bytes

class Base:

	__b58chars = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	__b43chars = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:'

	@classmethod
	def encode(self, v: bytes, *, base: int) -> str:
		# Encode v, which is a string of bytes, to base58.
		assert_bytes(v)
		if base not in (58, 43):
			raise ValueError('not supported base: {}'.format(base))
		chars = self.__b58chars
		if base == 43:
			chars = self.__b43chars
		long_value = 0
		power_of_base = 1

		# naive but slow variant: long_value += (256**i) * c
		for c in v[::-1]:
			long_value += power_of_base * c
			power_of_base <<= 8
		result = bytearray()
		while long_value >= base:
			div, mod = divmod(long_value, base)
			result.append(chars[mod])
			long_value = div
		result.append(chars[long_value])
		# Bitcoin does a little leading-zero-compression:
		# leading 0-bytes in the input become leading-1s
		nPad = 0
		for c in v:
			if c == 0x00:
				nPad += 1
			else:
				break
		result.extend([chars[0]] * nPad)
		result.reverse()
		return result.decode('ascii')

	@classmethod
	def decode(self, v: Union[bytes, str], *, base: int, length: int = None) -> Optional[bytes]:
		# decode v into a string of len bytes.
		v = to_bytes(v, 'ascii')
		if base not in (58, 43):
			raise ValueError('Error: Not supported base: {}'.format(base))
		chars = self.__b58chars
		if base == 43:
			chars = self.__b43chars
		long_value = 0
		power_of_base = 1
		for c in v[::-1]:
			digit = chars.find(bytes([c]))
			if digit == -1:
				raise Exception('Error: Forbidden character {} for base {}'.format(c, base))
			# naive but slow variant: long_value += digit * (base**i)
			long_value += digit * power_of_base
			power_of_base *= base
		result = bytearray()
		while long_value >= 256:
			div, mod = divmod(long_value, 256)
			result.append(mod)
			long_value = div
		result.append(long_value)
		nPad = 0
		for c in v:
			if c == chars[0]:
				nPad += 1
			else:
				break
		result.extend(b'\x00' * nPad)
		if length is not None and len(result) != length:
			return None
		result.reverse()
		return bytes(result)