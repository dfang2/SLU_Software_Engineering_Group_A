import time
import json
import zmq
import sys
import pprint
import numpy as np
import string as st
import matplotlib.pyplot as plt
import datetime
import matplotlib
from matplotlib.finance import candlestick
from matplotlib.dates import num2date
from matplotlib.dates import date2num
if __name__ == "__main__":
  if len(sys.argv) < 3:
    print "usage: zmq_stockpull.py ADDR TICKER [TICKER TICKER...]"

    pprint.pprint(sys.argv)
    exit()


  tickers = []

  for itr in range( len(sys.argv)-2 ):
    tickers.append(sys.argv[itr+2])

  # connect to zmq
  context = zmq.Context()

  socket = context.socket(zmq.REQ)
  addr = ("tcp://%s:5555" % sys.argv[1])
  print "connecting to server %s" % addr
  socket.connect ( addr )

  for stock in tickers:

    # format data package
    dataset = {'type' : "stock_pull", 'symbol' : stock, 'clientname' : 'Steve'}
    message = json.dumps(dataset)
    pprint.pprint(dataset)

    # send data package
    print "Requesting data for ticker ", stock, "..."
    socket.send(message)

    # wait for reply
    message = socket.recv()
    print "Received reply for ticker ", stock

    # print retreived st5ocks
    rcvd = json.loads(message)    
    #pprint.pprint(rcvd)

    arr = np.array([0,0,0,0])

    for row in rcvd:
      if st.find(row[1], "avg")>0:
        pass
        #print "ignoring average value"
        #arr = np.vstack((arr, [row[0], row[1], row[2], row[3]]))
      else:
        arr = np.vstack((arr, [row[0], row[1], row[2], row[3]]))
      """
      if st.find(row[1], "high")>0:
        print "ignoring high value"
      elif st.find(row[1], "low")>0:
        print "ignoring low value"
      else:
        arr = np.vstack((arr, [row[0], row[1], row[2], row[3]]))
      """
    print 'arr', arr[:50]
    print len(arr)
   # print arr[-30:]
    getline = [] # store the date+type
    getDate = []
    getBegin = []
    getClose = []
    getHigh = []
    getLow = []
    j = -1 # set the number of array
    for i in range (70):
   # for i in range (len(arr)):
        getline.append(arr[i][1])
        if st.find(getline[i],"09:30")>0:
            j = j + 1    
            seprate = getline[i].split()
            print seprate[0]
            getDate.append(seprate[0])
            getBegin.append(arr[i][3])
        elif st.find(getline[i],"16:00")>0:
            if (j == -1):
                j = 0
            getClose.append(arr[i][3])
        elif st.find(getline[i], "high")>0:
            if (j == -1):
                j = 0
            getHigh.append(arr[i][3])
        elif st.find(getline[i], "low")>0:
            if (j == -1):
                j = 0
            getLow.append(arr[i][3])
    Highest = float(max(getHigh))
    Lowest = float(min(getLow))
    print Highest, Lowest
    dataout = []
    #print date2num(datetime.datetime.strptime(getDate[1],'%Y-%m-%d').date())
    for i in range (10):
       dataout.append([date2num(datetime.datetime.strptime(getDate[i],'%Y-%m-%d').date()),float(getBegin[i]),float(getClose[i]),float(getHigh[i]),float(getLow[i])])
    data = np.array(dataout)
    print 'data',data
    # determine number of days and create a list of those days
    ndays = np.unique(np.trunc(data[:,0]), return_index=True)
    #print ndays
    xdays = []
    for n in np.arange(len(ndays[0])):
        xdays.append(datetime.date.isoformat(num2date(data[ndays[1],0][n])))
    
    
    # creation of new data by replacing the time array with equally spaced values.
    # this will allow to remove the gap between the days, when plotting the data
    data2 = np.hstack([np.arange(data[:,0].size)[:, np.newaxis], data[:,1:]])
    print 'data2',data2
    # plot the data
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_axes([0.1, 0.2, 0.85, 0.7])
        # customization of the axis
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.tick_params(axis='both', direction='out', width=2, length=8,
                   labelsize=12, pad=8)
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
        # set the ticks of the x axis only when starting a new day
    ax.set_xticks(data2[ndays[1],0])
    ax.set_xticklabels(xdays, rotation=45, horizontalalignment='right')
    
    ax.set_ylabel('Quote ($)', size=20)
    ax.set_ylim([Lowest, Highest])
    
    candlestick(ax, data2, width=0.5, colorup='g', colordown='r')
    
    plt.show()
    
