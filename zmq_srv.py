"""
 A server to handle pushes and pulls of stock and tweet information.
 Binds REP socket to tcp://*:5555
 Expects a type from the client and will send a confirmation reply accordingly.
"""

import zmq
import time
import sqlite3
import getyql
import json
import pprint


#connect to zmq
print("trying to connect")
# Connect to the zmq server.

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
 
# Connect to the database.
sdb = getyql.simpledb()
c = sdb.conn.cursor()

print("Connected")

# Have the server run forever.
while True:
	
    # Wait for the next request from the client and load the message.

    message = socket.recv()
    print "Recieved message: ", message,"\n"
    rcvd = json.loads(message)

    # interpret the query and run database operation
    # Interpret the query based on its type value. The run the database operation accordingly.
    if rcvd['type'] == "stock_push":
      # did we receive a raw stock value to store?
      print "stock push request received for %s from %s" % (rcvd['symbol'], rcvd['clientname'])
      c.execute("INSERT INTO stocks VALUES (NULL, '%s', '%s', '%s')" % (rcvd['timestamp'], rcvd['symbol'], rcvd['price']))
      sdb.conn.commit()
      print "added %s into database" % rcvd['symbol']
      socket.send("Ack")

    # Handler for stock_pull type.
    elif rcvd['type'] == "stock_pull":
      print "stock pull request received for %s from %s" % (rcvd['symbol'], rcvd['clientname'])
      pulled_stocks = []

      for row in c.execute("select * from stocks"):
          print row

      for row in c.execute("SELECT * FROM stocks WHERE symbol = '%s' order by timestamp" % rcvd['symbol']):
          pulled_stocks.append(row)
      message = json.dumps(pulled_stocks)
      socket.send(message)

    # Handler for tweet_push type.
    elif rcvd['type'] == "tweet_push":

        # Inserts into the database: 
        #    1. Date
        #    2. Company
        #    3. Sentiment
        #    4. ID
        #    5. Text of tweet
        c.execute("INSERT INTO tweets VALUES(NULL,?,?,?,?,?)",(rcvd['date'], rcvd['company'], rcvd['sentiment'], rcvd['id'], rcvd['tweet']))

        sdb.conn.commit()
        socket.send("Ack")
        
    # Handler for tweet_pull type, for tweet_trender.
    elif rcvd['type'] == "tweet_pull":
        print "recieved query for %s" % (rcvd['company'])
        pulled_tweets = []
        
        for row in c.execute("SELECT * FROM tweets WHERE company = '%s'" % (rcvd['company'])):
            #if ((int(row[1][8:10]) == int(rcvd['dateRange'][8:10])) and (int(row[1][0:4]) == int(rcvd['dateRange'][0:4])) and (int(row[1][5:7]) == int(rcvd['dateRange'][5:7]))):
	    pulled_tweets.append(row)
        print "sending %d tweets to tweet_trender" % len(pulled_tweets)
        message = json.dumps(pulled_tweets)
        socket.send(message)
  
    elif rcvd['type'] == 'avgSentiment_push':
        pprint.pprint(rcvd)
        print "recieved push request for %s avgerage sentiment on %s" % (rcvd['company'], rcvd['dateRange'])
	c.execute("DELETE FROM trendPoints WHERE dateRange = '%s' and company = '%s'" % (rcvd['dateRange'], rcvd['company']))
        c.execute("INSERT INTO trendPoints VALUES(NULL, '%s', '%s', '%d', '%d', '%d', '%d', '%d')" % (rcvd['dateRange'], rcvd['company'], rcvd['averageValue'], rcvd['positive'], rcvd['negative'], rcvd['neutral'], rcvd['dataVolume']))
        #'rcvd['dataType'],  rcvd['sentiment'], rcvd['volume']))
        sdb.conn.commit()
        print "Stored trendPoint into data base"
        socket.send("Ack")

    elif rcvd['type'] == 'avgSentiment_pull':
        print "recieved query for %s over the date range of %s" % (rcvd['symbol'], rcvd['dateRange'])
        pulled_sentiments = []

	for row in c.execute("select * from trendPoints"):
		print row
        
        for row in c.execute("SELECT trendID, dateRange, company, averageValue, positive, negative, neutral, dataVolume FROM trendPoints WHERE company = '%s'" % (rcvd['symbol'])):
            #if ((int(row[1][8:10]) == int(rcvd['dateRange'][8:10])) and (int(row[1][0:4]) == int(rcvd['dateRange'][0:4])) and (int(row[1][5:7]) == int(rcvd['dateRange'][5:7]))):
            pulled_sentiments.append(row)
        print "sending %d tweet sentiments to %s" % (len(pulled_sentiments), rcvd['clientname'])
        message = json.dumps(pulled_sentiments)
        socket.send(message)


    #---------------------------Aaron's additions-------------------
    #---------------------------------------------------------------
    
    #get list of companies to display
    elif rcvd['type'] == 'gui_get_companies':
	print "received query for list of companies"
	companyList = []
	
	for row in c.execute("select distinct company from tweets"):
		companyList.append(row[0])

        message = json.dumps(companyList)
        socket.send(message)


    #get dates for selected company
    elif rcvd['type'] == 'gui_get_dates':
	print "received query for list of dates"
	companyDates = []

	previouslyUsed = []
	for row in c.execute("select distinct timestamp from tweets where company = '%s'" % (rcvd['company'])):
		if(row[0][0:10] not in previouslyUsed):
			companyDates.append(row[0][0:10])
			previouslyUsed.append(row[0][0:10])

	message = json.dumps(companyDates)
	socket.send(message)


    elif rcvd['type'] == 'gui_tweet_pull':
	print "recieved query for tweet pull"
	tweetInfo = {}

	for i in range(len(rcvd['companies'])):
		start = rcvd['start_dates'][i-1]
		end = rcvd['end_dates'][i-1]

		startSum = int(start[0:4])*1000 + int(start[5:7])*10 + int(start[8:10])
		endSum = int(end[0:4])*1000 + int(end[5:7])*10 + int(end[8:10])

		tweetInfo[rcvd['companies'][i-1]] = []
		pos = 0
		neg = 0
		neu = 0
		total = 0

		for row in c.execute("select * from tweets where company = '%s'" % (rcvd['companies'][i-1].lower())):
			rowSum = int(row[1][0:4])*1000 + int(row[1][5:7])*10 + int(row[1][8:10])
			if(rowSum >= startSum and rowSum <= endSum):
				if(row[3] == 'pos'):
					pos = pos+1
				elif(row[3] == 'neg'):
					neg = neg+1
				else:
					neu = neu+1

				total = total+1

		#do not plan on displaying neutral, implied


		tweetInfo[rcvd['companies'][i-1]].append(total)
		tweetInfo[rcvd['companies'][i-1]].append(pos)
		tweetInfo[rcvd['companies'][i-1]].append(neg)

	print tweetInfo
	message = json.dumps(tweetInfo)
	socket.send(message)
	

    #-------------------------End of Aaron's Changes-------------
    #--------------------------------------------------------------




    else:
        # Send reply back to client that the query is unspecified.
        print "received unknown query, ignoring"
        socket.send("Ack")



