import os; import random; import string
from .crawler import Crawler

class FileModder:

	@classmethod
	def read_file(self, filepath: str) -> list: #in scrambler move this from crawler to here.
		lines = []
		with open(filepath,'r') as f:
			for line in f:
				if line[0] != '#':
					lines.append(line.rstrip('\n'))
		return lines

	@classmethod
	def read_line(self, filepath: str, linenum: int) -> str:
		with open(filepath,'r') as f:
			for n, line in enumerate(f):
				if n == linenum:
					return line.rstrip('\n')
		return ''

	@classmethod
	def _get_last_line(self, openedFile):
		try:
			openedFile.seek(-2, os.SEEK_END)
			while openedFile.read(1) != b'\n':
				openedFile.seek(-2, os.SEEK_CUR)
		except:
			pass

	@classmethod
	def read_last_line(self, filepath: str) -> str:
		with open(filepath, 'rb') as f:
			self._get_last_line(f)
			last_line = '\n' + f.readline().decode(errors='replace')
			return last_line

	@classmethod
	def format_ext(self, raw_extension, ifblank='.txt', ifstar=None):
		if raw_extension == '*':
			return ifstar
		if raw_extension == '':
			return ifblank
		if raw_extension[0] != '.':
			return '.' + raw_extension
		else:
			return raw_extension

	@classmethod
	def add_extension(self, wd: str, extension: str): # Create a new add extension to a file and update this function.
		if extension == None or '.' not in extension:
			return 'No extension found.'

		filepaths = Crawler.get_files(wd, extension=None)

		if len(filepaths) <= 0:
			return 'No files found.'

		for filepath in filepaths:
			if '.' not in filepath:
				os.rename(filepath, filepath+extension)
				print('Renamed: ' + str(filepath)) #This probably needs to be rewritten.

		return Crawler.get_files(wd, extension)

	@classmethod
	def add_tag(self, filepath: str, tag: str, spliton:str = '-',
					oldtags: list = [], newtags: list = []) -> str: #make sure to fix this in scrambler
		extension = Crawler.get_extension(filepath)
		prefix = Crawler.get_prefix(filepath)

		existing_tag = prefix.split(spliton)[-1]

		# If tag already applied then do not apply tag.
		if existing_tag in newtags: return filepath

		if existing_tag in oldtags:
			#If existing tag is in old tags, then update it to tag.
			return prefix.split(existing_tag)[0] + tag + extension
		else:
			return prefix + spliton + tag + extension

	@classmethod
	def add_rtag(self, filepath: str, length: int = 5, spliton: str = '-') -> str:
		if length < 4: length = 4
		if length > 10: length = 10
		extension = Crawler.get_extension(filepath)
		prefix = Crawler.get_prefix(filepath)
		rtag=''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
		return prefix + spliton + rtag + extension
