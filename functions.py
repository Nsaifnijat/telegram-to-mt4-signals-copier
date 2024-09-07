
import re
import pandas as pd

import sqlite3
import numpy as np
from os.path import join
import json
#mt.initialize()
from dwx_client import dwx_client
import time
def parsetext(TeleMSG):
    #prices=re.findall(r'[\d]+[.][\d]+', str(context.split('\n')))
    #price_patterns=re.compile(r'\d\d\d+.\d+|\d\d+.\d\d\d|\d.\d\d\d+|\d.\d\d+|\d\d.\d+|\d\d\d\d+')
    try: 
        TelMSG=TeleMSG.upper()
        stop_loss=re.compile("(SL|STOPLOSS|STOP\\s*LOSS|STOP|SUGERIDO|STOPPP LOSS AUF|STOP LOSS :round_pushpin::)\\s*(-|:|\\..)?\\s*(@|AT|#|_)?\\s*([0-9,.]+)")
        sl_match=stop_loss.findall(TelMSG)
        
        if ',' in sl_match[-1][-1]:
            stop_loss = sl_match[-1][-1].replace(',','.')
        else:
            stop_loss = sl_match[-1][-1]
        try:   
            entry=re.compile("\\s*(BUY|SELL|NOW|RECOMENDED|OPEN|ENTRY|💎|Einstieg: Jetzt! \\()\\s*([A-Z,#]*)?\\s*(LIMIT|STOP)?\\s*([A-Z,#]*)?\\s*(PRICE|AGAIN|ENTRY|NOW|\\()?\\s*([A-Z,#]*)?\\s*(@|AT\\s*CMP|:|_)?\\s*([A-Z,#]*)?\\s*([0-9,.]+)")
            entry_match=entry.findall(TelMSG)
            if ',' in entry_match[-1][-1]:
                entry=entry_match[-1][-1].replace(',','.')
            else:
                entry=entry_match[-1][-1]
        except:
            entry=0
        if 'SELL STOP' in TelMSG or 'SELLSTOP' in TelMSG:
            trade='SELL STOP'
        elif 'SELL LIMIT' in TelMSG or 'SELLLIMIT' in TelMSG:
            trade='SELL LIMIT'
        elif 'SELL' in TelMSG or 'SHORT' in TelMSG:
                trade='SELL MARKET'
        elif 'BUY STOP' in TelMSG or 'BUYSTOP' in TelMSG:
            trade='BUY STOP'
        elif 'BUY LIMIT' in TelMSG or 'BUYLIMIT' in TelMSG:
            trade='BUY LIMIT'
        elif 'BUY' in TelMSG or 'LONG' in TelMSG:
            trade='BUY MARKET'

        pairs=['EURUSD','USOIL','UKOIL','XAGUSD','XNGUSD','BRENT','GBPUSD','EURGBP','USDCAD','NZDUSD','AUDUSD','AUDCAD','AUDCHF','AUDGBP','AUDNZD','NZDCAD',
                    'CADCHF','EURCAD','EURCHF','EURAUD','GBPAUD','GBPNZD','GBPCAD','USDCHF','GBPCHF','NZDCHF',
                    'EURNZD','US30','DJ30','DOW','DOW JONES 30','SPX','S&P500','AUS200','SPY','US500','STOXX50E','SPX500','DE30','FR40','HK50','STOXX50','USTEC',
                    'AUDJPY','GBPJPY','CADJPY','CHFJPY','EURJPY','NZDJPY','USDJPY','XAUUSD','EURMXN','EURNOK','EURSEK','EURTRY',
                    'GBPMXN','GBPNOK','GBPSEK','GBPTRY','USDHKD','USDMXN','USDNOK','USDSEK','USDSGD','USDTRY']
        if 'GOLD' in TelMSG:
            symbol='XAUUSD'
        elif '/' in TelMSG:
            TelMSG=TelMSG.replace('/','')
            pattern=re.compile('|'.join(pairs),re.IGNORECASE).search(TelMSG)
            symbol=pattern.group()
            #symbol=symbol.upper()
        else:
            pattern=re.compile('|'.join(pairs),re.IGNORECASE).search(TelMSG)
            symbol=pattern.group()
            #symbol=symbol.upper()
    
        price_patterns=re.compile("(TP\\s*[1-4]*|TARGET\\s*[1-4]*|TAKE\\s*PROFIT\\s*[1-4]*|TP\\s*bitte\\s*auf)\\s*(-|:|=|\\..)?\\s*(@|AT|#)?\\s*([0-9,.]+)")
        match = price_patterns.findall(TelMSG)
        
        if len(match)==1:
            TP1=match[0][-1]
            if ',' in TP1:
                TP1 = TP1.replace(',','.')
            else:
                TP1 = TP1
            return (symbol,trade,stop_loss,entry,TP1)
        elif len(match) ==2:
            TP1=match[0][-1]
            TP2=match[1][-1]
            if ',' in TP1:
                TP1 = TP1.replace(',','.')
                TP2 = TP2.replace(',','.')
            else:
                TP1 = TP1
                TP2 = TP2
            return (symbol,trade,stop_loss,entry,TP1,TP2)
        elif len(match) == 3:
            TP1=match[0][-1]
            TP2=match[1][-1]
            TP3=match[2][-1]
            if ',' in TP1:
                TP1 = TP1.replace(',','.')
                TP2 = TP2.replace(',','.')
                TP3 = TP3.replace(',','.')
            else:
                TP1 = TP1
                TP2 = TP2
                TP3 = TP3
            return (symbol,trade,stop_loss,entry,TP1,TP2,TP3)
        elif len(match) == 4:
            TP1=match[0][-1]
            TP2=match[1][-1]
            TP3=match[2][-1]
            TP4=match[3][-1]
            if ',' in TP1:
                TP1 = TP1.replace(',','.')
                TP2 = TP2.replace(',','.')
                TP3 = TP3.replace(',','.')
                TP4 = TP4.replace(',','.')
            else:
                TP1 = TP1
                TP2 = TP2
                TP3 = TP3
                TP4 = TP4
            return (symbol,trade,stop_loss,entry,TP1,TP2,TP3,TP4)
        else:
            print('len 5')
            TP1=match[0][-1]
            TP2=match[1][-1]
            TP3=match[2][-1] 
            TP4=match[3][-1]
            TP5=match[4][-1]  
            if ',' in TP1:
                TP1 = TP1.replace(',','.')
                TP2 = TP2.replace(',','.')
                TP3 = TP3.replace(',','.')
                TP4 = TP4.replace(',','.')
                TP5 = TP5.replace(',','.')
            else:
                TP1 = TP1
                TP2 = TP2
                TP3 = TP3
                TP4 = TP4
                TP5 = TP5
            return (symbol,trade,stop_loss,entry,TP1,TP2,TP3,TP4,TP5)
    except BaseException:
        return 0        
    

