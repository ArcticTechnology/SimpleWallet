#!/usr/bin/python3 -B
from .simplewallet import SimpleWallet, SimpleWalletGUI
from .gui.instance import Instance
from .gui.addressgui import AddressGui
from .gui.signergui import SignerGui
from .gui.verifiergui import VerifierGui
from .utils.configloader import ConfigLoader

def main():
	simplewallet = SimpleWallet()
	configloader = ConfigLoader()
	instance = Instance(configloader)
	addressgui = AddressGui(simplewallet, instance)
	signergui = SignerGui(simplewallet, instance)
	verifiergui = VerifierGui(simplewallet, instance)
	simplewalletgui = SimpleWalletGUI(simplewallet, instance,
							addressgui, signergui, verifiergui)
	simplewalletgui.run()

if __name__ == "__main__":
	raise SystemExit(main())