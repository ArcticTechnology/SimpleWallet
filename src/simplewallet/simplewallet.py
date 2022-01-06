import base64
from .bitcoin.address import Address
from .bitcoin.privkey import Privkey
from .bitcoin.signer import Signer
from .bitcoin.verifier import Verifier

class SimpleWallet:

# Create Wallet
# Create Signature

	def test(self):
		message = 'hello world message'
		txin = 'p2wpkh'
		privkey = Privkey.generate(); address = Address.from_privkey(privkey, txin); signature = Signer.sign_message(privkey, message)
		return (address, privkey, signature)