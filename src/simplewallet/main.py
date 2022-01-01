#!/usr/bin/python3 -B
import simplewallet
from .simplewallet import SimpleWallet

def main():
	simplewallet = SimpleWallet()
	simplewallet.run()

if __name__ == '__main__':
	raise SystemExit(main())