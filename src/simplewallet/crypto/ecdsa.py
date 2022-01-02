from typing import Union

class Ecdsa:

	CURVE_ORDER = 0xFFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFE_BAAEDCE6_AF48A03B_BFD25E8C_D0364141

	@classmethod
	def isValid(self, secretbyte: Union[int, bytes]) -> bool:
		if isinstance(secretbyte, bytes):
			secret = int.from_bytes(secretbyte, byteorder='big', signed=False)
		else:
			secret = secretbyte
		return 0 < secret < self.CURVE_ORDER