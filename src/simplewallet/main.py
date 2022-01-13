#!/usr/bin/python3 -B
from .simplewallet import SimpleWallet, SimpleWalletGUI
from .gui.instance import Instance
from .utils.configparser import ConfigParser

def main():
	simplewallet = SimpleWallet()
	configparser = ConfigParser()
	instance = Instance(configparser)
	simplewalletgui = SimpleWalletGUI(simplewallet, instance)
	simplewalletgui.run()
#	print(simplewallet.test())

if __name__ == '__main__':
	raise SystemExit(main())