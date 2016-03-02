import requests
from bs4 import BeautifulSoup
import re

def page(url):
	book_name = []    #书名
	book_year = []    #出版日期
	book_num = []     #借阅次数

	r = requests.get(url)
	print(r.url)
	r.encoding = 'utf-8'
	soup = BeautifulSoup(r.text,"html.parser")

	for div in soup.find_all('div',class_='list_books'):
		link = div.find('a')

		book_name.append(link.string)     
	  
		year = div.p.getText()
		pattern = re.compile(r'\d+')
		if re.findall(pattern, year)==[]:
			book_year.append('?')
		else:				
			year = re.findall(pattern, year)[0]
			book_year.append(re.findall(pattern, year)[0])

		url = link.get('href')
		m = re.search( r"(?<=/).+", url)
		book_url = "http://202.195.144.118:8080/"+m.group(0)    #详细信息界面
		r = requests.get(book_url)
		r.encoding='utf-8'
		soup2 = BeautifulSoup(r.text,"html.parser")
		marc = soup2.find("p",id="marc")
		marc = marc.getText()
		m = re.findall( r'\d+', marc)    #匹配出浏览次数和借阅次数
		book_num.append(m[1])            #存储借阅次数

	print(book_name)
	print(book_year)
	print(book_num)