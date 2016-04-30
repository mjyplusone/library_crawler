import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import library_http
import sqlite3
import queue
import threading
import time

#-------------------------------------------------------------------------
def pagefind(url,Label):

	#加入异常处理
	r = library_http.HTTP()
	r.setget(url)
	soup = r.getpage()

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
		r = library_http.HTTP()
		r.setget(book_url)
		soup2 = r.getpage()
		marc = soup2.find("p",id="marc")
		marc = marc.getText()
		m = re.findall( r'\d+', marc)    #匹配出浏览次数和借阅次数
		book_num.append(m[1])            #存储借阅次数

		book_label.append(Label)         #所属标签
				
		workQueue2.put(book_label[-1])
		workQueue2.put(book_name[-1])
		workQueue2.put(book_year[-1])
		workQueue2.put(book_num[-1])
     
	print(book_label)   
	print(book_name)
	print(book_year)
	print(book_num)
#-------------------------------------------------------------------------



#-------------------------------------------------------------------------
exitFlag = 0

#获取数据线程类
class myThread (threading.Thread):
	def __init__(self, threadID, name, q):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
	def run(self):
		print ("Starting " + self.name)
		process_data(self.name, self.q)
		print ("Exiting " + self.name)

def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data1 = q.get()
            data2 = q.get()
            pagefind(data1,data2)
            queueLock.release()
            print ("%s processing %s\n" % (threadName, data1))
        else:
            queueLock.release()
        time.sleep(1)

#操作数据库线程类
class myThread2 (threading.Thread):
	def __init__(self, threadID, name, q):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
	def run(self):
		#打开SQlite数据库
		conn = sqlite3.connect('library_crawler.db')
		print ("Opened database successfully")
		print ("Starting " + self.name)
		while not exitFlag:
			if not workQueue2.empty():
				sq_data1 = self.q.get()
				sq_data2 = self.q.get()
				sq_data3 = self.q.get()
				sq_data4 = self.q.get()
				conn.execute("INSERT INTO '%s' (BOOK_NAME,BOOK_YEAR,BOOK_NUM) VALUES ('%s','%s','%s')"%(sq_data1,sq_data2,sq_data3,sq_data4))
				conn.commit()  
		print ("Records created successfully")
		conn.close()
		print ("Exiting " + self.name)
#-------------------------------------------------------------------------


queueLock = threading.Lock()
workQueue = queue.Queue()
workQueue2 = queue.Queue()
threads = []

#获得的信息
book_label = []    #标签
book_name = []    #书名
book_year = []    #出版日期
book_num = []     #借阅次数

# 创建新线程
#获取数据线程
thread1 = myThread(1, "Thread-1", workQueue)
thread1.start()
threads.append(thread1)

thread2 = myThread(2, "Thread-2", workQueue)
thread2.start()
threads.append(thread2)

#操作数据库线程
thread_sq = myThread2(3, "Thread-sq", workQueue2)
thread_sq.start()
threads.append(thread_sq)


url="http://202.195.144.118:8080/browse/cls_browsing_tree.php"
s_doctype = "all"
cls = ['A','B','C','D','E','F','G','H','I','J','K','N','O','P','Q','R','S','T','U','V','X','Z']
lvl = ['1#nodeA','1#nodeB','1#nodeC','1#nodeD','1#nodeE','1#nodeF',
	   '1#nodeG','1#nodeH','1#nodeI','1#nodeJ','1#nodeK','1#nodeN',
	   '1#nodeO','1#nodeP','1#nodeQ','1#nodeR','1#nodeS','1#nodeT',
	   '1#nodeU','1#nodeV','1#nodeX','1#nodeZ']
for i in range(0,22):
	url="http://202.195.144.118:8080/browse/cls_browsing_tree.php?"+"s_doctype="+s_doctype+"&cls="+cls[i]+"&lvl="+lvl[i]
	r = library_http.HTTP()
	r.setget(url)
	soup = r.getpage()
	print("label"+cls[i]+"...")


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
		url="http://202.195.144.118:8080/browse/cls_browsing_book.php?"+"s_doctype="+s_doctype+"&cls="+label[i]+"&clsname="+url_add[i]
		r = library_http.HTTP()
		r.setget(url)
		soup = r.getpage()
		font = soup.find('font',color='black')
		if font==None:      #处理只有一页提取不到页数的情况
			page = 1
		else:
			page = int(font.getText())


		for j in range(0,page):
			if j==0:
				str1 = "http://202.195.144.118:8080/browse/cls_browsing_book.php?"+"s_doctype="+s_doctype+"&cls="+label[i]+"&clsname="+url_add[i]				
				#conn.execute("INSERT INTO PAGE (LABEL,URL) VALUES ('%s', '%s')"%(label[i],str1));
				#pagefind("http://202.195.144.118:8080/browse/cls_browsing_book.php?"+"s_doctype="+s_doctype+"&cls="+label[i]+"&clsname="+url_add[i],label[i])
				# 填充队列
				queueLock.acquire()
				workQueue.put(str1)
				workQueue.put(label[i])
				queueLock.release()
			else:
				str1 = "http://202.195.144.118:8080/browse/cls_browsing_book.php?"+"s_doctype="+s_doctype+"&cls="+label[i]+"&clsname="+'&&page='+str(j+1)
				#conn.execute("INSERT INTO PAGE (LABEL,URL) VALUES ('%s', '%s')"%(label[i],str1));
				#pagefind("http://202.195.144.118:8080/browse/cls_browsing_book.php?"+"s_doctype="+s_doctype+"&cls="+label[i]+"&clsname="+'&&page='+str(j+1),label[i])
				queueLock.acquire()
				workQueue.put(str1)
				workQueue.put(label[i])
				queueLock.release()

		#conn.commit()


		# conn.execute('''CREATE TABLE "%s"
	 #       (BOOK_NAME   TEXT    NOT NULL,
	 #        BOOK_YEAR   TEXT    NOT NULL,
	 #        BOOK_NUM    TEXT    NOT NULL);'''%label[i])
		# print ("Table created successfully");

# 等待队列清空
while not workQueue.empty():
    pass

# 通知线程是时候退出
exitFlag = 1

# 等待所有线程完成
for t in threads:
    t.join()
print ("Exiting Main Thread")