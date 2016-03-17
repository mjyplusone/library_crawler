import requests
from bs4 import BeautifulSoup

class HTTP:
	def setget(self,url):
		self.url=url
	def getpage(self):
		try:
			r = requests.get(self.url)
		except:print("Error!")
		else:
			r.encoding='utf-8'
			soup = BeautifulSoup(r.text,"html.parser")
			return soup
	