#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 19:03:54 2024

min-api functions, mainly index stuff i.e. underlying & index values. 


@author: theochapman
"""
import pandas as pd
import requests
import urllib

def ccdata_minapi_index_ohlc(index:str, start: float, end: float, freq:str, key:str) -> pd.DataFrame:
    """
    Function returns data (if found) for a given index between a start and an end timestamp at 
    a given frequency. If error or no data found returns None.

    Parameters
    ----------
    index : str
        Name of index i.e. MVDA.
    start : float
        First timestamp you want.
    end : float
        Last timestamp you want (included).
    freq : str
        Frequency of data to be returned ['day','hour','minute'].
    key : str
        your api key.

    Returns
    -------
    df: pd.DataFrame
        df with OHLC data if any - other than moving from dict to df no changes made.

    """
    
    df = pd.DataFrame()
    
    should_continue = True
    
    ts = end
    
    while should_continue == True:
        
        url = f"https://min-api.cryptocompare.com/data/index/histo/{freq}?indexName={index}&limit=2000&toTs={ts}&api_key={key}"
        
        try:
            
            response = requests.get(url).json()
            
            if (response["Response"] == "Error") & (response['Message'] == "Minute data for undefined-undefined is only available for the last 7 days"):
                
                should_continue = False
                
                print(response['Message'])
                
            else:
                
                df_new = pd.DataFrame(response['Data'])
                
                df = pd.concat([df,df_new])
                
                ts = df_new['time'].iloc[0]
                
                if ts < start:
                    
                    should_continue = False
                    
        except urllib.error.HTTPError:
            
            should_continue = False
            
            print(f"HTTP Error check url : {url}")
            
            
        except:
            
            print(f"Unnexpected error for {url}")
            
            should_continue = False
            
    if len(df) > 0:
        
        return df[(df['time'] <= end) & (df['time'] >= start)]
    
    
def ccdata_minapi_underlying(market: str, base: str, quote: str, start: float, end: float, freq:str, key:str) -> pd.DataFrame:
    """
    Function returns data (if found) for a given underlying between a start and an end timestamp at 
    a given frequency. If error or no data found returns None.

    Parameters
    ----------
    market : str
        Name of index market i.e. MVDA.
    base: str 
        ticker of base asset 
    quote : str
        ticker of quote currency.
    start : float
        First timestamp you want.
    end : float
        Last timestamp you want (included).
    freq : str
        Frequency of data to be returned ['day','hour','minute'].
    key : str
        your api key.

    Returns
    -------
    df: pd.DataFrame
        df with OHLC data if any - other than moving from dict to df no changes made.

    """
    
    df = pd.DataFrame()
    
    should_continue = True
    
    ts = end
    
    while should_continue == True:
        
        url = f"https://min-api.cryptocompare.com/data/index/histo/underlying/{freq}?market={market}&base={base}&quote={quote}&limit=2000&toTs={ts}&api_key={key}"
        
        try:
            
            response = requests.get(url).json()
            
            if (response["Response"] == "Error") & (response['Message'] == "Minute data for undefined-undefined is only available for the last 7 days"):
                
                should_continue = False
                
                print(response['Message'])
                
            else:
                
                df_new = pd.DataFrame(response['Data'])
                
                df = pd.concat([df,df_new])
                
                ts = df_new['time'].iloc[0]
                
                if ts < start:
                    
                    should_continue = False
                    
        except urllib.error.HTTPError:
            
            should_continue = False
            
            print(f"HTTP Error check url : {url}")
            
            
        except:
            
            print(f"Unnexpected error for {url}")
            
            should_continue = False
            
    if len(df) > 0:
        
        return df[(df['time'] <= end) & (df['time'] >= start)]   
    
    