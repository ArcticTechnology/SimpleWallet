
def assert_bytes(*args):
	"""
	porting helper, assert args type
	"""
	try:
		for x in args:
			assert isinstance(x, (bytes, bytearray))
	except:
		raise TypeError("Failed to determine type")

def to_bytes(obj, encoding='utf8') -> bytes:
	if isinstance(obj, bytes):
		return obj
	if isinstance(obj, str):
		return obj.encode(encoding)
	elif isinstance(obj, bytearray):
		return bytes(obj)
	else:
		raise TypeError("Not a string or bytes like object")