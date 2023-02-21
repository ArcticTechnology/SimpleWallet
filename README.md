# Simple Wallet
The Simple Wallet is a minimalist Bitcoin wallet that lets you securely create Bitcoin addresses, sign messages, and validate addresses. Simple Wallet is completely open source and transparent; its simplicity minimizes its attack surface. Use this application on an offline computer to create fully secure Bitcoin private keys that will never be exposed to the internet. See the "Documentation" section of this guide for more details.
* Github repo: https://github.com/ArcticTechnology/SimpleWallet
* PyPi: https://pypi.org/project/SimpleWallet/

## Prerequisites
For Windows, it is recommended to run this app on a Linux emulation layer such as the Git Bash terminal. See the "Instructions for Git Bash" section for details. In addition to Git Bash, make sure you have Python3, Pip3, and Libsecp256k1-0 as described below.

For Mac and Linux, this app should work out of the box on either the Mac or Linux terminal, but make sure you have Python3, Pip3, and Libsecp256k1-0 as described below.

Requirements:
* Python3 (version 3.10 or greater) - Install Python3 here: [https://www.python.org/downloads/]. Check version with: ```python3 --version```.
* Pip3 (version 23.0 or greater) - Make sure to install python3-pip in order to use pip install. Check version with: ```pip3 --version```.
* Libsecp256k1-0 (version 0.3.0 or greater) or the equivalent - Libsecp265k1-0 is compiled libsecp256k1 python package that allows you to use the secp256k1 binary. See this for details: https://github.com/bitcoin-core/secp256k1. By installing Simple Wallet, it should install the libsecp256k1-0 package by default (https://github.com/ArcticTechnology/libsecp256k1-0). Libsecp265k1-0 contains the precompiled secp256k1 binaries and a Dockerized compiler that allows you to compile your own binaries. It is recommended that you compile your own binaries so that you don't need put your trust into our precompiled versions.

## Installation
There are a couple of options to install this app:
* Pip Install - This app is hosted on PyPi and can be installed with the following command:
```
pip3 install SimpleWallet
```
* Local Install - Alternatively, you can download or git clone the Github repo and install it locally with the following:
```
git clone https://github.com/ArcticTechnology/SimpleWallet.git
cd SimpleWallet
pip3 install -e .
```
To uninstall this app:
```
pip3 uninstall SimpleWallet
```
* If you used the local install option, you will also want to delete the ```.egg-info``` file located in the ```src/``` directory of the package. This gets created automatically with ```pip3 install -e .```.

## Usage
After installation, you can run this app in your terminal with this command:
```
simplewallet
```
You can also run it with ```python3 -m```:
```
python3 -m simplewallet
```

## Documentation
The Simple Wallet is a minimalist Bitcoin wallet that lets you securely create Bitcoin addresses, sign messages, and validate addresses. This application is intended to be run on an offline computer for maximum security. Install the fully open source code on to an offline computer and you will be able to create private keys that never touch the internet. The signature feature of this application allows you to use your private key to create signed messages. The validate feature allows you to use your signed messages to verify that an address is tied to a private key. This means before you send a single Satoshi to an address, you can check to make sure that your private key is able to unlocked that address without ever having to expose your private key. Finally, Simple Wallet has a bulk feature that let you create, sign, and verify multiple addresses in a csv file at the same time. 

### Settings
The Settings command allows you to modify the default settings of the application including setting a working directory and changing the address type. 

Simple Wallet is compatible with two address types: Pay To Public Key Hash (P2PKH) and Pay To Witness Public Key Hash (P2WPKH).

P2PKH is one of the most common address types which requires the sender to supply a valid signature (from the private key) and public key. The transaction output script will use the signature and the public key. 
Through some cryptographic functions will check if it matches with the public key hash, if it does, then the funds will be spendable. This method conceals your public key in the form of a hash for extra security.

Here is an example of a P2PKH address: ```1EgQPcb8pyKCasGYW7tPzmTXEyp2uEGbGF```

P2WPKH is another common address type that is like P2PKH except it uses segregated witness (segwit). Instead of using scriptSig parameters to check the transaction validity, it uses a witness. The witness separates the transaction data from the validation data moving it to the end of the hash. By default, the Simple Wallet uses P2WPKH, but you have the option to select P2PKH or you can have the application derive both types.

Here is an example of a P2WPKH address: ```bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn```

In order to use the bulk create features of the Simple Wallet, you will need to have a working directory set. This lets the Simple Wallet know which files and folders to use. You can set the working directory in your settings. This will allow you to simply pass Simple Wallet the file name you want it to modify.

The Simple Wallet works natively for linux paths. However, it should also work for windows and mac paths, as set dir will attempt to convert them to a standard format. Acceptable directory format examples include:
* ```/home/user/documents/myfolder```
* ```/c/user/documents/myfolder```
* ```C:/documents/myfolder```
* ```C:\documents\myfolder```

### Wallet
The Simple Wallet allows you to generate an address and private key pair or bulk addresses and private key pairs. If you already have a private key, you can also use it to derive your address. 

The way in which Simple Wallet generates private keys is with the Elliptic Curve Digital Signature Algorithm (ECDSA). In accordance with ECDSA, this application produces a cryptographically safe 256bit random integer. This integer is uniformly distributed between 1 <= k < bound, with the bound being the curve order. For secure randomness, this app relies on the Python secrets module which utilizes synchronization methods to generate randomness where no two processes can replicate the same data. See references below for more details:
* ECDSA Summary: https://bitcoin.stackexchange.com/a/98530
* ECDSA Specs: https://en.bitcoin.it/wiki/Secp256k1
* Secrets Module Summary: https://pynative.com/python-secrets-module/
* Secrets Module Specs: https://github.com/python/cpython/blob/3.6/Lib/secrets.py

The Simple wallet has the ability to bulk create addresses. In order to do that, you must first select a working directory in the app's settings. Then with the bulk feature, select the number of addresses you would like to create and the Simple Wallet will generate a CSV file with the addresses and their private keys and save it to your working directory.

### Signature
With Simple Wallet, you have the ability to generate signed messages using your private key. The signature function lets you paste in a private key and a message to generate your signed message. The advantage of having this signed message is it allows you to prove that the private key you own can unlock a specific address. More on this in the next section.

Here is an example of a signed message as well as the message and the private key use to create it.
```
Signature: H3AW3q8xR6F+Y9NH2slXhDjPcpm9M97bb/ZZCGY2BT18GAQOTpLhTF1FusM0PM8Xgx2JQMFTyvMpGCREk9RT72s=
Message: hello world message
Private Key: Ky3AiSn56PoTBLhBwqFbpJTtP35fSjh1ecrPEdUp3bdAKs8kZJKC
```

### Verify
The Simple Wallet also allows you to verify that your private key can unlock a specific address. With the verify feature, you can provide a message and the signature to cryptographically derive the address. This proves that the private key you used to sign your message is tied to the derived address. The verify feature also allows you to use a private key to verify your address as well. Of course, using signed messages for verification is preferable because this way you can keep your private key locked away and still be able to verify your addresses.

Here is an example of a signature and message. Feel free to use them with Simple Wallet to verify the address below.
```
Signature: H3AW3q8xR6F+Y9NH2slXhDjPcpm9M97bb/ZZCGY2BT18GAQOTpLhTF1FusM0PM8Xgx2JQMFTyvMpGCREk9RT72s=
Message: hello world message
Address (p2wpkh): bc1qvkuuatw6zsqhtx4md0y2mvyye45x828rp6p73a
```

Simple Wallet also has the ability to bulk verify addresses in a CSV file. Simply provide a csv file of addresses and signed messages (or private keys) and the verify feature can verify them all at once.

Here are a few more addresses you can try. The message is ```hello world message```. Please DO NOT use any of these example addresses in this guide to store Bitcoin as all of their private keys have been exposed.
```
Address (p2pkh): 1EgQPcb8pyKCasGYW7tPzmTXEyp2uEGbGF
Private Key: L5YggYAVHYtECWx8gWFPTs9we1VqFBjpexwWMdNyYLow7omhcCgZ
Signature: IG/7jZpMRGwcsVGBW9Gi/ccThA0c705YqaMrQKrgV8rLKcV86qZljGljGIXj4G0bLWJwbPZxuxCh1qUXiDjRAn8=

Address (p2pkh): 1H4FYUfj7Z8Nj9dg82M4n594J1R1h3G5Vn
Private Key: L1KpGvKzEdWFdogJ6yje9UM1gCmFJT5x2ZQqFTQhA33sBSiQk2hT
Signature: IGA0+UZ1urDdRdf/cOzZHrjaOfJrOY0lDqQ+EZbM8NKUNq46yB2oSxjOLjAfBUIDV43RdZKKk4ipI2sp2H/saq0=

Address (p2wpkh): bc1q3gvzwanemg6yxnwrxsfst6wj6e40mz2r40npfn
Private Key: L5HhPdapxP847zRPh7VsqqVtncW7VwyXGZXSohZg42QE69CxrLn5
Signature: IHvpYON7xWJt2DTTp53RUErb7TE3EBhoQzDo2m0yv5FdV+z3cDDGJ7kEDGVLc1dy0d8akq5P4tvl4y0hUEl4ZSU=

Address (p2wpkh): bc1q2ln4pdyxe4uszrsgpp2rwqdjxf6l8fy5n8tu5x
Private Key: L2koUM53HnhvHatFKb3RHW1LfziiDSkdvf4H2u2zRZwB7GZGRNyv
Signature: H0YLULEwPs9ut+WvTCWJ/JmxfAEWNgCFrR6zcoL94wbBUJ3A2to021GCoMHK5kuq14k868og0CIAS3c7ENRQ3Hg=
```

### Conclusion
With the Simple Wallet, you now have a simple way to create Bitcoin addresses, sign messages, and validate addresses. Remember, the best way to use this app is in an offline computer for maximum security. Hope you enjoy.

## Troubleshooting
This section goes over some of the common issues found and how to resolve them.

### "Command Not Found" Error When Running the App
On Linux, if you are getting a ```command not found``` error when trying to run the app, you may need to add ```~/.local/bin/``` to PATH. See this thread for details: [https://stackoverflow.com/a/34947489]. To add ```~/.local/bin/``` to PATH do the following:

1. Add ```export PATH=~/.local/bin:$PATH``` to ```~/.bash_profile```.
```
echo export PATH=~/.local/bin:$PATH > ~/.bash_profile
```
2. Execute command.
```
source ~/.bash_profile
```

### Instructions for Git Bash
For Windows, it is recommended to run this app on a linux emulation layer like the Git Bash terminal. Here are the instructions for installing and setting up Git Bash:
1. Go to https://git-scm.com/downloads and click download.
```
Version >= 2.34.1
```
2. During the installation setup, make sure to include OpenSSH. Recommenced setting should be fine:
```
Use bundled OpenSSH - This uses ssh.exe that comes with Git.
```
3. Leave the other settings as default, click through, and install.
4. Open ```bash.exe``` and install Python3 https://www.python.org/downloads/
5. Proceed to the "Installation" section to install this app.

IMPORTANT: For Windows, use the ```bash.exe``` terminal rather ```git-bash.exe```. There is a known issue with ```git-bash.exe``` messing up Python ```os``` commands in ```import os```. See this thread for details: [https://stackoverflow.com/a/33623136].
* You can find ```bash.exe``` Git folder in the ```bin/``` directory. For example: If ```git-bash.exe``` is here ```C:\Program Files\Git\git-bash.exe``` then you should find ```bash.exe``` here ```C:\Program Files\Git\bin\bash.exe```.


## Support and Contributions
Our software is open source and free for public use. If you found any of these repos useful and would like to support this project financially, feel free to donate to our bitcoin address.

Bitcoin Address 1: 1GZQY6hMwszqxCmbC6uGxkyD5HKPhK1Pmf

![alt text](https://github.com/ArcticTechnology/BitcoinAddresses/blob/main/btcaddr1.png?raw=true)