def tradeExecution(symbol,volume,trade,SL,TP,ENTRY,magic,address):
    dwx = address
   
    if trade=='BUY STOP':
        
        dwx.open_order(symbol=symbol, order_type='buystop',
                                lots=volume, price=ENTRY, stop_loss=SL, take_profit=TP,
                                magic=magic, comment='', expiration=0)
        

    elif trade=='BUY LIMIT':
        
        order = dwx.open_order(symbol=symbol, order_type='buylimit',
                                lots=volume, price=ENTRY, stop_loss=SL, take_profit=TP,
                                magic=magic, comment='', expiration=0)
        
    elif trade=='SELL STOP':
        
        order = dwx.open_order(symbol=symbol, order_type='sellstop',
                                lots=volume, price=ENTRY, stop_loss=SL, take_profit=TP,
                               magic=magic, comment='', expiration=0)
        
    elif trade=='SELL LIMIT':
        order = dwx.open_order(symbol=symbol, order_type='selllimit',
                                lots=volume, price=ENTRY, stop_loss=SL, take_profit=TP,
                                magic=magic, comment='', expiration=0)
       

def MarketExecution(symbol,volume,trade,SL,TP,magic,address):
    dwx = address
    if trade=='SELL MARKET':
        dwx.open_order(symbol=symbol, order_type='sell',
                                lots=volume, price=0, stop_loss=SL, take_profit=TP,
                                magic=magic, comment='', expiration=0)
        
    elif trade=='BUY MARKET':
        dwx.open_order(symbol=symbol, order_type='buy',
                                lots=volume, price=0, stop_loss=SL, take_profit=TP,
                                magic=magic, comment='', expiration=0)
        


