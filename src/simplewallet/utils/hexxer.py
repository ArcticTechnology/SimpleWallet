# The following is an implementation of the hex helper
# from Electrum - lightweight Bitcoin client, which is
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

class Hexxer:

	bfh = bytes.fromhex

	@classmethod
	def bh2u(self, x: bytes) -> str:
		# str with hex representation of a bytes-like object
		# x = bytes((1, 2, 10))
		# bh2u(x)
		# '01020A'
		return x.hex()

	@classmethod
	def rev_hex(self, s: str) -> str:
		return self.bh2u(self.bfh(s)[::-1])

	@classmethod
	def int_to_hex(self, i: int, length: int=1) -> str:
		# Converts int to little-endian hex string where 
		# length is the number of bytes available
		if not isinstance(i, int):
			raise TypeError('{} instead of int'.format(i))
		range_size = pow(256, length)
		if i < -(range_size//2) or i >= range_size:
			raise OverflowError('cannot convert int {} to hex ({} bytes)'.format(i, length))
		if i < 0:
			i = range_size + i
		s = hex(i)[2:].rstrip('L')
		s = "0"*(2*length - len(s)) + s
		return self.rev_hex(s)
