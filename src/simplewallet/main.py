#!/usr/bin/python3 -B
from .simplewallet import SimpleWallet

def main():
	simplewallet = SimpleWallet()
	#simplewallet.run()
	print(simplewallet.test())

if __name__ == '__main__':
	raise SystemExit(main())