def parserepltext(repltext):
    rtext=repltext.lower()
    #prices=re.findall(r'[\d]+[.][\d]+', str(rtext.split('\n')))
    price_patterns=re.compile(r'\d\d\d+.\d+|\d\d+.\d\d\d|\d.\d\d\d+|\d\d.\d+|\d\d\d\d+')
    prices=price_patterns.findall(rtext)
    if prices:
        prices=prices
    else:
        prices=[0]
        
    closes=['close','take']
    pattern1=re.compile('|'.join(closes),re.IGNORECASE).search(rtext)
    
    updates=['adjust','move','update','change']
    pattern2=re.compile('|'.join(updates),re.IGNORECASE).search(rtext)
    
    cancels=['cancel','remove','delete']
    pattern3=re.compile('|'.join(cancels),re.IGNORECASE).search(rtext)
    
    if pattern1 and pattern2:
        print('yes both')
        partialha=['partials','partial','partail','partil']
        subpat1=re.compile('|'.join(partialha),re.IGNORECASE).search(rtext)
        
        slha=['sl','stop']
        subpat2=re.compile('|'.join(slha),re.IGNORECASE).search(rtext)
        
        tpha=['tp','tps','target']
        subpat3=re.compile('|'.join(tpha),re.IGNORECASE).search(rtext)
        
        if subpat1 and subpat2:
            trade='partial sl'
        elif subpat1 and subpat3:
            trade = 'partial tp'
       
    elif pattern1:
        if 'partial' in rtext:
            trade='close partial'
        elif 'half' in rtext:
            trade='close partial'
        else:
            trade='close fully'

    elif pattern2:
        if 'sl' in rtext and 'tp' in rtext or 'stop' in rtext and 'target' in rtext:
            trade='adjust sltp'
        elif 'sl' in rtext or 'stop' in rtext:
            trade='adjust sl'
        elif 'tp' in rtext or 'target' in rtext:
            trade='adjust tp'

    elif pattern3:
        trade='cancel'

    else:
        trade='none'
    return (trade,prices)


def removeOrder(ticket,address):
    dwx = address
    dwx.close_order(ticket,0) #zero means full position


def AdjustSLTP(ticket,prices,address):
    
    dwx = address
    order = dwx.open_orders[str(ticket)]
    if order['type']=='buy':
        new_sl=min(prices)
        new_tp=max(prices)
    else:
        new_sl=max(prices)
        new_tp=min(prices)
    dwx.modify_order(ticket,
                     lots=order['lots'],
                     price = 0,
                     stop_loss = new_sl,
                     take_profit = new_tp)
def MagicAdjustSLTP(ticket,SL,TP,address):
    print('inside func')
    dwx = address
    order = dwx.open_orders[str(ticket)]
    dwx.modify_order(ticket,
                     lots=order['lots'],
                     price = 0,
                     stop_loss = SL,
                     take_profit = TP)
    print('end of func')

def AdjustTP(ticket,TP,address):
    
    dwx = address
    order = dwx.open_orders[str(ticket)]
    dwx.modify_order(ticket,
                     lots=order['lots'],
                     price = 0,
                     stop_loss = order['SL'],
                     take_profit = TP)



def AdjustSL(ticket,SL,address):
    
    dwx = address
    order = dwx.open_orders[str(ticket)]
    dwx.modify_order(ticket,
                     lots=order['lots'],
                     price = 0,
                     stop_loss = SL,
                     take_profit = order['TP'])

def closeFully(ticket,address):
    dwx = address
    dwx.close_order(ticket,0) #zero means full position
def closeHalf(ticket,address):
    dwx = address
    order = dwx.open_orders[str(ticket)]
    vol = order['lots']/2
    dwx.close_order(ticket,vol) 

def closePartials(ticket,vol,address):
    dwx = address
    dwx.close_order(ticket,vol) 


def breakeven_pos(ticket,address):
    dwx = address
    order = dwx.open_orders[str(ticket)]
    dwx.modify_order(ticket,
                     lots=order['lots'],
                     price = 0,
                     stop_loss = order['open_price'],
                     take_profit = order['TP'])

def close_custom(ticket,vol,address):
    dwx = address
    #dwx.start()
    dwx.close_order(ticket,vol) 

def close_one_lot(ticket,address):
    dwx = address
    #dwx.start()
    dwx.close_order(ticket,1) 

def close_point_fifty_lot(ticket,address):
    dwx = address
    dwx.close_order(ticket,0.5) #zero means full position
