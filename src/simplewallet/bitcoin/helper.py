# Simple Wallet
# Copyright (c) 2023 Arctic Technology

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ..crypto.sha256 import Sha256
from ..utils.hexxer import Hexxer
from ..utils.conversion import inv_dict

TXIN_LIST = ('p2pkh','p2wpkh')

def variable_length_integer(i: int) -> str:
	# See: https://en.bitcoin.it/wiki/Protocol_specification#Variable_length_integer
	# https://github.com/bitcoin/bitcoin/blob/efe1ee0d8d7f82150789f1f6840f139289628a2b/src/serialize.h#L247
	# "CompactSize"
	assert i >= 0, i
	if i<0xfd:
		return Hexxer.int_to_hex(i)
	elif i<=0xffff:
		return "fd" + Hexxer.int_to_hex(i,2)
	elif i<=0xffffffff:
		return "fe" + Hexxer.int_to_hex(i,4)
	else:
		return "ff" + Hexxer.int_to_hex(i,8)

def magic_hd(message: bytes) -> bytes:
	# Double hash Bitcoin Signed Message prefix + length + message
	# in accordence with Bitcoin Message Magic signing logic.
	# See: https://bitcoin.stackexchange.com/questions/34135/what-is-the-strmessagemagic-good-for.
	vli = variable_length_integer(len(message))
	length = Hexxer.bfh(vli)
	raw_signed_msg = b"\x18Bitcoin Signed Message:\n" + length + message
	return Sha256.hashd(raw_signed_msg)

class Wif:
	WIF_SCRIPT_TYPES = {
		'p2pkh':0,
		'p2wpkh':1,
		'p2wpkh-p2sh':2,
		'p2sh':5,
		'p2wsh':6,
		'p2wsh-p2sh':7}

	WIF_SCRIPT_TYPES_INV = inv_dict(WIF_SCRIPT_TYPES)

	SEGWIT_TYPES = ('p2wpkh', 'p2wpkh-p2sh', 'p2wsh', 'p2wsh-p2sh')

class BitcoinMainnet:

	NET_NAME = "mainnet"
	TESTNET = False
	WIF_PREFIX = 0x80
	ADDRTYPE_P2PKH = 0
	ADDRTYPE_P2SH = 5
	SEGWIT_HRP = "bc"
	BOLT11_HRP = SEGWIT_HRP
	GENESIS = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
	DEFAULT_PORTS = {'t': '50001', 's': '50002'}
	#DEFAULT_SERVERS = read_json('servers.json', {})
	#CHECKPOINTS = read_json('checkpoints.json', [])
	BLOCK_HEIGHT_FIRST_LIGHTNING_CHANNELS = 497000

	XPRV_HEADERS = {
		'standard': 0x0488ade4, # xprv
		'p2wpkh-p2sh': 0x049d7878, # yprv
		'p2wsh-p2sh': 0x0295b005, # Yprv
		'p2wpkh': 0x04b2430c, # zprv
		'p2wsh': 0x02aa7a99, # Zprv
	}
	XPRV_HEADERS_INV = inv_dict(XPRV_HEADERS)
	XPUB_HEADERS = {
		'standard': 0x0488b21e, # xpub
		'p2wpkh-p2sh': 0x049d7cb2, # ypub
		'p2wsh-p2sh': 0x0295b43f, # Ypub
		'p2wpkh': 0x04b24746, # zpub
		'p2wsh': 0x02aa7ed3, # Zpub
	}
	XPUB_HEADERS_INV = inv_dict(XPUB_HEADERS)
	BIP44_COIN_TYPE = 0
	LN_REALM_BYTE = 0
	LN_DNS_SEEDS = [
		'nodes.lightning.directory.',
		'lseed.bitcoinstats.com.',
		'lseed.darosior.ninja',
	]