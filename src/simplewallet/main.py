#!/usr/bin/python3 -B
from .simplewallet import SimpleWallet, SimpleWalletGUI
from .dircrawler.instance import Instance

def main():
	simplewallet = SimpleWallet()
	instance = Instance()
	simplewalletgui = SimpleWalletGUI(simplewallet, instance)
	simplewalletgui.run()
#	print(simplewallet.test())

if __name__ == '__main__':
	raise SystemExit(main())