#!/usr/bin/python3 -B
from simplewallet import *

def test_create_wallet():
	message = 'hello world message'
	txin = 'p2wpkh'
	privkey = Privkey.generate()
	address = Address.from_privkey(privkey, txin)
	signature = Signer.sign_message(privkey, message)
	return (address, privkey, signature)
	# Creates a new address, privkey, signature

def test_reveal_address():
	signature = 'IHvpYON7xWJt2DTTp53RUErb7TE3EBhoQzDo2m0yv5FdV+z3cDDGJ7kEDGVLc1dy0d8akq5P4tvl4y0hUEl4ZSU='
	message = 'hello world message'
	txin = 'p2wpkh'
	return Verifier.reveal_address_data(signature, message, txin)
	# {'address': 'bc1qkq0kv6krh56dv37g45mgz7dkfau94wss8cw39n', 'status': 200, 'message': 'Successfully varified signature.'}

def test_verify_address():
	address = 'bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn'
	signature = 'IHvpYON7xWJt2DTTp53RUErb7TE3EBhoQzDo2m0yv5FdV+z3cDDGJ7kEDGVLc1dy0d8akq5P4tvl4y0hUEl4ZSU='
	message = 'hello world message'
	return Verifier.verify_address(address, signature, message)
	# 'status': 200, 'message': 'Successfully varified signature.', 'match': {'p2pkh': False, 'p2wpkh': True}}

def test_get_address():
	privkey = 'L5HhPdapxP847zRPh7VsqqVtncW7VwyXGZXSohZg42QE69CxrLn5'
	txin = 'p2wpkh'
	return Address.from_privkey(privkey, txin)
	# bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn

def test_match_privkey():
	privkey = 'L5HhPdapxP847zRPh7VsqqVtncW7VwyXGZXSohZg42QE69CxrLn5'
	address = 'bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn'
	return Verifier.match_privkey(privkey, address)
	# {'status': 200, 'message': 'Successfully matched address to privkey.', 'match': {'p2pkh': False, 'p2wpkh': True}}

if __name__ == '__main__':
	#test = test_create_wallet()
	#test = test_reveal_address()
	#test = test_verify_address()
	test = test_get_address()
	#test = test_match_privkey()
	raise SystemExit(test)

### Test Addresses (DO NOT USE TO STORE BITCOIN!!!) ###
# ('1EgQPcb8pyKCasGYW7tPzmTXEyp2uEGbGF', 'L5YggYAVHYtECWx8gWFPTs9we1VqFBjpexwWMdNyYLow7omhcCgZ', 'IG/7jZpMRGwcsVGBW9Gi/ccThA0c705YqaMrQKrgV8rLKcV86qZljGljGIXj4G0bLWJwbPZxuxCh1qUXiDjRAn8=')
# ('1H4FYUfj7Z8Nj9dg82M4n594J1R1h3G5Vn', 'L1KpGvKzEdWFdogJ6yje9UM1gCmFJT5x2ZQqFTQhA33sBSiQk2hT', 'IGA0+UZ1urDdRdf/cOzZHrjaOfJrOY0lDqQ+EZbM8NKUNq46yB2oSxjOLjAfBUIDV43RdZKKk4ipI2sp2H/saq0=')
# ('bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn', 'L5HhPdapxP847zRPh7VsqqVtncW7VwyXGZXSohZg42QE69CxrLn5', 'IHvpYON7xWJt2DTTp53RUErb7TE3EBhoQzDo2m0yv5FdV+z3cDDGJ7kEDGVLc1dy0d8akq5P4tvl4y0hUEl4ZSU=')
# ('bc1qvkuuatw6zsqhtx4md0y2mvyye45x828rp6p73a', 'Ky3AiSn56PoTBLhBwqFbpJTtP35fSjh1ecrPEdUp3bdAKs8kZJKC', 'H3AW3q8xR6F+Y9NH2slXhDjPcpm9M97bb/ZZCGY2BT18GAQOTpLhTF1FusM0PM8Xgx2JQMFTyvMpGCREk9RT72s=')



		#address = '1H4FYUfj7Z8Nj9dg82M4n594J1R1h3G5Vn'
		#signature='IGA0+UZ1urDdRdf/cOzZHrjaOfJrOY0lDqQ+EZbM8NKUNq46yB2oSxjOLjAfBUIDV43RdZKKk4ipI2sp2H/saq0='
		#address_data = Verifier.reveal_address_data(signature, message, txin)
		# verify = Verifier.verify_address(address, signature, message)
		#match = Verifier.match_address('L1KpGvKzEdWFdogJ6yje9UM1gCmFJT5x2ZQqFTQhA33sBSiQk2hT', address)
		#return match
