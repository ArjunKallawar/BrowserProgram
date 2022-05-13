from tornado import gen, httpclient, ioloop
import tornado.ioloop
import tornado.web
import sqlite3
import string
import time
import webbrowser
import subprocess
import os
import traceback

#Global dictionary to track open browser, tabs 
browserInstance = {
		'brave' : { 'pid':-1,'active_url':'','tab_urls':[]},
		'chrome' : { 'pid':-1,'active_url':'','tab_urls':[]},
		'safari' : { 'pid':-1,'active_url':'','tab_urls':[]}
	}
	
class BrowserService :
	global browserInstance 
	
	def openBrowser(browser,url):
		#Specify the browser application path
		if browser == 'chrome' :
			path = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'
		elif browser == 'brave' :
			path = '/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser'
		elif browser == 'safari' :
			path = '/Applications/Safari.app/Contents/MacOS/Safari'
		else:
			resp = 'Invalid Browser specified'
		
		#If browser is open then open url in new tab. Else open the browser with URL
		if browserInstance[browser]['pid'] == -1:
			webbrowser.get('open -a ' + path + ' %s').open(url)
			browserInstance[browser]['active_url'] = url
			browserInstance[browser]['tab_urls'].append(url)
			
			
			#Get the process ID of the newly open browser
			temp = subprocess.Popen(['ps', '-x'], stdout = subprocess.PIPE)
			op = temp.communicate()[0].decode("utf-8")
			temp = op.split('\n')
			
			browserPIDs = []
			for item in temp:
				path = path.replace('\ ',' ')
				if item.find(path) != -1:
					browserPIDs.append(item)
			#Debug options
			#print(path)
			#print('Debug')
			#print(browserPIDs)
			browserInstance[browser]['pid'] = browserPIDs[0].split(' ')[0]
		else:
			webbrowser.get('open -a ' + path + ' %s').open_new_tab(url)
			browserInstance[browser]['active_url'] = url
			browserInstance[browser]['tab_urls'].append(url)
			
		resp = 'Browser is open'
		print(browserInstance)
		return resp

	def getURL(browser):
		return browserInstance[browser]['active_url']
		
	def stopBrowser(browser):
		cmd = 'kill -9 ' + str(browserInstance[browser]['pid'])
		os.system(cmd)
		browserInstance[browser] = { 'pid':-1,'active_url':'','tab_urls':[]}
		print(browserInstance)
		return 'Browser Instance Closed'
	
	def cleanUpBrowser(browser):
		if browser == 'chrome' :
			path = '/Users/arjun/Library/Application Support/Google/Chrome/Default/History'
		elif browser == 'brave' :
			path = '/Users/arjun/Library/Application Support/BraveSoftware/Brave-Browser/Default/History'
		elif browser == 'safari' :
			path = '/Applications/Safari.app/Contents/MacOS/Safari'
		else:
			resp = 'Invalid Browser specified'
			
		try:
			print(path)
			conn = sqlite3.connect(path)
			c = conn.cursor()
			c.execute('DELETE FROM urls')
			conn.commit()
			resp = 'Cleanup operation is comeplete'
		except:
			traceback.print_exc()
			resp = 'Close the browser before cleanup operation'
			
		return resp

class ServiceHandler(tornado.web.RequestHandler):

	def get(self,path):
		#Get the request path
		rpath=self.request.path
		inputsValid = False
		#Initialize variable for response
		resp=''
		      
		if rpath == '/start' :
			
			try:
				browser = self.get_argument('browser')
				url = self.get_argument('url')
				inputsValid = True
			except:
				browser = ''
				url = ''
    		
			if inputsValid :
				resp = BrowserService.openBrowser(browser,url)
			else:
				resp = 'Invalid Inputs'
    	
		elif rpath == '/stop':
			#Required parameter browser
			
			try:
				browser = self.get_argument('browser')
				inputsValid = True
			except:
				browser = ''
    		
			if inputsValid :
				resp = BrowserService.stopBrowser(browser)
			else:
				resp = 'Invalid Inputs'
				
			
		elif rpath == '/cleanup':
			#Required parameter browser
			try:
				browser = self.get_argument('browser')
				inputsValid = True
			except:
				browser = ''
    		
			if inputsValid :
				resp = BrowserService.cleanUpBrowser(browser)
			else:
				resp = 'Invalid Inputs'
				
		elif rpath == '/geturl':
			#Required parameter browser
			try:
				browser = self.get_argument('browser')
				inputsValid = True
			except:
				browser = ''
    		
			if inputsValid :
				resp = BrowserService.getURL(browser)
			else:
				resp = 'Invalid Inputs'
			
		else:
		#NO matches
			resp='Invalid Input'
		self.write(resp)



application = tornado.web.Application([
    (r"/(.*)", ServiceHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()