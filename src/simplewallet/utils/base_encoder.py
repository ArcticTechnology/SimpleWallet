from .type_conv import assert_bytes

class BaseEncoder:

	__b58chars = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	__b43chars = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:'

	@classmethod
	def enc(self, v: bytes, *, base: int) -> str:
		""" encode v, which is a string of bytes, to base58."""
		assert_bytes(v)
		if base not in (58, 43):
			raise ValueError('not supported base: {}'.format(base))
		chars = self.__b58chars
		if base == 43:
			chars = self.__b43chars
		long_value = 0
		power_of_base = 1
		for c in v[::-1]:
			# naive but slow variant: long_value += (256**i) * c
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