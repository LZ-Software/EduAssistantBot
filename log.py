from time import localtime, strftime


class Logger:

	class __Colors:
		OKGREEN = '\033[92m'
		WARNING = '\033[93m'
		FAIL = '\033[91m'
		ENDC = '\033[0m'

	@staticmethod
	def __get_time():
		return strftime("%Y-%m-%d %H:%M:%S", localtime())

	@staticmethod
	def info(text):
		print(f"{Logger.__Colors.WARNING}[{Logger.__get_time()}] {text}{Logger.__Colors.ENDC}")

	@staticmethod
	def ok(text):
		print(f"{Logger.__Colors.OKGREEN}[{Logger.__get_time()}] {text}{Logger.__Colors.ENDC}")

	@staticmethod
	def error(text):
		print(f"{Logger.__Colors.FAIL}[{Logger.__get_time()}] {text}{Logger.__Colors.ENDC}")
