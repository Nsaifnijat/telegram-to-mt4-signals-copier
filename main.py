
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
import csv
#from functools import reduce
import numpy as np
import sys
from os.path import join
import json
from threading import Thread

from PyQt5.uic import loadUi
import asyncio
from PyQt5.QtWidgets import QDialog, QApplication, QWidget,QMainWindow


from telethon import TelegramClient, events, sync, client, utils
import phonenumbers
from PyQt5.QtCore import QThread, QObject
import sqlite3
from dwx_client import dwx_client

from functions import *
import datetime as dt
import config
api_id = config.api_id
api_hash = config.api_hash

client = TelegramClient('gui/session', api_id, api_hash)    
client.connect()
conn=sqlite3.connect('gui/employee.db')
c=conn.cursor()


def users_table():
    c.execute('''
            CREATE TABLE users(
              Server   text,
              LoginID text,
              Suffix   text
                )
            ''')
def defaults_table():
    c.execute('''
            CREATE TABLE defaults(
              fxvolume   integer,
              fxslippage integer,
              indexvolume   integer,
              indexslippage integer,
              comvolume integer,
              comslippage integer
                )
            ''')
    c.execute("INSERT INTO defaults VALUES(:fxvol,:fxslip,:indexvol,:indexslip,:comvol,:comslip)",
            {'fxvol':0.01,'fxslip':0.01,'indexvol':0.01,'indexslip':0.01 ,'comvol':0.01 ,'comslip': 0.01 })
    conn.commit()
def symbols_volume():
    c.execute('''
            CREATE TABLE symbol_volume(
              symbol   text,
              volume integer,
              slippage integer
                )
            ''')
forexsym = ['EURUSD','GBPUSD','EURGBP','USDCAD','NZDUSD','AUDUSD','AUDCAD','AUDCHF','AUDGBP','AUDNZD','NZDCAD',
                    'CADCHF','EURCAD','EURCHF','EURAUD','GBPAUD','GBPNZD','GBPCAD','USDCHF','GBPCHF','NZDCHF',
                    'EURNZD','AUDJPY','GBPJPY','CADJPY','CHFJPY','EURJPY','NZDJPY','USDJPY','EURMXN','EURNOK','EURSEK','EURTRY',
                    'GBPMXN','GBPNOK','GBPSEK','GBPTRY','USDHKD','USDMXN','USDNOK','USDSEK','USDSGD','USDTRY']

indexsym = ['US30','DJ30','DOW','RUSSEL 2000','DOW JONES 30','NAS100','US100','NASDAQ','SPX','S&P500','AUS200','SPY','US500','STOXX50E','SPX500','DE30','FR40','HK50','STOXX50','USTEC']
comsym = ['USOIL','UKOIL','XAGUSD','XNGUSD','BRENT','XAUUSD']
"""
with open("gui/forex.csv","a",encoding='UTF-8') as f:
    writer = csv.writer(f,delimiter=",",lineterminator="\n")
    # First write the headers
    writer.writerow(forexsym)"""
def exclude_table():
    c.execute('''
            CREATE TABLE exclude_symbols(
              symbol   text
                )
            ''')

def symbols_table():
    c.execute('''
            CREATE TABLE all_symbol(
              symbol   text
                )
            ''')

def Trailer_table():
    print('its trailer')
    c.execute('''
            CREATE TABLE trailer(
              fxdef   integer,
              fxtrail integer,
              fxdistance  integer,
              fxcus   integer,
              inddef   integer,
              indtrail integer,
              inddistance  integer,
              indcus   integer,
              comdef   integer,
              comtrail integer,
              comdistance  integer,
              comcus   integer
                )
            ''')
    print('trailer created')

def partials_table():
    c.execute('''
            CREATE TABLE partials(
              forexp   integer,
              indexp    integer,
              comp  integer
                )
            ''')
    c.execute("INSERT INTO partials VALUES(:forexp,:indexp,:comp)",
                    {'forexp':0.01,'indexp':0.01,'comp':0.01})
    conn.commit()

try:
    defaults_table()
    partials_table()
    exclude_table()
    symbols_volume()
    Trailer_table()
    users_table()
    

except:
    pass

with open("gui/telmsg.csv","a",encoding='UTF-8') as f:
    writer = csv.writer(f,delimiter=",",lineterminator="\n")
    # First write the headers
    writer.writerow(['FirstMSG','FirstmsgID','Firstmsgchat_title','chat_id','repltext','replid'])
#liast=[0,1,2,3,4]
executed_trades=pd.DataFrame(columns=['AccountID','MessageID','PositionID','SL','TP'])
#executed_trades.columns=['AccountID','MessageID','PositionID','SL','TP']
tpholder = pd.DataFrame(columns=['PosID','TPS'])

