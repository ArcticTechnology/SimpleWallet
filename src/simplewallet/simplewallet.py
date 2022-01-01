import json
import pkgutil
import requests
from random import sample
from .utils.commoncmd import CommonCmd as cmd
from .utils.configparser import ConfigParser

class SimpleWallet:

	def __init__(self):
		rawconfig = ConfigParser.get_config()
		if rawconfig['status'] == 200:
			config = rawconfig['output']
		else:
			config = {'answers': ['Unable to load answers']}

		self.answers = config['answers']

	def get_pkg_data(self):
		"""
		Modern way to get package data is with pkgutil.get_data(). See this post:
		https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package/58941536#58941536
		"""
		pkgdata = pkgutil.get_data(__name__, 'data/default.json')
		return json.loads(pkgdata.decode('utf-8'))

	def get_response(self):
		return sample(self.answers, 1)[0]

	def get_myip(self):
		"""
		Modern way to get get my ip using requests. See this post:
		https://stackoverflow.com/questions/22492484/how-do-i-get-the-ip-address-from-a-http-request-using-the-requests-library/22513161#22513161
		"""
		resp = requests.get('https://www.google.com', stream=True)
		return resp.raw._connection.sock.getsockname()

	def splashscreen(self):
		cmd.cls()
		print('Welcome to the Python Starter Package')

	def optionscreen(self):
		print(' ')
		print('What would you like to do?')
		print('(a) Ask me a question, (q) Quit')

	def option_a(self):
		cmd.cls()
		print('What question would you like to ask?')
		print(' ')
		question = input('Type your question: ')
		cmd.cls()
		print('Question: ' + question)
		print(' ')
		
		if question.lower() in ['get my data', 'get data', 'get my data.', 'get data.']:
			print('Answer: ' + str(self.get_pkg_data()))
		elif question.lower() in ['get my ip', 'my ip', 'what is my ip', 'what is my ip?']:
			print('Answer: ' + str(self.get_myip()))
		else:
			print('Answer: ' + self.get_response())
		print(' ')
		input()
		cmd.cls()

	def run(self):
		cmd.cls()
		self.splashscreen()

		while True:
			self.optionscreen()
			select = input()

			if select not in ['a', 'q']:
				#'(a) Ask me a question, (q) Quit'
				cmd.cls(); print('Invalid selection. Try again.')

			if select == 'q':
				cmd.cls()
				break

			if select == 'a':
				self.option_a()
