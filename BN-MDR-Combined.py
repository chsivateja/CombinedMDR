from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import xlwings as xw
import string
import re
import math
import datetime
import logging
import urllib.request, urllib.error, urllib.parse
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib.animation as animation
import matplotlib
import pylab
import threading
import pandas as pd


# Python program to find Excel column name from a  
# given column number 
MAX = 50 
ColumnCounter = 0
previousVolume = 0


xarray=[]
yarray=[]
nifty50mdrArray = []
nifty50_FO_mdrArray = []

nifty_MDR_delta = []

InstiDeltaArray = []
InstiCummilativeBuy = 0

nifty50_DeltaCash_Array = []
nifty50_DeltaFNO_Array = []

lastPriceArray = []

isTickreceived = [0]*50
MDR_Shares = [0]*12
MDR_FO = [0]*12
CumDelta_Cash= [0]*12
CumDelta_FNO= [0]*12
sripsFortickdata = []
sripsweightage = []
FOsripsFortickdata = []
Lot_Size = []
lock = threading.Lock()

def marketDepth(company_data):
	#global previousVolume,currentVolume
	global ColumnCounter
	global xarray,yarray,nifty50mdrArray,nifty50_FO_mdrArray
	global sripsFortickdata,sripsweightage,MDR_Shares,MDR_FO,FOsripsFortickdata,Lot_Size
	global InstiDeltaArray,InstiCummilativeBuy,CumDelta_Cash,CumDelta_FNO,nifty50_DeltaCash_Array,nifty50_DeltaFNO_Array,nifty_MDR_delta

	if (company_data['depth']['sell'][0]['price'] != 0) and (company_data['depth']['buy'][0]['price'] != 0 ):
		if company_data['instrument_token'] == 11615490 :
			ColumnCounter += 1

			xarray.append(ColumnCounter)
			mdr_index = (company_data['buy_quantity'] - company_data['sell_quantity'])/(company_data['buy_quantity'] + company_data['sell_quantity'])*100
			yarray.append(mdr_index )
			InstiBuy = ((company_data['depth']['buy'][0]['quantity'])/(company_data['depth']['buy'][0]['orders']))/20
			if InstiBuy > 10:
				InstiCummilativeBuy = InstiCummilativeBuy + InstiBuy
			InstiSell = ((company_data['depth']['sell'][0]['quantity'])/(company_data['depth']['sell'][0]['orders']))/20
			if InstiSell > 10:
				InstiCummilativeBuy = InstiCummilativeBuy - InstiSell
			InstiDeltaArray.append(InstiCummilativeBuy)

			lastPriceArray.append(company_data['last_price'])

			totalMdr = 0.0
			total_FO_Mdr = 0.0
			total_Delta_Cash = 0.0
			total_Delta_FNO = 0.0

			for mdr,FO_mdr, Delta_Cash, Delta_FNO, weight in zip(MDR_Shares, MDR_FO, CumDelta_Cash, CumDelta_FNO, sripsweightage):
				#print(mdr,weight,totalMdr)
				totalMdr = totalMdr+ mdr*weight/100
				total_FO_Mdr = total_FO_Mdr+ FO_mdr*weight/100

				total_Delta_Cash = total_Delta_Cash + Delta_Cash*weight /100
				total_Delta_FNO = total_Delta_FNO + Delta_FNO*weight /100

			nifty50mdrArray.append(totalMdr)
			nifty50_FO_mdrArray.append(total_FO_Mdr)
			nifty_MDR_delta.append(totalMdr - mdr_index)

			nifty50_DeltaCash_Array.append(total_Delta_Cash)
			nifty50_DeltaFNO_Array.append(total_Delta_FNO)

		else:
			x=0
			for FOtoken, token, weight, lot in zip(FOsripsFortickdata, sripsFortickdata, sripsweightage,Lot_Size):
				#print(token,lot)
				if company_data['instrument_token'] == token:
					print(token,weight)
					MDR_Shares[x] = (company_data['buy_quantity'] - company_data['sell_quantity'])/(company_data['buy_quantity'] + company_data['sell_quantity'])*100

					InstiBuy = 0.0
					InstiSell = 0.0
					InstiBuy = ((company_data['depth']['buy'][0]['quantity'])/(company_data['depth']['buy'][0]['orders']))/lot
					#if InstiBuy > 0:
					CumDelta_Cash[x] = CumDelta_Cash[x] + InstiBuy
					InstiSell = ((company_data['depth']['sell'][0]['quantity'])/(company_data['depth']['sell'][0]['orders']))/lot
					#if InstiSell > 0:
					CumDelta_Cash[x] = CumDelta_Cash[x] - InstiSell

					#print(MDR_Shares[x])
					break
				elif company_data['instrument_token'] == FOtoken:
					print(FOtoken,weight)
					MDR_FO[x] = (company_data['buy_quantity'] - company_data['sell_quantity'])/(company_data['buy_quantity'] + company_data['sell_quantity'])*100
					#print(MDR_FO[x])
					InstiBuy = 0.0
					InstiSell = 0.0
					InstiBuy = ((company_data['depth']['buy'][0]['quantity'])/(company_data['depth']['buy'][0]['orders']))/lot
					#if InstiBuy > 0:
					CumDelta_FNO[x] = CumDelta_FNO[x] + InstiBuy
					InstiSell = ((company_data['depth']['sell'][0]['quantity'])/(company_data['depth']['sell'][0]['orders']))/lot
					#if InstiSell > 0:
					CumDelta_FNO[x] = CumDelta_FNO[x] - InstiSell
					break					
				x=x+1