print(executed_trades)
class trail_sl(QObject):
    def __init__(self,ui,dwx):
        super().__init__()
        self.ui = ui
        self.dwx = dwx
        self.conn=sqlite3.connect('gui/employee.db')
        self.c=conn.cursor()
    def trail_starter(self):
        try:
            QApplication.sendPostedEvents()
            conn=sqlite3.connect('gui/employee.db')
            c=conn.cursor()
            c.execute('SELECT * FROM trailer')
            data=c.fetchall()
        
            
            fx_default = int(data[0][0])
            fx_trail = int(data[0][1])
            fx_max_dist = int(data[0][2])
            ind_default = int(data[0][4])
            ind_trail = int(data[0][5])
            ind_max_dist = int(data[0][6])
            c.execute('SELECT * FROM users')
            allAccounts =c.fetchall()
            for account in allAccounts:
                TrailFunc(fx_default,fx_trail,fx_max_dist,ind_default,ind_trail,ind_max_dist,account,self.ui,self.dwx)
            QApplication.processEvents()
        except:
            self.ui.generalErrors.setText('Please add your trailing settings or check if you have added an account!')
    def Tp_starter(self):
        QApplication.sendPostedEvents()
        
        while True:
            if self.ui.stop_tp.isChecked():
                self.ui.start_trailing_tp.setText('Start Trailing by TP')
                break
            else:
                self.ui.start_trailing_tp.setText('Trailing by TP Started')
                conn=sqlite3.connect('gui/employee.db')
                d=conn.cursor()
                d.execute('SELECT * FROM users')
                allAccounts =d.fetchall()
                for user in allAccounts:
                    address = user[0]

                    symbols = []
                    tposition = self.dwx.open_orders.items()
                    for ticket, position in tposition:
                        symbols.append(position['symbol'])

                    self.dwx.subscribe_symbols(symbols)
                    time.sleep(1.5)
                    if len(tpholder) >0:
                        for ticket, position in tposition:
                            ticket= ticket
                            open_price=position['open_price']
                            tp = position['TP']
                            symbol = position['symbol']
                            
                            if position['type'] == 'buy':
                                curr_price= self.dwx.market_data[symbol]['bid']
                            else:
                                curr_price= self.dwx.market_data[symbol]['ask']
                            
                            filt=tpholder[tpholder['PosID']== position['magic']]
                            if len(filt) == 0:
                                continue
                            else:
                                tps = filt['TPS'].values[0]
                                for i in range(len(tps)):
                                    if position['type'] == 'buy':
                                        if curr_price > float(tps[i]):
                                            if tps[i] == tps[0]:
                                                update(ticket,open_price,tp,self.dwx)
                                                d.execute('SELECT * FROM partials')
                                                data2=d.fetchall()
                                                for dat in data2:
                                                    if symbol in forexsym:
                                                        volume= dat[0]
                                                    elif symbol in indexsym:
                                                        volume = dat[1]
                                                    elif symbol in comsym:
                                                        volume = dat[2]
                                                    else:
                                                        volume = 0.01
                                                closePartials(ticket,volume,self.dwx)
                                            else:
                                                update(ticket,float(tps[i-1]),tp,self.dwx)
                                                d.execute('SELECT * FROM partials')
                                                data2=d.fetchall()
                                                for dat in data2:
                                                    if symbol in forexsym:
                                                        volume= dat[0]
                                                    elif symbol in indexsym:
                                                        volume = dat[1]
                                                    elif symbol in comsym:
                                                        volume = dat[2]
                                                    else:
                                                        0.01
                                                closePartials(ticket,float(volume),self.dwx)
                                    else:
                                        if curr_price < float(tps[i]):
                                            if tps[i] == tps[0]:
                                                update(ticket,open_price,tp,self.dwx)
                                                d.execute('SELECT * FROM partials')
                                                data2=d.fetchall()
                                                for dat in data2:
                                                    if symbol in forexsym:
                                                        volume= dat[0]
                                                    elif symbol in indexsym:
                                                        volume = dat[1]
                                                    elif symbol in comsym:
                                                        volume = dat[2]
                                                    else:
                                                        volume = 0.01
                                                closePartials(ticket,volume,self.dwx)
                                            else:
                                                update(ticket,float(tps[i-1]),tp,self.dwx)
                                                d.execute('SELECT * FROM partials')
                                                data2=d.fetchall()
                                                for dat in data2:
                                                    if symbol in forexsym:
                                                        volume= dat[0]
                                                    elif symbol in indexsym:
                                                        volume = dat[1]
                                                    elif symbol in comsym:
                                                        volume = dat[2]
                                                    else:
                                                        0.01
                                                closePartials(ticket,float(volume),self.dwx)
            QApplication.sendPostedEvents()
            
    

