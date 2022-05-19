import os
import requests
import shutil


class Downloader:

	@staticmethod
	def __create_dir(path):
		if os.path.isdir(path):
			shutil.rmtree(path)
			os.mkdir(path)

	@staticmethod
	def download_file(url, filename):
		r = requests.get(url, stream=True)
		if r.status_code == 200:
			with open(f'{filename}', 'wb') as f:
				r.raw.decode_content = True
				shutil.copyfileobj(r.raw, f)
				print('Got schedule')
		else:
			raise FileNotFoundError('Can\'t download file')

	@staticmethod
	def download_files(files):
		folder = f'{os.getcwd()}\\schedule'
		Downloader.__create_dir(folder)
		for file in files.items():
			name = file[0]
			url = file[1]
			r = requests.get(url, stream=True)
			if r.status_code == 200:
				with open(f'{folder}\\{name}', 'wb') as f:
					r.raw.decode_content = True
					shutil.copyfileobj(r.raw, f)
					print(name)
			else:
				print(f'ERROR {name}')