def plotGraph():
	global xarray,yarray,nifty50mdrArray,nifty50_FO_mdrArray
	global InstiDeltaArray,nifty50_DeltaCash_Array,nifty50_DeltaFNO_Array,nifty_MDR_delta
	fig = plt.figure()
	plt.ion()

	ax1 = plt.subplot(3,1,1)
	ax1.grid(True)

	ax2 = plt.subplot(3,1,2)
	ax2.grid(True)

	ax3 = plt.subplot(3,1,3)
	ax3.grid(True)

	while True:
		if len(xarray) > 0:
			ax1.clear()
			ax2.clear()
			ax3.clear()
			
			ax2.plot(xarray,yarray, label='MDR')
			ax2.plot(xarray[-1], yarray[-1], 'og')

			ax2.plot(xarray,nifty50mdrArray,color='orange', label='Nifty50MDR')
			ax2.plot(xarray[-1], nifty50mdrArray[-1], 'og')

			ax2.plot(xarray,nifty50_FO_mdrArray,color='pink', label='nifty50_FO_mdrArray')
			ax2.plot(xarray[-1], nifty50_FO_mdrArray[-1], 'or')

			ax2.plot(xarray,nifty_MDR_delta,color='magenta', label='nifty_MDR_delta')
			ax2.plot(xarray[-1], nifty_MDR_delta[-1], 'or')

			ax1.plot(xarray,lastPriceArray, label='Price')
			ax1.plot(xarray[-1], lastPriceArray[-1], 'og')

			ax3.plot(xarray,InstiDeltaArray, label='InstiAction')
			ax3.plot(xarray[-1], InstiDeltaArray[-1], 'og')

			ax3.plot(xarray,nifty50_DeltaCash_Array,color='orange', label='Nifty50 Insti')
			ax3.plot(xarray[-1], nifty50_DeltaCash_Array[-1], 'ob')

			ax3.plot(xarray,nifty50_DeltaFNO_Array,color='pink', label='nifty50 FNO Insti')
			ax3.plot(xarray[-1], nifty50_DeltaFNO_Array[-1], 'or')

			#plt.gcf().autofmt_xdate()
			#plt.legend(loc='best')
			plt.show()
			plt.pause(1)


kws =""
kite=""
api_k = "5jy5w5xb5xkh82n3xa"
api_s = "gklfjq6nd7ngpcuvgfuiwwgbpkoh7pic"

