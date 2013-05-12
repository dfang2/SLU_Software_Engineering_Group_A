from Tkinter import *
from PIL import Image, ImageTk
import re
import os
import zmq
import urllib2
import json
import graphanalysis as g
from datetime import datetime, date

#string constants
ALPHANUMERIC_UNDERSCORE = "^[a-zA-Z0-9_ ]*$"

#alert number constants
ALERT_INVALID_INPUT = 0
ALERT_NO_NETWORK_CONNECTION = 1
ALERT_NO_SERVER_CONNECTION = 2
ALERT_FAILED_SENTIMENT_ANALYZER = 3
ALERT_FAILED_GET_TWEETS = 4
ALERT_FAILED_FINANCE_INFO = 5
ALERT_DATE_RANGE_ERROR = 6

MAX_LENGTH_COMPANY_NAME = 32

ALERT_ARRAY = ["Invalid Input", "No Network Connection", "Server Problems", \
		"Sentiment Analyzer Failure", "Aaron's Fault...", "Floundering Financials", "Invalid Date Range"]

TICKER_SYMBOL_DICT = {'Goog':'GOOG', 'Samsung':'IBM', 'Sony':'SNE', 'Microsoft':'MSFT', 'Dell':'DELL'}


class Application(Frame):

	def __init__(self, parent, address):
		Frame.__init__(self, parent, background="white")

	#---------Class Variables---------------
		self.parent = parent
		self.companies = []
		self.address = address

		self.previousSelectedCompany = ""

		self.companiesAdded = []
		self.startDatesAdded = []
		self.endDatesAdded = []

		self.listViewList = []

		self.tweetInfoDict = {}
		self.stockInfoDict = {}


		self.parent.title("Twahoo Finance")

		self.createMainMenuObjects()
		self.displayMainMenu()


	def addCompany(self):
		company = self.listVariableCompany.get()
		startDate = self.listVariableStartDate.get()
		endDate = self.listVariableEndDate.get()

		startYear = int(startDate[0:4])
		endYear = int(endDate[0:4])
		startMonth = int(startDate[5:7])
		endMonth = int(endDate[5:7])
		startDay = int(startDate[8:10])
		endDay = int(endDate[8:10])

		if(company != "" and company not in self.companiesAdded):
			if(endYear < startYear):
				self.showAlertDialogue(ALERT_DATE_RANGE_ERROR)
			elif(endMonth < startMonth):
				self.showAlertDialogue(ALERT_DATE_RANGE_ERROR)
			elif(endDay < startDay):
				self.showAlertDialogue(ALERT_DATE_RANGE_ERROR)
			else:
				self.companyListBox.insert(END, company)
				self.companiesAdded.append(company)
				self.startDateListBox.insert(END, startDate)
				self.startDatesAdded.append(startDate)
				self.endDateListBox.insert(END, endDate)
				self.endDatesAdded.append(endDate)


	def showAlertDialogue(self, alertNum):
		alert = Toplevel()
		alert.title("Something Went Wrong!")
		alertMessage = Message(alert, text=ALERT_ARRAY[alertNum])
		alertMessage.pack()
		dismiss = Button(alert, text="Dismiss", command=alert.destroy)
		dismiss.pack()


	def hideMainMenu(self):
		self.refreshButton.grid_forget()
		self.companyListBox.grid_forget()
		self.startDateListBox.grid_forget()
		self.endDateListBox.grid_forget()
		self.companyLabel.grid_forget()
		self.startDateLabel.grid_forget()
		self.endDateLabel.grid_forget()
		self.addButton.grid_forget()
		self.retrieveDataButton.grid_forget()
		self.refreshButton.grid_forget()
		self.companyDrop.grid_forget()
		self.startDateDrop.grid_forget()
		self.endDateDrop.grid_forget()
		self.deleteButton.grid_forget()

	
	def displayMainMenu(self):
		self.companyLabel.grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=(100,0), sticky=S)
		self.startDateLabel.grid(row=0, column=2, columnspan=1, rowspan=1, padx=5, pady=(100,0), sticky=S)
		self.endDateLabel.grid(row=0, column=4, columnspan=1, rowspan=1, padx=5, pady=(100,0), sticky=S)
		self.companyListBox.grid(row=1, column=0, columnspan=1, rowspan=2, padx=10, sticky=E+W+S+N)
		self.startDateListBox.grid(row=1, column=2, columnspan=1, rowspan=2, padx=10, sticky=E+W+S+N)
		self.endDateListBox.grid(row=1, column=4, columnspan=1, rowspan=2, padx=10, sticky=E+S+W+N)
		self.companyDrop.grid(row=4, column=0, columnspan=1, rowspan=1, padx=10, sticky=E+S+N+W)
		self.startDateDrop.grid(row=4, column=2, columnspan=1, rowspan=1, padx=10, sticky=E+S+N+W)
		self.endDateDrop.grid(row=4, column=4, columnspan=1, rowspan=1, padx=10, sticky=E+S+N+W)
		self.addButton.grid(row=4, column=5, columnspan=1, rowspan=1, sticky=W+S+N)
		self.retrieveDataButton.grid(row=7, column=4, columnspan=1, rowspan=1, padx=15, pady=25, sticky=E+S+N+W)
		self.refreshButton.grid(row=7, column=0, columnspan=1, rowspan=1, padx=15, pady=25, sticky=E+S+N+W)
		self.deleteButton.grid(row=1, column=5, columnspan=1, rowspan=1, sticky=W+N+E)

	def createMainMenuObjects(self):
		self.companyLabel = Label(self.parent, text="Company:")
		self.startDateLabel = Label(self.parent, text="Start Date:")
		self.endDateLabel = Label(self.parent, text="End Date:")

		self.companyListBox = Listbox(self.parent)
		
		self.startDateListBox = Listbox(self.parent)

		self.endDateListBox = Listbox(self.parent)

		companies = self.refreshCompanyList()
		self.listCompanies = companies
		self.listVariableCompany = StringVar()
		self.listVariableCompany.set(self.listCompanies[0])
		self.companyDrop = OptionMenu(self.parent, self.listVariableCompany, *self.listCompanies)

		startDates = self.refreshDateList()
		self.listStartDates = startDates
		self.listVariableStartDate = StringVar()
		self.listVariableStartDate.set(self.listStartDates[0])
		self.startDateDrop = OptionMenu(self.parent, self.listVariableStartDate, *self.listStartDates)

		self.listEndDates = startDates
		self.listVariableEndDate = StringVar()
		self.listVariableEndDate.set(self.listEndDates[0])
		self.endDateDrop = OptionMenu(self.parent, self.listVariableEndDate, *self.listEndDates)

		self.addButton = Button(self.parent, text="+", command=self.addCompany)

		self.retrieveDataButton = Button(self.parent, text="Get My Data", command=self.retrieveData)

		self.refreshButton = Button(self.parent, text="Refresh Company List", command=self.refreshCompanyList)

		self.deleteButton = Button(self.parent, text="-", command=self.deleteSelectedCompany)

	
	def createCompanyInfoObjects(self, companyInfo):
		self.listViewList = []
		offset = 0
		for c in companyInfo:
			index = self.companiesAdded.index(c)
			sd = self.startDatesAdded[index]
			newListView = self.ListView(self, c, companyInfo[c][0], companyInfo[c][1], companyInfo[c][2], rowOffset=offset, startDate=sd)
			self.listViewList.append(newListView)
			offset = offset + 1

		self.companyInfoBackButton = Button(self.parent, text="Back", command=self.companyInfoBack)


	def displayCompanyInfo(self):
		self.hideMainMenu()
		backButtonRow = 1

		for lv in self.listViewList:
			lv.display()
			backButtonRow = backButtonRow+2

		self.companyInfoBackButton.grid(row=backButtonRow, column=0, columnspan=1, rowspan=1, padx=(25,0), pady=(15,0), sticky=W+N)


	def hideCompanyInfo(self):
		for lv in self.listViewList:
			lv.forget()

		self.companyInfoBackButton.grid_forget()


	def deleteSelectedCompany(self):
		cSelection = self.companyListBox.curselection()
		sSelection = self.startDateListBox.curselection()
		eSelection = self.endDateListBox.curselection()

		selection = ""

		if(cSelection):
			selection = cSelection
		elif(sSelection):
			selection = sSelection
		elif(eSelection):
			selection = eSelection

		if(selection):
			self.companyListBox.delete(selection)
			self.startDateListBox.delete(selection)
			self.endDateListBox.delete(selection)
			del self.companiesAdded[int(selection[0])]
			del self.startDatesAdded[int(selection[0])]
			del self.endDatesAdded[int(selection[0])]
		else:
			return 0



	def retrieveData(self):
		if(len(self.companiesAdded) > 0):
			tempData = []

			messageDict = {'type':'gui_tweet_pull', 'companies':self.companiesAdded, 'start_dates':self.startDatesAdded, 'end_dates':self.endDatesAdded}
			message = json.dumps(messageDict)
			socket = self.createSocket()
			socket.send(message)
			message = socket.recv()
			rcvd = json.loads(message)

			self.createCompanyInfoObjects(rcvd)
			self.displayCompanyInfo()

		else:
			return 0
		


	def refreshCompanyList(self):
		dict = {'type': 'gui_get_companies'}
		list = self.refreshListFromDB(dict)

		return list


	def refreshDateList(self):
		company = self.listVariableCompany.get().lower()
		dict = {'type': 'gui_get_dates', 'company': company}
		list = self.refreshListFromDB(dict)

		return list


	def refreshListFromDB(self, messageDict):
		tempData = []
		message = json.dumps(messageDict)
		socket = self.createSocket()
		socket.send(message)
		message = socket.recv()
		rcvd = json.loads(message)
		for r in rcvd:
			tempData.append(r.title())

		return tempData


	def onCompanySelect(self):
		currentCompany = self.listVariableCompany.get()
		if(self.previousSelectedCompany != currentCompany):
			newDates = self.refreshDateList()
			sMenu = self.startDateDrop['menu']
			sMenu.delete(0, END)
			eMenu = self.endDateDrop['menu']
			eMenu.delete(0, END)

			for nd in newDates:
				sMenu.add_command(label=nd, command=lambda v=self.listVariableStartDate, l=nd: v.set(l))
				eMenu.add_command(label=nd, command=lambda v=self.listVariableEndDate, l=nd: v.set(l))
			
			self.listVariableStartDate.set(newDates[0])
			self.listVariableEndDate.set(newDates[0])

			self.previousSelectedCompany = currentCompany

		self.parent.after(250, self.onCompanySelect)

	
	def showStockGraph(self, company, daterange):
		## retreive stock dataset
		print daterange
		dataset = {'type' : 'stock_pull', 'symbol' : TICKER_SYMBOL_DICT[company], 'clientname' : 'graphanalysis_test'}
		message = json.dumps(dataset)
		socket = self.createSocket()
		socket.send(message)
    
		message = socket.recv()
		rcvd = json.loads(message)

		stk = g.graphanalysis(rcvd, 'stock')
		stk.interpolate(10)
		#dt = datetime(2013,4,4)
		stk.run_plot()

		return 0

	
	def showTweetGraph(self, company, daterange):
		print daterange
		dataset = {'type' : 'avgSentiment_pull', 'symbol' : company.lower(), 'dateRange' : 'doesntmatter', 'clientname' : 'graphanalysis_test'}
		message = json.dumps(dataset)
		socket = self.createSocket()
		socket.send(message)

		message = socket.recv()
		rcvd = json.loads(message)

		twt = g.graphanalysis(rcvd, 'tweet')
		#dt = datetime(2013,4,4)
		twt.run_plot()

		return 0


	def showCorrelationGraph(self, company, daterange):
		## retreive stock dataset
		print daterange
		dataset = {'type' : 'stock_pull', 'symbol' : company.lower(), 'clientname' : 'graphanalysis_test'}
		message = json.dumps(dataset)
		socket = self.createSocket()
		socket.send(message)
    
		message = socket.recv()
		rcvd = json.loads(message)

		stk = g.graphanalysis(rcvd, 'stock')
		stk.interpolate(10)

		dataset = {'type' : 'avgSentiment_pull', 'symbol' : company.lower(), 'dateRange' : 'doesntmatter', 'clientname' : 'graphanalysis_test'}
		message = json.dumps(dataset)
		socket = self.createSocket()
		socket.send(message)

		message = socket.recv()
		rcvd = json.loads(message)

		twt = g.graphanalysis(rcvd, 'tweet')

		print twt.starts_within(stk)
		print stk.starts_within(twt)
		#dt = datetime(int(daterange[0:4]),int(daterange[5:7]),int(daterange[8-10]))
		dt = datetime(2013,4,4)
		stk.run_plot(8, stk.get_date_loc(dt))

		return 0



	def companyInfoBack(self):
		self.hideCompanyInfo()
		self.displayMainMenu()


	def createSocket(self):
		context = zmq.Context()
		socket = context.socket(zmq.REQ)
		socket.connect("tcp://%s:5555" % (self.address))

		return socket




	class ListView:
		
		def __init__(self, app, company, numTweets, posTweets, negTweets, rowOffset=0, startDate=0):
			self.app = app
			self.parent = app.parent
			self.company = company
			self.numTweets = numTweets
			self.posTweets = posTweets
			self.negTweets = negTweets
			self.rowOffset = rowOffset
			self.startDate = startDate

			self.createDisplayObjects()

		def createDisplayObjects(self):
			self.backgroundLabel = Label(self.parent, text="")
			self.companyLabel = Label(self.parent, text=self.company)
			self.tweetsLabel = Label(self.parent, text="Tweets: %s" % (self.numTweets))
			self.posTweetsLabel = Label(self.parent, text="Pos: %s" % (self.posTweets))
			self.negTweetsLabel = Label(self.parent, text="Neg: %s" % (self.negTweets))
			self.stockGraphButton = Button(self.parent, text="Stock Graph", command=self.showStockGraph)
			self.tweetGraphButton = Button(self.parent, text="Tweet Graphs", command=self.showTweetGraph)
			self.correlationGraphButton = Button(self.parent, text="Correlation Graph", command=self.showCorrelationGraph)

		def display(self):
			row = 2*self.rowOffset
			self.backgroundLabel.grid(row=row, column=0, columnspan=5, rowspan=2, padx=(25,0), pady=(15,0), stick=N+S+W+E)
			self.companyLabel.grid(row=row, column=0, columnspan=1, rowspan=1, padx=(25,0), pady=(15,0), sticky=W+N)
			self.tweetsLabel.grid(row=row+1, column=1, columnspan=1, rowspan=1, padx=5, sticky=W+N)
			self.posTweetsLabel.grid(row=row+1, column=2, columnspan=1, rowspan=1, padx=5, sticky=W+N)
			self.negTweetsLabel.grid(row=row+1, column=3, columnspan=1, rowspan=1, padx=5, sticky=W+N)
			self.stockGraphButton.grid(row=row, column=4, columnspan=1, rowspan=1, padx=5, pady=(15,0), sticky=W+N)
			self.tweetGraphButton.grid(row=row, column=3, columnspan=1, rowspan=1, padx=5, pady=(15,0), sticky=W+N)
			self.correlationGraphButton.grid(row=row, column=2, columnspan=1, rowspan=1, padx=5, pady=(15,0), stick=W+N)

		def forget(self):
			self.backgroundLabel.grid_forget()
			self.companyLabel.grid_forget()
			self.tweetsLabel.grid_forget()
			self.posTweetsLabel.grid_forget()
			self.negTweetsLabel.grid_forget()
			self.stockGraphButton.grid_forget()
			self.tweetGraphButton.grid_forget()
			self.correlationGraphButton.grid_forget()

		def showStockGraph(self):
			self.app.showStockGraph(self.company, self.startDate)

		def showTweetGraph(self):
			self.app.showTweetGraph(self.company, self.startDate)

		def showCorrelationGraph(self):
			self.app.showCorrelationGraph(self.company, self.startDate)



def main():

	if(len(sys.argv) < 2):
		mainAddress = "localhost"
	elif(len(sys.argv) > 2):
		print "Usage: GoldmineGUI.py [ADDR]"
	else:
		mainAddress = sys.argv[1]

	print "Address: %s" % (mainAddress)

	root = Tk()
	
	image = Image.open("res/TWAHOO_Finance_Background.jpg")
	background = ImageTk.PhotoImage(image=image)
	backgroundLabel = Label(root, image=background)
	backgroundLabel.place(x=0, y=0)

	width = background.width()
	height = background.height()

	root.geometry('%dx%d+0+0' % (width, height))
	root.resizable(0,0)

	app = Application(root, mainAddress)

	root.after(250, app.onCompanySelect)
	root.mainloop()
	sys.exit(0)


if __name__=='__main__':
	main()
