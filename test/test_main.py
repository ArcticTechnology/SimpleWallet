#!/usr/bin/python3 -B
from simplewallet import *

def test_main():
	simplewallet = SimpleWallet()
	configparser = ConfigParser()
	instance = Instance(configparser)
	addressgui = AddressGui(simplewallet, instance)
	signergui = SignerGui(simplewallet, instance)
	verifiergui = VerifierGui(simplewallet, instance)
	simplewalletgui = SimpleWalletGUI(simplewallet, instance,
							addressgui, signergui, verifiergui)
	simplewalletgui.run()

if __name__ == '__main__':
	raise SystemExit(test_main())