user_id = "USERID"


instr ={}
NFOintr = {}
def getInstrumentToken(symbol):
	global instr
	for scrip in instr:
		if scrip['tradingsymbol'] == symbol:
			return scrip['instrument_token']

def getFOInstrumentToken(symbol):
	global NFOintr
	symbol = symbol + '19MARFUT'
	for scrip in NFOintr:
		if scrip['tradingsymbol'] == symbol:
			return scrip['instrument_token']

def getLotSize(symbol):
	global NFOintr
	symbol = symbol + '19MARFUT'
	#print(symbol)
	for scrip in NFOintr:
		if scrip['tradingsymbol'] == symbol:
			print(scrip['tradingsymbol'])
			print(scrip['lot_size'])
			return scrip['lot_size']

def get_login(api_k, api_s):
	global instr,isTickreceived,NFOintr
	global kws, kite,sripsFortickdata,FOsripsFortickdata
	kite = KiteConnect(api_key=api_k)
	print("[*] Generate access Token : ", kite.login_url())
	request_tkn = input( "[*]Enter you request tocken here: ");
	data = kite.generate_session(request_tkn, api_secret=api_s )
	kite.set_access_token(data["access_token"])
	kws = KiteTicker(api_k, data["access_token"])
	instr = kite.instruments("NSE") 
	NFOintr = kite.instruments("NFO") 

	print(len(instr))
	'''for scrip in instr:
		print(scrip['tradingsymbol'])'''

	df = pd.read_csv("D:\\Dev_Folder\\BankNifty.csv",usecols=['stocks', 'weightage']) 

	df['instrument_token'] = df['stocks'].apply(getInstrumentToken)
	df['FOinstrument_token'] = df['stocks'].apply(getFOInstrumentToken)
	df['LotSize'] = df['stocks'].apply(getLotSize)
	for index, row in df.iterrows():
		#print (row["stocks"], row["instrument_token"])
		sripsFortickdata.append(row["instrument_token"])
		sripsweightage.append(row["weightage"])
		FOsripsFortickdata.append(row["FOinstrument_token"])
		Lot_Size.append(row["LotSize"])

	#sripsFortickdata = df['instrument_token'][:]
	#print(sripsFortickdata)
	'''x=0
	for token, weight in zip(sripsFortickdata, sripsweightage):
		isTickreceived[x] =1
		print(token,weight)
		x=x+1
	print(isTickreceived)'''




get_login(api_k, api_s)
t1= threading.Thread(target=plotGraph)
t1.start()
#write_here = xw.Book('BankNifty.xlsx')
#BankNifty=write_here.sheets['BN']

# Initialise

def on_ticks(ws, ticks):  # noqa
	global xarray,yarray,zarray,BidArray,AskArray
    # Callback to receive ticks.
	for company_data in ticks:
		#print(company_data)
		#bookmap(company_data)
		marketDepth(company_data)



def on_connect(ws, response):  # noqa
	global sripsFortickdata,FOsripsFortickdata
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    #ws.subscribe([9029378,3861249,60417,1510401,4267265])
	print(len(sripsFortickdata))
	print(sripsFortickdata)
	listofinstrument_tokens = sripsFortickdata[:]
	listofinstrument_tokens.append(11615490)
	listofinstrument_tokens = listofinstrument_tokens + FOsripsFortickdata
	print(len(listofinstrument_tokens))
	ws.subscribe(listofinstrument_tokens)

    # Set RELIANCE to tick in `full` mode.
    #ws.set_mode(ws.MODE_FULL, [9029378,3861249,60417,1510401,4267265])
	ws.set_mode(ws.MODE_FULL, listofinstrument_tokens)


# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect()
#kws = WebSocket(api_key, public_tocken, user_id )
'''
def get_login(api_k, api_s):
	global kws, kite
	kite = KiteConnect(api_key-api_k)
	print("[*] Generate access Token : ", kite.login_url())



def on_tick(tick, ws):
    print(tick, "/n")
    '''