class start_copying(QObject):
    #stop_event = pyqtSignal()
    def __init__(self,client,widgett,dwx):
        super().__init__()
        self.client=client
        self.ui =widgett
        self.dwx = dwx
    def start_event(self):
        try:
            QApplication.sendPostedEvents()
            asyncio.run(self.main())
            QApplication.processEvents()
        except BaseException as e : #sqlite3.OperationalError or ValueError:
            time.sleep(1)
            QApplication.sendPostedEvents()
            print('hey stop error happned',e)
            self.ui.startbtn.setEnabled(True)
            self.ui.startbtn.setText('Restart App')
            self.ui.channelsbtn.setEnabled(True)
            QApplication.processEvents()
       
           
    async def main(self):
        QApplication.sendPostedEvents()
        self.client.connect
        await self.client.disconnect()
       
        conn=sqlite3.connect('gui/employee.db')
        c=conn.cursor()
        async with TelegramClient('gui/session', api_id, api_hash) as client:
            username= await client.get_me()
            print(utils.get_display_name(username))
            try:
                with open('gui/alljang.csv', "r") as f:
                    reader = csv.reader(f, delimiter=",",lineterminator="\n")
                    for row in reader:
                        channelha = row
            except:
                self.ui.generalErrors.setText('Please add one channel or group at least!')
            @client.on(events.NewMessage(chats=channelha))
            async def my_event_handler(event):
                with open("gui/telmsg.csv","a",encoding='UTF-8') as f:
                    writer = csv.writer(f,delimiter=",",lineterminator="\n")    
                    try:
                        if event.is_reply:
                            repl=await event.get_reply_message()
                            base_text=repl.raw_text
                            base_text_id=repl.id 
                            reply_msg=event.raw_text
                            reply_msg_id=event.id
                            chat_from = event.chat if event.chat else (await event.get_chat()) # telegram MAY not send the chat enity
                            chat_title = chat_from.title
                            chat_id=chat_from.id
                            #totally=f'{chat_title,chat_id,base_text_id,reply_msg,reply_msg_id}'
                            #await client.send_message('freemium2', totally)
                            writer.writerow([base_text,base_text_id,chat_title,chat_id,reply_msg,reply_msg_id]) 
                            
                            trade,prices=parserepltext(reply_msg)
                            c.execute(f'SELECT * FROM users')
                            data=c.fetchall()
                            for mt in data:
                                serverAddress=mt[0]
                                accountID=mt[1]
                                filt=executed_trades[(executed_trades['AccountID']==accountID) & (executed_trades['MessageID']==base_text_id)]
                                pos_magic = int(filt['PositionID'].values[0])
                                #pos_ticket=int(executed_trades.loc[filt,'PositionID'].values[0])
                                pos_sl=filt['SL'].values[0]
                                pos_tp=filt['TP'].values[0]
                                #serverAddress =  'C:\\Users\Hamdard PC\\AppData\Roaming\\MetaQuotes\\Terminal\\6B8ECCBC538D1463C6775349E49C33B0\\MQL4\\Files'
                                
                                try:
                                    for tickat, order in self.dwx.open_orders.items():
                                        ticket = tickat
                                        magic = order['magic']
                                        if magic == pos_magic:
                                            pos_ticket = ticket
                                            break
                                    
                                finally:
                                    if 'partial' in trade:
                                        order = self.dwx.open_orders[str(pos_ticket)]
                                        symbol = order['symbol']
                                        if trade=='close partial':
                                            c.execute('SELECT * FROM partials')
                                            data2=c.fetchall()
                                            for dat in data2:
                                                if symbol in forexsym:
                                                    volume= dat[0]
                                                elif symbol in indexsym:
                                                    volume = dat[1]
                                                elif symbol in comsym:
                                                    volume = dat[2]
                                            closePartials(pos_ticket,float(volume),self.dwx)
                                        elif trade=='partial sl':
                                            c.execute('SELECT * FROM partials')
                                            data2=c.fetchall()
                                            for dat in data2:
                                                if symbol in forexsym:
                                                    volume= dat[0]
                                                elif symbol in indexsym:
                                                    volume = dat[1]
                                                elif symbol in comsym:
                                                    volume = dat[2]
                                            new_sl=prices[0]
                                            AdjustSL(pos_ticket,float(new_sl),self.dwx)
                                            closePartials(pos_ticket,float(volume),self.dwx)
                                        elif trade == 'partial tp':
                                            c.execute('SELECT * FROM partials')
                                            data2=c.fetchall()
                                            for dat in data2:
                                                if symbol in forexsym:
                                                    volume= dat[0]
                                                elif symbol in indexsym:
                                                    volume = dat[1]
                                                elif symbol in comsym:
                                                    volume = dat[2]
                                            new_tp=prices[0]
                                            AdjustTP(pos_ticket,float(new_tp),self.dwx)
                                            closePartials(pos_ticket,float(volume),self.dwx)
                                    elif trade=='adjust sltp':
                                        AdjustSLTP(pos_ticket,prices,self.dwx)
                                    elif trade=='adjust sl':
                                        new_sl=prices[0]
                                        AdjustSL(pos_ticket,float(new_sl),self.dwx)
                                    elif trade=='adjust tp':
                                        new_tp=prices[0]
                                        AdjustTP(pos_ticket,float(new_tp),self.dwx)
                                    elif trade=='cancel':
                                        removeOrder(pos_ticket,self.dwx)
                                    elif trade=='close fully':
                                        closeFully(pos_ticket,self.dwx)

                        else:
                            chat_from = event.chat if event.chat else (await event.get_chat()) # telegram MAY not send the chat enity
                            chat_title = chat_from.title
                            chat_id=chat_from.id
                            base_text=event.raw_text
                            base_text_id=event.id
                            #totally=f'{chat_title,chat_id,base_text,base_text_id}'
                            #await client.send_message('freemium2', totally)
                            writer.writerow([base_text,base_text_id,chat_title,chat_id]) 
                            #analyzing the telegram text and getting sl,tp,...
                            #symbol,trade,SL,TP,ENTRY=parsetext(base_text)
                            if self.ui.stopCopier.isChecked():
                                self.ui.generalErrors.setText('Copying is stopped')
                                
                                self.ui.startbtn.setText('Start Copying')
                                self.ui.startbtn.setEnabled(True)
                                self.ui.channelsbtn.setEnabled(True)
                                await client.disconnect()
                            else:
                                self.ui.generalErrors.setText('')
                                symbol, trade, SL, ENTRY,*TPS = parsetext(base_text)
                                print(symbol,trade,SL,ENTRY,TPS)
                                TP=TPS[-1]
                                c.execute("SELECT * FROM exclude_symbols WHERE symbol=?", (symbol,))
                                exsymbo=c.fetchall()
                                if exsymbo:
                                    print('this is excluded')
                                    pass
                                else:
                                    c.execute("SELECT * FROM symbol_volume WHERE symbol=?", (symbol,))
                                    symboldefault=c.fetchall()
                                    if symboldefault:
                                        for symbo in symboldefault:
                                            volume = symbo[1]
                                            slippage = symbo[2]
                                    else:
                                        print('inside else')
                                        c.execute('SELECT * FROM defaults')
                                        data3=c.fetchall()
                                        for datt in data3:
                                            if symbol in forexsym:
                                                volume= datt[0]
                                                slippage= datt[1]
                                            elif symbol in indexsym:
                                                volume = datt[2]
                                                slippage = datt[3]
                                            elif symbol in comsym:
                                                volume = datt[4]
                                                slippage = datt[5]
                                            else:
                                                volume = 0.01
                                                slippage = 8
                                    
                                    if type(volume) != float:
                                        volume = float(volume)
                                    c.execute('SELECT * FROM users')
                                    data=c.fetchall()
                                    for mt in data:
                                        serverAddress=mt[0]
                                        accountID=mt[1]
                                        suffix = mt[2]
                                        magic = int(time.time())
                                        if len(suffix) >0:
                                            symbol = symbol+suffix
                                        else:
                                            symbol = symbol
                                        if trade=='SELL MARKET' or trade=='BUY MARKET':
                                            
                                            if self.ui.ali.isChecked():
                                            
                                                for i, a in enumerate(TPS):
                                                    print('a',type(a),a, 'b',type(i),i)
                                                    if a == TPS[0]:
                                                        MarketExecution(symbol,volume,trade,float(SL),float(TPS[i]),magic,self.dwx)
                                                        time.sleep(1)
                                                        executed_trades.loc[len(executed_trades)]=[accountID,base_text_id,magic,SL,TPS[i]]
                                                        tpholder.loc[len(tpholder)]=[magic,TPS]
                                                        print(tpholder)
                                                        print(executed_trades,symbol,SL,TP)
                                                    elif a == TPS[1]:
                                                        
                                                        if trade == 'BUY MARKET':
                                                            trade = 'BUY STOP'
                                                        else:
                                                            trade = 'SELL STOP'
                                                        tradeExecution(symbol,volume,trade,float(ENTRY),float(TPS[i]),float(TPS[i-1]),magic+i,self.dwx)
                                        
                                                        executed_trades.loc[len(executed_trades)]=[accountID,base_text_id,magic,SL,TP]
                                                        tpholder.loc[len(tpholder)]=[magic,TPS]
                                                        print(executed_trades,symbol,SL,TP)
                                                        time.sleep(1)
                                                        
                                                    else:
                                                        if trade == 'BUY MARKET' or trade == 'BUY STOP':
                                                            trade = 'BUY STOP'
                                                        else:
                                                            trade = 'SELL STOP'
                                                        
                                                        tradeExecution(symbol,volume,trade,float(TPS[i-2]),float(TPS[i]),float(TPS[i-1]),magic+i,self.dwx)
                                        
                                                        executed_trades.loc[len(executed_trades)]=[accountID,base_text_id,magic,SL,TP]
                                                        tpholder.loc[len(tpholder)]=[magic,TPS]
                                                        print(executed_trades,symbol,SL,TP)
                                                        time.sleep(1)
                                            else:
                                                MarketExecution(symbol,volume,trade,float(SL),float(TP),magic,self.dwx)
                                                time.sleep(1)
                                                executed_trades.loc[len(executed_trades)]=[accountID,base_text_id,magic,SL,TP]
                                                tpholder.loc[len(tpholder)]=[magic,TPS]
                                                print(tpholder)
                                                print(executed_trades,symbol,SL,TP)
                                            
                                        else:
                                            
                                            if self.ui.ali.isChecked():
                                                for i, a in enumerate(TPS):
                                                   
                                                    if a == TPS[0]:
                        
                                                        tradeExecution(symbol,volume,trade,float(SL),float(TPS[i]),ENTRY,magic,self.dwx)
                                                        time.sleep(1)
                                                       
                                                    elif a == TPS[1]:
                                                       
                                                        tradeExecution(symbol,volume,trade,float(ENTRY),float(TPS[i]),float(TPS[i-1]),magic+i,self.dwx)
                                        
                                                        executed_trades.loc[len(executed_trades)]=[accountID,base_text_id,magic,SL,TP]
                                                        tpholder.loc[len(tpholder)]=[magic,TPS]
                                                        print(executed_trades,symbol,SL,TP)
                                                        time.sleep(1)
                                                        
                                                    else:
                                                        
                                                        tradeExecution(symbol,volume,trade,float(TPS[i-2]),float(TPS[i]),float(TPS[i-1]),magic+i,self.dwx)
                                        
                                                        executed_trades.loc[len(executed_trades)]=[accountID,base_text_id,magic,SL,TP]
                                                        tpholder.loc[len(tpholder)]=[magic,TPS]
                                                        print(executed_trades,symbol,SL,TP)
                                                        time.sleep(1)
                                            else:
                                                tradeExecution(symbol,volume,trade,float(SL),float(TP),ENTRY,magic,self.dwx)
                                            
                                                executed_trades.loc[len(executed_trades)]=[accountID,base_text_id,magic,SL,TP]
                                                tpholder.loc[len(tpholder)]=[magic,TPS]
                                                print(executed_trades,symbol,SL,TP)
                                                time.sleep(1)
                    except BaseException as e:
                        print('error is in the event.',e)                    
                    
                
            try:
                await client.run_until_disconnected()
            finally:
                 client.disconnect()
            QApplication.sendPostedEvents()


