# Simple Wallet
The Simple Wallet is a minimalist Bitcoin wallet that lets you securely create Bitcoin addresses, sign messages, and validate addresses in a fully offline environment. Simple Wallet is completely open source and transparent; its simplicity minimizes its attack surface. Use this application on an offline computer to create fully secure Bitcoin private keys that will never be exposed to the internet. See the "Documentation" section of this guide for more details.
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
The purpose of this project is to show you how to create a standard python package from scratch. This project is inspired by @iamtennislover's excellent getmyip package (https://github.com/iamtennislover/getmyip) and @sigma-coding's great guide on deploying python packages (https://github.com/areed1192/sigma-coding).

### Setup
See "PythonStarterPackage Setup Guide.md" in ```doc/``` for a detailed walkthrough of what each of the package resources do. Once you have an understanding of this package, you can clone this package to your local directory and proceed to testing and deployment.

### Testing
In the directory containing the ```setup.py``` file, you can test the package by installing it in ```pip3``` editable mode. This will allow you make changes to it and test it without having to push the changes each time.
1. Use ```pip3``` to install the package in editable mode:
```
pip3 install -e .
```
2. Run the package by calling the package directly:
```
pythonstarterpackage
```
Or use ```python3 -m```:
```
python3 -m pythonstarterpackage
```
3. Testing the import. Run the ```test_main.py``` file:
```
python3 ./test/test_main.py
```
4. Once finished, delete the PythonStarterPackage.egg-info file and uninstall the package with:
```
pip3 uninstall PythonStarterPackage
```

Note: It is recommended that you use a virtual environment when testing your package.
1. To create a virtual environment:
```
virtualenv venv
```
2. Activate the environment use: ```. venv/bin/activate```. On Windows it may be: ```. venv/Script/activate```.

### Dependency Mapping
Next, make sure to check the package dependencies and update the setup.cfg file as needed. To do this:
1. Create (or overwrite) the requirements.txt document with ```pipreqs```. This is an extremely useful tool because it automatically finds all of the relevant versions of dependencies your package relies on and puts them into the ```requirements.txt``` file. If you don't have ```pipreqs```, install it with ```pip install pipreqs```.
```
pipreqs --force --encoding utf-8
```
2. Once the ```requirements.txt``` is updated, check to see if there is any additional dependencies that need to be added or updated in setup.cfg under the ```install_requires =```. If so, add or update it.

### Deployment
Once the package is ready, we can work on deploying the package.

1. Upgrade ```setuptools```, ```wheel```, and ```twine``` (```twine``` will be used in the next part).
```
pip3 install --upgrade setuptools wheel twine
```
2. Build the package with ```setup.py```.
```
python3 setup.py sdist bdist_wheel
```
3. Check the contents of the .whl and .tar.gz distributions. The key things to look for are: (1) all of your package subdirectories like utils are added to both distributions, (2) your config and package data are included in both distributions.
```
unzip -l dist/*.whl && tar --list -f dist/*.tar.gz
```
4. Test a local install of the package and run it to make sure it is working.
```
pip3 install .
pythonstarterpackage
```
5. After testing that it is working, uninstall the package from pip3.
```
pip3 uninstall PythonStarterPackage
```
If there are any issues in the above you can always uninstall the package and delete the distributions then proceed to troubleshoot the issue. Once complete start over from the beginning. The commands below allows you to delete the distributions.
```
rm -rf build dist src/*.egg-info
```
BE CAREFUL not to miss copy the above command, as if you delete something you didn't intend you will not be able to retrieve.

### Upload to PyPi
In order to upload to PyPi make sure to setup your PyPi account first. See "PyPi Setup Guide.md" in ```doc/``` for more details. You will also need to have ```twine``` installed and upgraded. Once you have all of this setup do the following:

1. Upload using ```twine```.
```
twine upload dist/*
```
2. Install your package with ```pip```.
```
pip3 install PythonStarterPackage
```
Note: If you get a "Requirements already satisfied..." for PythonStarterPackage when trying to install, it may be because ```pip``` still thinks you have the package already installed from the testing earlier. To cleanly break that connection, simply delete the ```./src/PythonStarterPackage.egg-info```. Then try uninstalling and reinstalling again.

3. Finally, run the app with: ```pythonstarterpackage```.
4. Uninstall with: ```pip3 uninstall PythonStarterPackage```.

## Support and Contributions
Our software is open source and free for public use. If you found any of these repos useful and would like to support this project financially, feel free to donate to our bitcoin address.

Bitcoin Address 1: 1GZQY6hMwszqxCmbC6uGxkyD5HKPhK1Pmf

![alt text](https://github.com/ArcticTechnology/BitcoinAddresses/blob/main/btcaddr1.png?raw=true)
