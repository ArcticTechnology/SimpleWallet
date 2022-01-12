#!/usr/bin/python3 -B
from simplewallet import *

def test_main():
	simplewallet = SimpleWallet()
	instance = Instance()
	simplewalletgui = SimpleWalletGUI(simplewallet, instance)
	simplewalletgui.run()

if __name__ == '__main__':
	raise SystemExit(test_main())