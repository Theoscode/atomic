# -*- coding: utf-8 -*-
"""
Spyder Editor

These are functions from CCdata's data-api. though many of these may require more than a free key 
I keep them incase I ever need them. Perhaps for personal investing. 


This is a temporary script file.
"""

import requests
import urllib
import pandas as pd

def markets_instruments(types:str, key:str,instruments:str="", market:str="", status:str="") -> dict:
    """
    Function takes at minimum an API key, as well as strings that may contain lists comma seperated lists 
    of instruments, markets and status. 
    
    Note: Only API key is required. If no other params specified then returns data on all markets.
    
    If error returns none and print errors.

    Parameters
    ----------
    types : str
        either ['spot','reference_rate','futures','options','futures_indices','onchain'] for either spot markets & instruments or reference rate.
    key : str
        your api key.
    instruments : str, optional
        list of insturment pairs "BTC-USD,ETH-USD,DOGE-USDT". The default is "".
    market : str, optional
        single market string i.e. one of  ["ccix","cadli","ccxrp"]. The default is "".
    status : str, optional
        List of instrument/market statuses to return choose from "ACTIVE,IGNORED,RETIRED,EXPIRED". The default is "".

    Returns
    -------
    dict
        raw response['Data'] output from API. 

    """
    if types == "spot":
        
        base = "spot"
        
    elif types == "reference_rate":
        
        base = "index/cc"
        
    elif types == "futures":
        
        base = "futures"
        
    elif types =="options":
        
        base = "options"
    
    elif types == 'futures_indices':
        
        base = 'index'
        
    elif types == 'onchain':
        
        base = 'onchain'
    
    url = f"https://data-api.cryptocompare.com/{base}/v1/markets/instruments?market={market}&instruments={instruments}&instrument_status={status}&api_key={key}"
    
    try:
        
        response = requests.get(url).json()
        
        return response['Data']
    
    except urllib.error.HTTPError:
        
        print(f"HTTP ERROR: {url}")
        
        
   
def ohlc(types:str, market:str, instrument:str, start:int, end:int,freq:str, key:str, groups:str="") -> pd.DataFrame:
    """
    General function that downloads CCdata OHLC data formats, as the params and output groups are the same 
    across all CCdata data forms. Essentially returns OHLCV+ data between 2 timestamp points : start and end for a given market and instrument. 

    Parameters
    ----------
    types : str
        type of data to request, choose from ['spot','reference_rate','futures','options','futures_indices','onchain']: 
    market : str
        market name, either exchange name 'kraken' or reference rate market i.e. 'ccix'.
    instrument : str
        instrument name, i.e. BTC-USD, for futures & options these will be more complicated.
    start : int
        first timestamp you want .
    end : int
        last/most recent timestamp you want.
    freq: str
        frequency of data you want, ['days','hours','minutes']
    key: str
        your api key.
    groups : str, optional
        output groups . The default is "".

    Returns
    -------
    None.

    """
    
    if types == "spot":
        
        base = "spot"
        
    elif types == "reference_rate":
        
        base = "index/cc"
        
    elif types == "futures":
        
        base = "futures"
        
    elif types =="options":
        
        base = "options"
    
    elif types == 'futures_indices':
        
        base = 'index'
        
    df = pd.DataFrame()
    
    ts = end
    
    should_continue = True
    
    while should_continue == True:
        
        url = f"https://data-api.cryptocompare.com/{base}/v1/historical/{freq}?market={market}&instrument={instrument}&groups={groups}&to_ts={ts}&limit=2000&apiKey={key}"
    
        try:
            
            response = requests.get(url).json()
            
            if len(response['Err']) >0:
                
                should_continue = False
                
                print(response['Err'])
                
            else:
                
                df_new = pd.DataFrame(response['Data'])
                
                df = pd.concat([df,df_new])
                
                ts = df_new['TIMESTAMP'].iloc[0]
                
                if ts < start:
                    
                    should_continue = False
                    
        except urllib.error.HTTPError:
            
            print(f"HTTP ERROR with url : {url}")
            
            
    if len(df) > 0:
        
        return df[(df['TIMESTAMP'] <= end) & (df['TIMESTAMP'] >= start)]
    
    
    
def messages_and_trades(types:str, instrument:str, market: str, hour_ts: int, key:str)->pd.DataFrame:
    """
    function can be used to download a set of historical messages/trades for a given type of data 
    for the hour, instrument and market given. 

    Parameters
    ----------
    types : str
        choose from : ['spot','reference_rate','futures','options','futures_indices','onchain'].
    instrument : str
        i.e. BTC-USD, for futures, options etc instrument names are more complicated.
    market : str
        Market name, will either be exchange name 'kraken' or reference rate name 'ccix'.
    hour_ts : int
        timestamp anywehre within the hour you want.
    key : str
        your api key.

    Returns
    -------
    df : pd.DataFrame
        raw data in dataframe format. 

    """
    
    if types == "spot":
        
        base = "spot"
        
        tm = "trades"
        
    elif types == "reference_rate":
        
        base = "index/cc"
        
        tm = "messages"
        
    elif types == "futures":
        
        base = "futures"
        
        tm = "trades"
        
    elif types =="options":
        
        base = "options"
        
        tm = "trades"
    
    elif types == 'futures_indices':
        
        base = 'index'
        
        tm = "messages"
        
    
    root = f"https://data-api.cryptocompare.com/{base}/v1/historical/{tm}/hour?"
    
    url = root + f"market={market}&instrument={instrument}&hour_ts={hour_ts}&apiKey={key}"
    
    try:
        
        response = requests.get(url).json()
        
        df = pd.DataFrame(response['Data'])
        
        return df
    
    except urllib.error.HTTPError:
        
        print(f"HTTP Error: {url}")
    
    
        