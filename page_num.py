import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

page_all = 0
url="http://202.195.144.118:8080/browse/cls_browsing_tree.php"
s_doctype = "all"
cls = ['A','B','C','D','E','F','G','H','I','J','K','N','O','P','Q','R','S','T','U','V','X','Z']
lvl = ['1#nodeA','1#nodeB','1#nodeC','1#nodeD','1#nodeE','1#nodeF',
	   '1#nodeG','1#nodeH','1#nodeI','1#nodeJ','1#nodeK','1#nodeN',
	   '1#nodeO','1#nodeP','1#nodeQ','1#nodeR','1#nodeS','1#nodeT',
	   '1#nodeU','1#nodeV','1#nodeX','1#nodeZ']
for i in range(0,22):
	r = requests.get("http://202.195.144.118:8080/browse/cls_browsing_tree.php?"+"s_doctype="+s_doctype+"&cls="+cls[i]+"&lvl="+lvl[i])
	r.encoding='utf-8'
	#print(r.url)	
	print("label"+cls[i]+"...")

	soup = BeautifulSoup(r.text,"html.parser")

	#print (soup.prettify())

	label = []
	url_add = [] 
	label_num = 0 
	for div in soup.find_all('div',class_='stepright2'):
		link = div.find('a',style='cursor:hand;')
		if link==None:        #处理标签为span的特殊情况
			link = div.find('span',style='cursor:hand;')
		#print(link)
		string = link.get('onclick')
		m = re.findall( r"(?<=').+?(?=')", string)
		url = urllib.parse.unquote(m[2])     #decode
		url_add.append(url)
		label.append(m[0])
		label_num += 1

	for i in range(0,label_num):
		s_doctype = "all"
		# cls = label[0]
		# clsname = url_add[0]
		#最终要获取数据的页面
		r = requests.get("http://202.195.144.118:8080/browse/cls_browsing_book.php?"+"s_doctype="+s_doctype+"&cls="+label[i]+"&clsname="+url_add[i])
		#print(r.url)
		r.encoding = 'utf-8'
		soup = BeautifulSoup(r.text,"html.parser")
		font = soup.find('font',color='black')
		if font==None:      #处理只有一页提取不到页数的情况
			page = 1
		else:
			page = font.getText()
		print(page)
		page_all += int(page)
	print("present pagecount: "+str(page_all))