def close_point_ten_lot(ticket,address):
    dwx = address
    dwx.close_order(ticket,0.1) 

def close_point_five_lot(ticket,address):
    dwx = address
    print('hey point five')
    dwx.close_order(str(ticket),0.05)
    print('yolo')

def close_point_one_lot(ticket,address):
    dwx = address
    dwx.close_order(ticket,0.01) 

def update(ticket,new_sl,new_tp,address):
    dwx = address
    order = dwx.open_orders[str(ticket)]
    
    dwx.modify_order(ticket,
                     lots=order['lots'],
                     price = 0,
                     stop_loss = new_sl,
                     take_profit = new_tp)

def TrailFunc(fx_default,fx_trail,fx_max_dist,ind_default,ind_trail,ind_max_dist,account, gui,dwx):#,dtframe):
    MAX_DIST_SL = fx_max_dist  # Max distance between current price and SL, otherwise SL will update
    TRAIL_AMOUNT =fx_trail  # Amount by how much SL updates
    DEFAULT_SL = fx_default  # If position has no SL, set a default SL
    INDEX_DEFAULT_SL= ind_default
    INDEX_TRAIL_AMOUNT= ind_trail
    INDEX_MAX_DIST_SL= ind_max_dist

    indices=  ['US30','DJ30','DOW','RUSSEL 2000','DOW JONES 30','NAS100','US100','NASDAQ','SPX','S&P500','AUS200','SPY','US500','STOXX50E','SPX500','DE30','FR40','HK50','STOXX50','USTEC']
    five_digit_pairs=['EURUSD','GBPUSD','EURGBP','USDCAD','NZDUSD','AUDUSD','AUDCAD','AUDCHF','AUDGBP','AUDNZD','NZDCAD',
                  'CADCHF','EURCAD','EURCHF','EURAUD','GBPAUD','GBPNZD','GBPCAD','USDCHF','GBPCHF','NZDCHF',
                  'EURNZD']
    three_digit_pairs=['XAGUSD','USOIL','UKOIL','BRENT','AUDJPY','GBPJPY','CADJPY','CHFJPY','EURJPY','NZDJPY','USDJPY']
    address =  dwx
    accountID = account[1]
    suffix = account[2]
    
    while True:
        try:
            if gui.stop_sl.isChecked():
                gui.start_trailing.setText('Start Trailing SL')
                break
            else:
                symbols = []
        
                tposition = dwx.open_orders.items()
                for ticket, position in tposition:
                    symbols.append(position['symbol'])

                dwx.subscribe_symbols(symbols)
                #dwx.start()
                symbols = []
                time.sleep(1)

                for ticket, position in tposition:
                        open_price=position['open_price']
                        ticket= ticket
                        symbol = position['symbol']
                    
                        if position['type'] == 'buy':
                            #path_market_data = join(address,'DWX', 'DWX_Market_Data.txt')
                            #with open(path_market_data) as f2:
                                #data=json.load(f2)
                                #curr_price = data[symbol]['bid']
                            curr_price= dwx.market_data[symbol]['bid']     
                        else:
                            #path_market_data = join(address,'DWX', 'DWX_Market_Data.txt')
                            #with open(path_market_data) as f2:
                                #data=json.load(f2)
                                #curr_price = data[symbol]['ask'] 
                            curr_price= dwx.market_data[symbol]['ask']

                        if position['type']== 'buy':        
                            OPEN_CUR_PRICE_DIST=curr_price-open_price
                            SL_CUR_PRICE_DIST=curr_price-position['SL']
                        else:
                            OPEN_CUR_PRICE_DIST= open_price-curr_price
                            SL_CUR_PRICE_DIST= position['SL']-curr_price
                
                        if symbol in indices:
                            #giving default sl to indices
                            if position['SL']==0.0:
                                if position['type']== 'buy':
                                    new_sl=open_price-INDEX_DEFAULT_SL
                                    new_tp=position['TP']
                                    trailed = update(ticket,new_sl, new_tp,address)
                                else:
                                    new_sl=open_price+INDEX_DEFAULT_SL
                                    new_tp=position['TP']
                                    trailed = update(ticket,new_sl, new_tp,address)
                            else:
                                #trail stop loss
                                if OPEN_CUR_PRICE_DIST>INDEX_DEFAULT_SL and SL_CUR_PRICE_DIST>INDEX_MAX_DIST_SL:
                                    if SL_CUR_PRICE_DIST>INDEX_DEFAULT_SL:
                                        if position['type']== 'buy':
                                            new_sl=position['SL']+INDEX_TRAIL_AMOUNT
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                        else:
                                            new_sl=position['SL']-INDEX_TRAIL_AMOUNT
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                    
                                    else:
                                        if position['type']== 'buy':
                                            new_sl=open_price+1
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                        else:
                                            new_sl=open_price-1
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                
                        elif symbol == 'XAUUSD':
                            #giving default sl to indices
                            if position['SL']==0.0:
                                if position['type']== 'buy':
                                    new_sl=open_price-abs(round(DEFAULT_SL/5))
                                    new_tp=position['TP']
                                    trailed = update(ticket,new_sl, new_tp,address)
                                else:
                                    new_sl=open_price+abs(round(DEFAULT_SL/5))
                                    new_tp=position['TP']
                                    trailed = update(ticket,new_sl, new_tp,address)
                            else:
                                if OPEN_CUR_PRICE_DIST>abs(round(DEFAULT_SL/5)) and SL_CUR_PRICE_DIST>abs(round(MAX_DIST_SL/5)):
                                    if SL_CUR_PRICE_DIST>abs(round(DEFAULT_SL/5)):
                                        if position['type']== 'buy':
                                            new_sl=position['SL']+abs(round(TRAIL_AMOUNT/5))
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                        else:
                                            new_sl=position['SL']-abs(round(TRAIL_AMOUNT/5))
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                            
                                    else:
                                        if position['type']== 'buy':
                                            new_sl=open_price+0.2
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                        else:
                                            new_sl=open_price-0.2
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                        # upto here do the rest
                        elif symbol in five_digit_pairs:
                            if position['SL']==0.0:
                                    multiplier=0.0001
                                    if position['type']== 'buy':
                                        new_sl=open_price-(DEFAULT_SL*multiplier)
                                        new_tp=position['TP']
                                        trailed = update(ticket,new_sl, new_tp,address)
                                    else:
                                            new_sl=open_price+(DEFAULT_SL*multiplier)
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                            else:
                                multiplier=0.0001
                                if OPEN_CUR_PRICE_DIST>(DEFAULT_SL*multiplier) and SL_CUR_PRICE_DIST>(MAX_DIST_SL*multiplier):
                                    if SL_CUR_PRICE_DIST>(DEFAULT_SL*multiplier):    
                                        if position['type']== 'buy':
                                            new_sl=position['SL']+(TRAIL_AMOUNT*multiplier)
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                        else:
                                            new_sl=position['SL']-(TRAIL_AMOUNT*multiplier)
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                    else:
                                        if position['type']== 'buy':
                                            new_sl=open_price+0.00007
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                        else:
                                            new_sl=open_price-0.00007
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                        elif symbol in three_digit_pairs:
                            multiplier=0.01
                            if position['SL']==0.0:
                                if position['type']== 'buy':
                                    new_sl=open_price-(DEFAULT_SL*multiplier)
                                    new_tp=position['TP']
                                    trailed = update(ticket,new_sl, new_tp,address)
                                else:
                                    new_sl=open_price+(DEFAULT_SL*multiplier)
                                    new_tp=position['TP']
                                    trailed = update(ticket,new_sl, new_tp,address)
                                
                            else:
                                multiplier=0.01
                                if OPEN_CUR_PRICE_DIST>(DEFAULT_SL*multiplier) and SL_CUR_PRICE_DIST>(MAX_DIST_SL*multiplier):
                                    if SL_CUR_PRICE_DIST>(DEFAULT_SL*multiplier):    
                                        if position['type']== 'buy':
                                            new_sl=position['SL']+(TRAIL_AMOUNT*multiplier)
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                        else:
                                            new_sl=position['SL']-(TRAIL_AMOUNT*multiplier)
                                            new_tp=position['TP']
                                            trailed =update(ticket,new_sl, new_tp,address)
                                    else:
                                        if position['type']== 'buy':
                                            new_sl=open_price+0.007
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
                                        else:
                                            new_sl=open_price-0.007
                                            new_tp=position['TP']
                                            trailed = update(ticket,new_sl, new_tp,address)
        except BaseException as b:
            print('error',b)
            continue    
      