class welcomescreen(QDialog):
    def __init__(self,client):
        super(welcomescreen, self).__init__()
        self.client=client
        loadUi('gui/welcomescreen.ui',self)
        
        #to add a func to the login button
        if client.is_user_authorized():
            if client.get_me():
                self.login.clicked.connect(self.home_page)

        else:
            self.login.clicked.connect(self.gotologin)
    def home_page(self):
        home=home_page(client)
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)
    def gotologin(self):
        login=LoginScreen(self.client)
        widget.addWidget(login)
        #make the index of the screen, we change the screen by giving its index
        widget.setCurrentIndex(widget.currentIndex()+1)

class LoginScreen(QDialog):
    def __init__(self,client):
        super(LoginScreen, self).__init__()
        loadUi('gui/loginpage.ui',self)
     
        self.login.clicked.connect( self.loginfunction)
        
    #with this func we get the typed text inside the linedit
    def loginfunction(self):
        
        phone_number= self.phonefield.text()
        if len(phone_number) ==0:
            self.error.setText('Please enter your Phone!')
        elif len(phone_number)>0:
            phone=phonenumbers.parse(phone_number)
            if phonenumbers.is_valid_number(phone):
                    print('phone is valid')
                    #self.phonefield.clear()
                    if not client.is_user_authorized():
                        client.send_code_request(phone_number)
                        codelogin= tele_code(phone_number,client)
                        widget.addWidget(codelogin)
                        #make the index of the screen, we change the screen by giving its index
                        widget.setCurrentIndex(widget.currentIndex()+1)
                        #client.sign_in(phone_number, telegramCode)
                    
            else:
                self.error.setText('Please put a valid Phone Number! code, +93, +91')
    

class tele_code(QDialog):
    def __init__(self,phone_number,client):
        super(tele_code, self).__init__()
        self.phone_number=phone_number
        loadUi('gui/codepage.ui',self)
        #to add a func to the login button
        self.login.clicked.connect(self.logintelegram)
    
    def logintelegram(self):
        try:
            self.logged_in=client.sign_in(self.phone_number, self.phonefield.text())
            if self.logged_in:
                if client.get_me():
                    messageha = client.get_messages('hello6398',2)
                    myusername = client.get_me().username
                    if myusername in messageha[0].message:
                        home=home_page(client)
                        widget.addWidget(home)
                        widget.setCurrentIndex(widget.currentIndex()+1)
                    else:
                        self.error.setText('Please Contact the Seller!')
        except:
            self.error.setText('Please put the correct Code!')
        #print('user',self.logged_in)

