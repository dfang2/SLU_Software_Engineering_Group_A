# Retreives data using YQL
#
# Steve Massey - 1/21/13
#
# resources used:
# http://stackoverflow.com/questions/7625079/download-csv-directly-into-python-csv-parser
# http://stackoverflow.com/questions/376461/string-concatenation-vs-string-substitution-in-python
# http://code.google.com/p/yahoo-finance-managed/wiki/csvQuotesDownload
# may need http://stackoverflow.com/questions/1695183/how-to-percent-encode-url-parameters-in-python

import simplejson as json
import urllib2
import pprint
import datetime
import cStringIO
import csv
import httplib2
import yql
import time
import sqlite3
from datetime import date 

class simpledb:
  def __init__(self):
    # constructor, open our connection
    self.conn = sqlite3.connect("sample.db")

  def newdb(self):
    # Instantiate the database
    c = self.conn.cursor()
    c.execute('''CREATE TABLE stocks
                  (id INTEGER PRIMARY KEY, timestamp TEXT, symbol TEXT, price REAL)''')

    c.execute('''CREATE TABLE tweets (tweetsID INTEGER PRIMARY KEY, timestamp TEXT, company TEXT, sentiment TEXT, id TEXT, tweet TEXT)''')
  
    c.execute('''CREATE TABLE trendPoints
                  (trendID INTEGER PRIMARY KEY, dateRange TEXT, company TEXT, averageValue INTEGER, positive INTEGER, negative INTEGER, neutral INTEGER, dataVolume INTEGER)''')

    c.execute('''CREATE TABLE trendMap
                  (trendID INTEGER, tweetID INTEGER)''')
    
    c.execute('''CREATE TABLE subTrendMap
                  (trendID INTEGER, subTrendID INTEGER)''')
    self.conn.commit()

  def execute(self, query):
    # execute a query
    # string query: query to execute
    c = self.conn.cursor()

  def __del__(self):
    # destructor, close our connection
    self.conn.close()

class getyql:
  def __init__(self):
    # set up a few global variables for our object
    self.y = yql.Public()
    self.pre_query = "use \"http://www.datatables.org/yahoo/finance/yahoo.finance.quotes.xml\" as yahoo.finance.quotes; "

  def Instant(self, ticker):
    ## import instant quote, uses sql library
    ## yql y;         yql connection object
    ## string ticker; ticker symbol
    query = "select symbol, AskRealtime, LastTradeTime from yahoo.finance.quotes where symbol in (\"%s\")" % ticker
    print "executing '%s'" % query
    result = self.y.execute((self.pre_query+query) )
    return result.rows

  def CSVGrab(self, ticker, start, stop, intv):
    ## import CSV historical quote data
    ## http://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
    ## string ticker; ticker symbol, string format
    ## date start;    start date of data to get, date object
    ## date stop;     end date of data to get, date object
    url = "http://ichart.yahoo.com/table.csv?s=%s&a=%i&b=%i&c=%i&d=%i&e=%i&f=%i&d=%s" % (ticker, (start.month-1), start.day, start.year, (stop.month-1), stop.day, stop.year, intv)
    h = httplib2.Http('.cache')
    headers, data = h.request(url)
    return data

if __name__ == "__main__":
  # todo: how to merge datasets. Yahoo only has day-by-day resolution
  # would be nice to have something with hour-by-hour at least?
  # our object
  y = getyql()
  """
  # demonstrate historical download
  d1 = datetime.date(2012,1,1)
  d2 = datetime.date(2012,6,1)
  out = y.CSVGrab('GOOG',d1,d2,'d')
  out = cStringIO.StringIO(out)

  sheet = csv.reader(out)
  for row in sheet:
    print row

  ## instant
  t0 = time.clock()
  result = y.Instant("GOOG")
  timestamp = time.time()
  t1 = time.clock() - t0
  print result[0]["AskRealtime"]
  print result[0]["symbol"]
  print "done in %f cpu seconds" % t1
  t2 = time.clock() - t0
  print "shown in %f cpu seconds" % t0
  """
  print
  print "now trying the database"
  sdb = simpledb()
  try:
    sdb.newdb()
    print "new database created" 
  except sqlite3.OperationalError:
    print "caught trying to make a new database; excepting"

  c = sdb.conn.cursor()
  
  #c.execute("INSERT INTO stocks VALUES (NULL, %d, '%s', '%s')" % (timestamp, result[0]["symbol"], result[0]["AskRealtime"]))
  #sdb.conn.commit()

  
  #print "**** dropping trend points"
  #c.execute('''DROP TABLE trendPoints''')
  #print "**** adding trendPoints"
  #c.execute('''CREATE TABLE trendPoints
  #            (trendID INTEGER PRIMARY KEY, dateRange TEXT, company TEXT, averageValue INTEGER, positive INTEGER, negative INTEGER, neutral INTEGER, dataVolume INTEGER)''')

  print "printing tweets: "
  for row in c.execute("SELECT * FROM tweets"):
    print row

  print "printing trendPoints: "
  for row in c.execute("SELECT * FROM trendPoints"):
    print row
