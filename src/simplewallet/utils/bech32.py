# The following is an implementation of bech32 from
# Pieter Wuille, which is subject to the following license.
#
# Copyright (c) 2017 Pieter Wuille
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

class Bech32:

	CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

	@classmethod
	def _polymod(self, values):
		# Internal function that computes the Bech32 checksum.
		generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
		chk = 1
		for value in values:
			top = chk >> 25
			chk = (chk & 0x1ffffff) << 5 ^ value
			for i in range(5):
				chk ^= generator[i] if ((top >> i) & 1) else 0
		return chk

	@classmethod
	def _hrp_expand(self, hrp):
		# Expand the HRP into values for checksum computation.
		return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

	@classmethod
	def _create_checksum(self, hrp, data):
		# Compute the checksum values given HRP and data.
		values = self._hrp_expand(hrp) + data
		polymod = self._polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
		return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

	@classmethod
	def _verify_checksum(self, hrp, data):
		# Verify a checksum given HRP and converted data characters.
		return self._polymod(self._hrp_expand(hrp) + data) == 1

	@classmethod
	def encode(self, hrp, data):
		# Compute a Bech32 string given HRP and data values.
		combined = data + self._create_checksum(hrp, data)
		return hrp + '1' + ''.join([self.CHARSET[d] for d in combined])

	@classmethod
	def decode(self, bech, ignore_long_length=False):
		# Validate a Bech32 string, and determine HRP and data.
		if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
				(bech.lower() != bech and bech.upper() != bech)):
			return (None, None)
		bech = bech.lower()
		pos = bech.rfind('1')
		if pos < 1 or pos + 7 > len(bech) or (not ignore_long_length and len(bech) > 90):
			return (None, None)
		if not all(x in self.CHARSET for x in bech[pos+1:]):
			return (None, None)
		hrp = bech[:pos]
		data = [self.CHARSET.find(x) for x in bech[pos+1:]]
		if not self._verify_checksum(hrp, data):
			return (None, None)
		return (hrp, data[:-6])