class home_page(QMainWindow):

    def __init__(self,client):
        super(home_page,self).__init__()
        self.ui = loadUi('gui/mainpage.ui',self)
        self.client=client
        self.widget=self.stackedWidget
        self.widget.setCurrentWidget(self.home)
        username=self.client.get_me()
        username=utils.get_display_name(username)
        self.usernamebtn.setText(f'Telegram Username: {username}')
        self.channelsbtn.clicked.connect(self.channels_page)
        self.mt5btn.clicked.connect(self.mt5_page)
        self.defaultsbtn.clicked.connect(self.defaults_page)
        self.homebtn.clicked.connect(self.home_page)
        self.magicbtn.clicked.connect(self.magic_page)
        self.trailingbtn.clicked.connect(self.trailer_page)
        self.logoutbtn.clicked.connect(self.logout_telegram)
    ######################### Analytics page ###################################
    def logout_telegram(self):
        #try:
        self.client.connect()
        self.client.log_out()
        sys.exit(app.exec()) 
        #except:
            #self.generalErrors.setText('Please stop the Copy event first and then log out!!!')
    def trailer_page(self):
        self.widget.setCurrentWidget(self.stop_loss)
        self.trailing_save.clicked.connect(self.save_trailers)
        self.start_trailing.clicked.connect(self.start_trailing_func)
        self.start_trailing_tp.clicked.connect(self.start_tp_func)
    
    def start_trailing_func(self):
        try:
            if self.stop_sl.isChecked():
                self.start_trailing.setText('Start Trailing SL')
                
                
            else:
                c.execute('SELECT * FROM trailer')
                data=c.fetchall()
                print(len(data))
                print(data)
                if len(data) ==0:
                    self.generalErrors.setText('Please fill the trailing defaults and then try!')
                else:
                    self.generalErrors.setText('')
                    self.trailer_start  = trail_sl(self.ui,self.dwx)
                    self.objThread3 = QThread(parent=self)
                    self.trailer_start.moveToThread(self.objThread3)
                    self.objThread3.started.connect(self.trailer_start.trail_starter)
                    self.objThread3.start()
                    self.start_trailing.setText('Trailing SL Started')
        except:
            self.generalErrors.setText('Go to MT4 Page and login to an Account first!')
    def start_tp_func(self):
        try:
            if self.stop_tp.isChecked():
                self.start_trailing_tp.setText('Start Trailing by TP')
                
            else:
                
                if len(tpholder) ==0:
                    self.generalErrors.setText('You havent executed a multi TP trade yet!')
                else:
                    self.generalErrors.setText('')
                    self.trailer_start  = trail_sl(self.ui,self.dwx)
                    self.objThread3 = QThread(parent=self)
                    self.trailer_start.moveToThread(self.objThread3)
                    self.objThread3.started.connect(self.trailer_start.Tp_starter)
                    self.objThread3.start()
                    self.start_trailing_tp.setText('Trailing by TP Started')
                    #start_tp_trailing()
        except:
            self.generalErrors.setText('Go to MT4 Page and login to an Account first!')
        
    def save_trailers(self):
        fx_default = self.fx_default.text()
        fx_trailer =  self.fx_trailer.text()
        fx_distance = self.fx_distance.text()
        fx_cus =0
        ind_default = self.ind_default.text()
        ind_trailer =  self.ind_trailer.text()
        ind_distance = self.ind_distance.text()
        ind_cus=0
        com_default = self.com_default.text()
        com_trailer =  self.com_trailer.text()
        com_distance = self.com_distance.text()
        com_cus=0
        c.execute('SELECT * FROM trailer')
        data=c.fetchall()
        print(len(data))
        print(data)
        if len(data)==0:
            c.execute("""INSERT INTO trailer VALUES(:fxd,:fxt,:fxdist,:fxc,
                    :indd,:indt,:inddist,:indc,:comd,:comt,:comdist,:comc)""",
                    {'fxd':fx_default,'fxt':fx_trailer,'fxdist':fx_distance,'fxc':fx_cus,
                    'indd':ind_default,'indt':ind_trailer,'inddist':ind_distance,'indc':ind_cus,
                    'comd':com_default,'comt':com_trailer,'comdist':com_distance,'comc':com_cus})
            conn.commit()
        elif len(data) >0:
            c.execute('''
                    UPDATE trailer SET fxdef=:fxd,fxtrail=:fxt,fxdistance=:fxdist,fxcus=:fxc,
                    inddef=:indd,indtrail=:indt,inddistance=:inddist,indcus=:indc,
                    comdef=:comd,comtrail=:comt,comdistance=:comdist,comcus=:comc
                    ''',
                    {'fxd':fx_default,'fxt':fx_trailer,'fxdist':fx_distance,'fxc':fx_cus,
                    'indd':ind_default,'indt':ind_trailer,'inddist':ind_distance,'indc':ind_cus,
                    'comd':com_default,'comt':com_trailer,'comdist':com_distance,'comc':com_cus
                    })
            conn.commit()
            
        self.fx_default.clear()
        self.fx_trailer.clear()
        self.fx_distance.clear()
        
        self.ind_default.clear()
        self.ind_trailer.clear()
        self.ind_distance.clear()
        
        self.com_default.clear()
        self.com_trailer.clear()
        self.com_distance.clear()
          
    #######################################################

    def magic_page(self):
        self.generalErrors.setText('')
        try:
            if self.dwx:
                #print(dwx.open_orders.items())
                self.widget.setCurrentWidget(self.magickeys)
                self.showtrades.clicked.connect(self.show_trades)
                self.refreshtrades.clicked.connect(self.refresh_trades)
                self.editTPsl.clicked.connect(self.edit_tp_sl)
                self.saveTPsl.clicked.connect(self.save_tp_sl)
                self.closeAll.clicked.connect(self.close_current_pos)
                self.closeHalf.clicked.connect(self.close_half)
                self.close_customlot.clicked.connect(self.close_custom)
                self.closeLot.clicked.connect(self.close_lot)
                self.close_fifty.clicked.connect(self.close_point_fifty)
                self.close_ten.clicked.connect(self.close_point_ten)
                self.close_five.clicked.connect(self.close_point_five)
                self.close_one.clicked.connect(self.close_point_one)
                self.breakeven.clicked.connect(self.breakeven_def)
            else:
                self.generalErrors.setText('Go to MT4 Page and login to an Account first then try Magic Keys!')
        except:
            self.generalErrors.setText('Go to MT4 Page and login to an Account first then try Magic Keys!')
        
        
    def breakeven_def(self):
        self.magic_errors.clear()
        items = self.tradeslist.selectedItems()
        if items:
            for i in range(len(items)):
                self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                self.edit_ID=int(self.edit_ID[2].split(' ')[1])
                result=breakeven_pos(self.edit_ID,self.dwx)
                #time.sleep(1)
                self.show_trades()
            
    def close_point_one(self):
        self.magic_errors.clear()
        try:
            items = self.tradeslist.selectedItems()
            if items:
                for i in range(len(items)):
                    self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                    self.edit_ID=int(self.edit_ID[2].split(' ')[1])
                    close_point_one_lot(self.edit_ID,self.dwx)
                    #time.sleep(1)
                    self.show_trades()
                   
        except BaseException:
            self.magic_errors.setText('| Please select positionID row!')
            self.show_trades()
    def close_point_five(self):
        self.magic_errors.clear()
        #try:
        items = self.tradeslist.selectedItems()
        if items:
            for i in range(len(items)):
                self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                self.edit_ID=int(self.edit_ID[2].split(' ')[1])
                close_point_five_lot(self.edit_ID,self.dwx)
                #time.sleep(1)
                self.show_trades()
       # except BaseException:
          #  self.magic_errors.setText('| Please select positionID row!') 
          #  self.show_trades()  
    def close_point_ten(self):
        self.magic_errors.clear()
        try:
            items = self.tradeslist.selectedItems()
            if items:
                for i in range(len(items)):
                    self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                    self.edit_ID=int(self.edit_ID[2].split(' ')[1])
                    close_point_ten_lot(self.edit_ID,self.dwx)
                    #.sleep(1)
                    self.show_trades()
        except BaseException:
            self.magic_errors.setText('| Please select positionID row!')
            #time.sleep(1)
            self.show_trades()
    def close_point_fifty(self):
        self.magic_errors.clear()
        try:
            items = self.tradeslist.selectedItems()
            if items:
                for i in range(len(items)):
                    self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                    self.edit_ID=int(self.edit_ID[2].split(' ')[1])
                    close_point_fifty_lot(self.edit_ID,self.dwx)
                    #time.sleep(1)
                    self.show_trades()
        except BaseException:
            self.magic_errors.setText('| Please select positionID row!')
            #time.sleep(1)
            self.show_trades()
    def close_lot(self):
        self.magic_errors.clear()
        try:
            items = self.tradeslist.selectedItems()
            if items:
                for i in range(len(items)):
                    self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                    self.edit_ID=int(self.edit_ID[2].split(' ')[1])
                    close_one_lot(self.edit_ID,self.dwx)
                    #time.sleep(1)
                    self.show_trades()
        except BaseException:
            self.magic_errors.setText('| Please select positionID row!')
            #time.sleep(1)
            self.show_trades()
    def close_custom(self):
        self.magic_errors.clear()
        items = self.tradeslist.selectedItems()
        #try:
        if items:
            for i in range(len(items)):
                self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                self.edit_ID=int(self.edit_ID[2].split(' ')[1])
                #positions=mt5.positions_get(ticket=int(self.edit_ID))[0]
                #self.custompcEntry.setText(str(positions.volume))
                percent=self.customEntry.text()
                if percent:
                    close_custom(self.edit_ID,percent,self.dwx)
                    #time.sleep(1.1)
                    self.show_trades()
        #except BaseException:
            #self.magic_errors.setText('| Please select positionID row!')
            #self.show_trades()
    def close_half(self):
        self.magic_errors.clear()
        #try:
        items = self.tradeslist.selectedItems()
        if items:
            for i in range(len(items)):
                self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                self.edit_ID=int(self.edit_ID[2].split(' ')[1])
                closeHalf(self.edit_ID,self.dwx)
                #time.sleep(1)
                self.show_trades()
        #except BaseException:
          #  self.magic_errors.setText('| Please select positionID row!')
           # self.show_trades()
    def close_current_pos(self):
        self.magic_errors.clear()
        try:
            items = self.tradeslist.selectedItems()
            if items:
                for i in range(len(items)):
                    self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                    self.edit_ID=int(self.edit_ID[2].split(' ')[1])
                    closeFully(self.edit_ID,self.dwx)
                    #time.sleep(1)
                    self.show_trades()
        except BaseException:
            self.magic_errors.setText('| Please select positionID row!')
            #time.sleep(1)
            self.show_trades()
    def save_tp_sl(self):
        try:
            tp=self.tpentry.text()
            sl=self.slentry.text()
            ticket=self.edit_ID
            print('i am 1')
            MagicAdjustSLTP(ticket,sl,tp,self.dwx)
            print('i am 2')
        except BaseException:
            self.magic_errors.setText('| Check if Fields are empty or Refresh trades!')
    def edit_tp_sl(self):
        try:
            items = self.tradeslist.selectedItems()
            if items:
                for i in range(len(items)):
                    self.edit_ID=self.tradeslist.selectedItems()[i].text().split(':')
                    self.edit_ID=self.edit_ID[2].split(' ')[1]
                    print(self.edit_ID)
                    position = self.dwx.open_orders[str(self.edit_ID)]
                    order_path = join(self.logged_address,'DWX', 'DWX_Orders.txt')
                    with open(order_path) as f:
                        data=json.load(f)
                    position = data['orders'][str(self.edit_ID)]
                    self.tpentry.setText(str(position['TP']))
                    self.slentry.setText(str(position['SL']))
                    self.volentry.setText(str(position['lots']))
                    self.volentry.setEnabled(False)
                    self.profitentry.setText(str(position['pnl']))
                    self.profitentry.setEnabled(False)
                    self.curentry.setText(str(position['open_price']))
                    self.curentry.setEnabled(False)
        except BaseException:
            self.magic_errors.setText('| Please select the PositionID row!')
    def refresh_trades(self):
        self.magic_errors.clear()
        self.show_trades()
           
    def show_trades(self):
        
        #self.tradeslist.sortingEnabled(enabled)
        #self.pos=[]
        try:
            symbols = []
            tposition = self.dwx.open_orders.items()
            for ticket, position in tposition:
                symbols.append(position['symbol'])

            self.dwx.subscribe_symbols(symbols)
            time.sleep(0.8)
            self.tradeslist.clear()
            
            if not tposition:
                self.magic_errors.setText('| Currently there is no positions ')
            else:
                #try:
                    for ticket, position in tposition:
                        ticket=ticket
                        symbol = position['symbol']
                        profit=position['pnl']
                        sl=position['SL']
                        tp=position['TP']
                        volume = position['lots']
                        pos_type= position['type']
                        print(symbol)
                        if position['type'] == 'buy':
                           
                            curr_price= self.dwx.market_data[symbol]['bid']    
                        else:
                           
                            curr_price= self.dwx.market_data[symbol]['ask']
                        #cur_price=position.price_current
                        open_price=position['open_price']
                        symbol=position['symbol']
                        self.tradeslist.addItem(f'Symbol: {symbol}                                                                 PositionID: {ticket}   ')
                        self.tradeslist.addItem(f'Profit/Loss: {profit}                SL: {sl}           TP: {tp}                     Type: {pos_type}')
                        self.tradeslist.addItem(f'Volume:{volume}                            Current_Price: {curr_price}            Opened_Price: {open_price}')
                        self.tradeslist.addItem(f'-----------------------------------------------')
                        #self.pos.append(ticket)
                    self.showtrades.setEnabled(False)
        except:
            pass
    ########################### HOME_PAGE ##########################
    def home_page(self):
        self.widget.setCurrentWidget(self.home)
        self.startbtn.clicked.connect(self.start_copy)

    def start_copy(self):
        try:
            self.start_copier  = start_copying(client,self.ui,self.dwx)
            self.Thread_object = QThread(parent=self)
            self.start_copier.moveToThread(self.Thread_object)
            #self.Thread_object.stop_signal.connect(self.stopper)
            self.Thread_object.started.connect(self.start_copier.start_event)
            self.Thread_object.start()
            self.startbtn.setText('Copy Started')
            self.startbtn.setEnabled(False)
            self.channelsbtn.setEnabled(False)
        except:
            self.generalErrors.setText('Go to MT4 Page and login to an Account first!')
    '''
    def stopper(self):
        self.stopbtn.clicked.connect(self.stop_copy)
    def stop_copy(self):
        self.Thread_object.finished.connect(self.Thread_object.terminate)
    '''
    ########################### DEFAULTS_PAGE #######################
    def defaults_page(self):
        self.widget.setCurrentWidget(self.defaults)
        self.defaultsavebtn.clicked.connect(self.save_defaults)
        self.symbolsavebtn.clicked.connect(self.save_symbol_vol)
        self.exsavebtn.clicked.connect(self.exclude_symbols)
        self.insavebtn.clicked.connect(self.include_symbols)
        self.savep.clicked.connect(self.save_partials)
    def save_partials(self):
        forexp=self.forexp.text()
        indexp=self.indp.text()
        comp=self.comp.text()
        c.execute("SELECT * FROM partials")
        data=c.fetchall()
        
        c.execute(f'''
            UPDATE partials SET forexp=?,indexp=?,comp=?
            ''',
            (forexp,indexp,comp))
           
        conn.commit()
        self.forexp.clear()
        self.indp.clear()
        self.comp.clear()
    def exclude_symbols(self):
        symbol=self.exentry.text()
        #c.execute("DELETE FROM symbols WHERE symbol ={}".format(symbol))
        c.execute("INSERT INTO exclude_symbols VALUES(:symbo)",
                {'symbo':symbol})
        conn.commit()
        self.exentry.clear()
    def include_symbols(self):
        symbol=self.inentry.text()
        #c.execute("SELECT * FROM exclude_symbols")
        #data=c.fetchall()
        #print(data)
        c.execute("DELETE FROM exclude_symbols WHERE symbol =?",(symbol,))
        conn.commit()
        self.inentry.clear()
    def save_symbol_vol(self):
        symbol = self.symbolentry.text()
        volume = self.symbolvolume.text()
        slips = self.symbolslippage.text()
        c.execute("SELECT * FROM symbol_volume WHERE symbol=?", (symbol,))
        data=c.fetchall()
        if len(data)==0:
            c.execute("INSERT INTO symbol_volume VALUES(:symbo,:vol,:slip)",
                {'symbo':symbol ,'vol': volume,'slip':slips })
            conn.commit()
        else:
            c.execute(f'''
                  UPDATE symbol_volume SET symbol=?,volume=?,slippage=? WHERE symbol = ?
                  ''',
                  (symbol,volume,slips,symbol))
           
            conn.commit()
        c.execute("SELECT * FROM symbol_volume")
        data=c.fetchall()
        self.symbolentry.clear()
        self.symbolvolume.clear()
        self.symbolslippage.clear()
    def save_defaults(self):
        fxvolume=self.fxvolume.text()
        fxslippage=self.fxslippage.text()

        indexvolume=self.indexvolume.text()
        indexslippage=self.indexslippage.text()

        comvolume=self.comvolume.text()
        comslippage=self.comslippage.text()
        c.execute('''
                  UPDATE defaults SET fxvolume=:fxvol,fxslippage=:fxslip,indexvolume=:indexvol,
                  indexslippage=:indexslip,comvolume=:comvol,comslippage=:comslip
                  ''',
                  {'fxvol':fxvolume,'fxslip':fxslippage,'indexvol':indexvolume,'indexslip':indexslippage,
                  'comvol':comvolume,'comslip':comslippage})
        conn.commit()
        c.execute('SELECT * FROM defaults')
        data=c.fetchall()
        self.fxvolume.clear()
        self.fxslippage.clear()

        self.indexvolume.clear()
        self.indexslippage.clear()

        self.comvolume.clear()
        self.comslippage.clear()
    ########################### MT5_PAGE   ######################    
    def mt5_page(self):
        self.widget.setCurrentWidget(self.mt)
        self.mtaddbtn.clicked.connect(self.line_data)
        self.mtshow.clicked.connect(self.show_accounts)
        self.mtlogin.clicked.connect(self.login_accounts)
        self.mtdelete.clicked.connect(self.delete_accounts)
    def login_accounts(self):
        items = self.mtlist.selectedItems()
        self.mt_errors.setText('')
        try:
            for i in range(len(items)):
                self.ID=self.mtlist.selectedItems()[i].text().split(':')
                c.execute('SELECT * FROM users WHERE LoginID ={}'.format(self.ID[1]))
                
                data=c.fetchall()
                
                for mt in data:
                    
                    self.logged_address = mt[0]
                    self.dwx = dwx_client(None, self.logged_address, sleep_delay=0.005,
                                    max_retry_command_seconds=10, verbose=False)
                    time.sleep(0.05)
                    self.dwx.start()
                    #print(dwx.open_orders.items())
                    self.mt_errors.setText(f'Now You are Logged in Account ID: {mt[1]}')
                    
        except:
            self.mt_errors.setText('please select the ID row!')
        QApplication.sendPostedEvents()

    def delete_accounts(self):
        items = self.mtlist.selectedItems()
        try:
            for i in range(len(items)):
                self.ID=self.mtlist.selectedItems()[i].text().split(':')
                self.ID = self.ID[1]
                
                c.execute("DELETE FROM users WHERE LoginID ={}".format(self.ID))
                conn.commit()  
                self.show_accounts()
                #self.error.setText('please select the ID row!')
        except:
            self.mt_errors.setText('please select the ID row to delete!')
    def show_accounts(self):
        self.mtlist.clear()
        c.execute("SELECT * FROM users")
        data=c.fetchall()
        for mt in data:
            #self.mtlist.addItem(str(mt))
            self.mtlist.addItem(str(f'Address : {mt[0]}'))
            self.mtlist.addItem(str(f'ID : {mt[1]}'))
            self.mtlist.addItem(str(f'Suffix : {mt[2]}'))
            #self.mtlist.addItem(str(f'Symbols : {mt[4]}'))
            self.mtlist.addItem(str('............................. '))
    def line_data(self):
        
        mtserver=self.mtserver.text()
        if not mtserver:
            self.serverError.setText('* Required')
        mtid=self.mtid.text()
        if not mtid:
            self.idError.setText('* Required')
        #mtpass=self.mtpassword.text()
        #if not mtpass:
            #self.passError.setText('* Required')
        mtsuffix=self.mtsuffix.text()
        #mtsymbol=self.mtsymbols.text()
        try:
            int(mtid)
            self.idError.setText('')
            if mtserver  and mtid:
                c.execute("INSERT INTO users VALUES(:server,:login,:suffix)",{'server':mtserver,'login':mtid,'suffix':mtsuffix})
                conn.commit()
            self.mtserver.clear()
            self.mtid.clear()
            #self.mtpassword.clear()
            self.mtsuffix.clear()
            #self.mtsymbols.clear()
        except ValueError:
            self.idError.setText('Wrong ID')

    ################################ CHANNELS_PAGE  ####################################
    def channels_page(self):
        self.widget.setCurrentWidget(self.channels)
        self.list1.clear()
        self.client.connect()
        #channels=client.get_dialogs()
        for dialog in client.iter_dialogs():
            if not dialog.is_user :
            #if not dialog.is_group and dialog.is_channel:
                self.list1.addItem(dialog.name)
            #print(channel.name)
        try:
            with open('gui/alljang.csv', "r") as f:
                reader = csv.reader(f, delimiter=",",lineterminator="\n")
                self.list2.clear()
                for row in reader:    
                    for i in row:
                        self.list2.addItem(str(i))
        except:
            pass 
        self.addbtn.clicked.connect(self.add_item)
        #self.list1.itemClicked.connect(self.do_print)
        self.removebtn.clicked.connect(self.remove_item)
        self.savebtn.clicked.connect(self.save_item)
    def add_item(self):
        self.error.setText('')  
        items = self.list1.selectedItems()
        for i in range(len(items)):
            itemsTextList =  [str(self.list2.item(i).text()) for i in range(self.list2.count())]
            if self.list1.selectedItems()[i].text() in itemsTextList:
                self.error.setText('--> Duplicates not allowed!')
                continue
            else:
                
                self.list2.addItem(str(self.list1.selectedItems()[i].text()))
               
    def remove_item(self):
        self.list2.takeItem(self.list2.currentRow())
    def save_item(self):
        itemsTextList =  [str(self.list2.item(i).text()) for i in range(self.list2.count())]        
        
        with open("gui/alljang.csv","w",encoding='UTF-8') as f:
            writer = csv.writer(f,delimiter=",",lineterminator="\n")
            writer.writerow(itemsTextList) 
        
        
    #######################################################################
    


app=QApplication(sys.argv)
#app.setWindowTitle('Telegram TO MT5 Copier')
welcome=welcomescreen(client)

widget = QtWidgets.QStackedWidget()
widget.setWindowTitle('Telegram To MT5 Copier')
widget.setMinimumHeight(620)
widget.setMinimumWidth(1000)
widget.addWidget(welcome)
widget.show()

try:
    sys.exit(app.exec())
except:
    print('there is a problem')

