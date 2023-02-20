#!/usr/bin/python3 -B
from simplewallet import *

class UnitTest:

	def _check(self, test_condition, result, expected_data):
		if 'status' in result:
			if result['status'] != expected_data['status']:
				return {'status': 400,
						'message': 'FAILED: {}.'.format(test_condition)}

		if result['result'] == expected_data['result']:
			return {'status': 200,
					'message': 'PASSED: {}.'.format(test_condition)}
		else:
			return {'status': 400,
					'message': 'FAILED: {}.'.format(test_condition)}

	def test_condition_1(self):
		test_condition = 'Privkey.generate()'
		expected_data = {'status': 200, 'message': 'Match found, verification complete.',
						'matched': True}
		expected_result = {'status': expected_data['status'], 'result': expected_data['matched']}

		txin = 'p2wpkh'
		privkey = Privkey.generate()
		address = Address.from_privkey(privkey, txin)
		verify = Verifier.with_privkey(address, privkey)
		result = {'status': verify['status'], 'result': verify['matched']}
		return self._check(test_condition, result, expected_result)

	def test_condition_2(self):
		test_condition = 'Address.from_privkey()'
		expected_data = 'bc1qfyp2t96wgekalv30y8w9pnzhcq7rr8k5409zq9'
		expected_result = {'result': expected_data}

		privkey = 'KxL45a866ZnetmhpU2oBQbVv7ZwnJBsBCEMMWusfb24YdvKYFbBJ'
		txin = 'p2wpkh'
		address = Address.from_privkey(privkey, txin)
		result = {'result': address}
		return self._check(test_condition, result, expected_result)

	def test_condition_3(self):
		test_condition = 'Signer.sign_message()'
		expected_data = {'status': 200, 'message': 'Successfully created signature.',
						'signature': 'IHvpYON7xWJt2DTTp53RUErb7TE3EBhoQzDo2m0yv5FdV+z3cDDGJ7kEDGVLc1dy0d8akq5P4tvl4y0hUEl4ZSU='}
		expected_result = {'status': expected_data['status'], 'result': expected_data['message']}

		privkey = 'KxL45a866ZnetmhpU2oBQbVv7ZwnJBsBCEMMWusfb24YdvKYFbBJ'
		message = 'hello world message'
		sign = Signer.sign_message(privkey, message)
		result = {'status': sign['status'], 'result': sign['message']}
		return self._check(test_condition, result, expected_result)

	def test_condition_4(self):
		test_condition = 'Verifier.reveal_address()'
		expected_data = 'bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn'
		expected_result = {'result': expected_data}

		signature = 'IHvpYON7xWJt2DTTp53RUErb7TE3EBhoQzDo2m0yv5FdV+z3cDDGJ7kEDGVLc1dy0d8akq5P4tvl4y0hUEl4ZSU='
		message = 'hello world message'
		txin = 'p2wpkh'
		reveal = Verifier.reveal_address(signature, message, txin)
		result = {'result': reveal}
		return self._check(test_condition, result, expected_result)

	def test_condition_5(self):
		test_condition = 'Verifier.with_signature()'
		expected_data = {'status': 200, 'message': 'Match found, verification complete.', 'matched': True}
		expected_result = {'status': expected_data['status'], 'result': expected_data['matched']}

		address = 'bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn'
		signature = 'IHvpYON7xWJt2DTTp53RUErb7TE3EBhoQzDo2m0yv5FdV+z3cDDGJ7kEDGVLc1dy0d8akq5P4tvl4y0hUEl4ZSU='
		message = 'hello world message'
		verify = Verifier.with_signature(address, signature, message)
		result = {'status': verify['status'], 'result': verify['matched']}
		return self._check(test_condition, result, expected_result)

	def test_condition_6(self):
		test_condition = 'Verifier.with_privkey()'
		expected_data = {'status': 200, 'message': 'Match found, verification complete.', 'matched': True}
		expected_result = {'status': expected_data['status'], 'result': expected_data['matched']}

		address = 'bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn'
		privkey = 'L5HhPdapxP847zRPh7VsqqVtncW7VwyXGZXSohZg42QE69CxrLn5'
		verify = Verifier.with_privkey(address, privkey)
		result = {'status': verify['status'], 'result': verify['matched']}
		return self._check(test_condition, result, expected_result)

	def _test(self, test_condition):
		if test_condition == 'test_condition_1':
			return self.test_condition_1()
		elif test_condition == 'test_condition_2':
			return self.test_condition_2()
		elif test_condition == 'test_condition_3':
			return self.test_condition_3()
		elif test_condition == 'test_condition_4':
			return self.test_condition_4()
		elif test_condition == 'test_condition_5':
			return self.test_condition_5()
		elif test_condition == 'test_condition_6':
			return self.test_condition_6()
		else:
			raise ValueError('Error: invalid test_condition: {}'.format(test_condition))

	def test(self):
		print('Unit test started...')
		test_conditions = [
			'test_condition_1',
			'test_condition_2',
			'test_condition_3',
			'test_condition_4',
			'test_condition_5',
			'test_condition_6']

		for test_condition in test_conditions:
			unit_test = self._test(test_condition)
			print(test_condition + ' ' + unit_test['message'])
			if unit_test['status'] != 200: break

		print('Unit test complete.')
		return

if __name__ == "__main__":
	test = UnitTest()
	raise SystemExit(test.test())

#===== More Test Addresses (DO NOT USE TO STORE BITCOIN!!!) =====
# ('1EgQPcb8pyKCasGYW7tPzmTXEyp2uEGbGF', 'L5YggYAVHYtECWx8gWFPTs9we1VqFBjpexwWMdNyYLow7omhcCgZ', 'IG/7jZpMRGwcsVGBW9Gi/ccThA0c705YqaMrQKrgV8rLKcV86qZljGljGIXj4G0bLWJwbPZxuxCh1qUXiDjRAn8=')
# ('1H4FYUfj7Z8Nj9dg82M4n594J1R1h3G5Vn', 'L1KpGvKzEdWFdogJ6yje9UM1gCmFJT5x2ZQqFTQhA33sBSiQk2hT', 'IGA0+UZ1urDdRdf/cOzZHrjaOfJrOY0lDqQ+EZbM8NKUNq46yB2oSxjOLjAfBUIDV43RdZKKk4ipI2sp2H/saq0=')
# ('bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn', 'L5HhPdapxP847zRPh7VsqqVtncW7VwyXGZXSohZg42QE69CxrLn5', 'IHvpYON7xWJt2DTTp53RUErb7TE3EBhoQzDo2m0yv5FdV+z3cDDGJ7kEDGVLc1dy0d8akq5P4tvl4y0hUEl4ZSU=')
# ('bc1qvkuuatw6zsqhtx4md0y2mvyye45x828rp6p73a', 'Ky3AiSn56PoTBLhBwqFbpJTtP35fSjh1ecrPEdUp3bdAKs8kZJKC', 'H3AW3q8xR6F+Y9NH2slXhDjPcpm9M97bb/ZZCGY2BT18GAQOTpLhTF1FusM0PM8Xgx2JQMFTyvMpGCREk9RT72s=')
