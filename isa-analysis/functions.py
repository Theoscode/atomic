#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 17:30:05 2023

functions used to get data from API. 

@author: theochapman
"""

import yfinance as yf
from datetime import datetime , timedelta 
from dateutil.relativedelta import relativedelta
import pandas as pd
import requests
import time
import os
from pytz import timezone
from dash import Dash , dcc , html , Output , Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = 'browser'

NOW = datetime.now()

print(f"STARTING DAILY UPDATE : {NOW.replace(microsecond = 0)}\n")


WINDOWS = {
    'LAST_30_DAYS': NOW - timedelta(30),
    'TAX_YEAR_TO_DATE': NOW.replace(month=4, day=6, minute=0,
                                    second=0, microsecond=0)
           }

TZ = timezone("GMT")

# %% Functions

def get_yf_histo(ticker : str ="VUSA.L", start : str = (datetime.now() - timedelta(10) ).strftime("%Y-%m-%d"), end : str = datetime.now().strftime("%Y-%m-%d") , freq : str = "1d") -> pd.DataFrame :
    """
    function downloads histoical data using yfinance. 

    Parameters
    ----------
    ticker : str, optional
        ticker you wish to donwload - . The default is "^GSPC" : S&P 500
    start : str, optional
        str date for start time. The default is 5 days ago
    end : str, optional
        string date for end time. The default is datetime.now.strftime("%Y-%m-%d").
    freq : str , optional 
        frequency of data you want - options are [“1m”, “2m”, “5m”, “15m”, “30m”, “60m”, “90m”, “1h”, “1d”, “5d”, “1wk”, “1mo”, “3mo”]. The default is "1d" 
    Returns
    -------
    None.

    """
    
    try:
    
        data = yf.download(tickers = ticker , start= start , end = end , interval= freq)
        
        
        return data

    except ValueError as e:
        return e
        
        
        
def poll(max_retries : int =5, retry_delay : int =2 * 60) -> pd.DataFrame :
    
    
    retries = 0
    
    
    while retries < max_retries:

        response = get_yf_histo()
            
            
        if isinstance(response, pd.DataFrame):
            
            print("Data get : success")
            
            
            return response
            
            
        else:
            print(f"Data get : fail {retries}")
            
            
            retries += 1
            
            time.sleep(retry_delay)

        
    
    print("Max retries reached. Unable to fetch data.")
    return None


def write_csv(data = pd.DataFrame , name : str = "VUSA.L"  , path : str  = os.path.expanduser("~/atomic/isa-analysis/") ):
    """
    writes downloaded data to csv 

    Parameters
    ----------
    path : str
        path to save to.
    name : str
        DESCRIPTION.

    Returns
    -------
    None.

    """   
    
    try:
    
        data.to_csv(path + f"{name}_day.csv" ) 
        
        #data.to_csv(path + f"{name}_day.csv" , mode = 'a' ,header=not os.path.exists(path))
        
    except:
        print("error_saving")
        
        
def str_date_to_dt(str_date : str) ->datetime:
    """
    

    Parameters
    ----------
    str_date : str
        string date in format %Y-%m-%d.

    Returns
    -------
    dt : datetime
        datetime with GMT time.

    """
    
    
    date = timezone("GMT").localize(datetime.strptime(str_date , "%Y-%m-%d"))
    
    return date  
        
        
def join_update_with_hitso(path : str = os.path.expanduser("~/atomic/isa-analysis/") , history_name : str = "vusa-history.csv" , update_name : str = "VUSA.L_day.csv" ):
    """
    function reads in the history file and the update file and saves. Will need to take precuation 
    that the file you overwrite with is not None type should you lose all the histo data. 
    
    i either only save an update if there's an update or
    read in both and compare. then check wether to update. 

    Parameters
    ----------
    path : str, optional
        path where update data and historical data is daved. The default is os.path.expanduser("~/atomic/isa-anlysis/").
    history : str, optional
        history file. The default is "vusa-history.csv".
    update : str, optional
        update file. The default is "VUSA.L_day.csv".

    Returns
    -------
    None.

    """
    
    try:
        history = pd.read_csv(path + history_name )
    except FileNotFoundError:
        history = "history file not found"
        
    try:
        update = pd.read_csv(path + update_name )
    except FileExistsError :
        update = "update file not found"
        
        
    if (isinstance(history, pd.DataFrame)) & (isinstance(update, pd.DataFrame)) :
        
        
        history['dt'] = history['Date'].map(str_date_to_dt)
        
        update['dt'] = update['Date'].map(str_date_to_dt)
        
        
        last_update = history['dt'].iloc[-1]
        
        
        new_updates = update[update['dt'] > last_update]
        
        if len(new_updates) > 1:
            
            print(f"updates found! : \n{new_updates['dt']}")
            
            
            new_updates.set_index("Date").drop("dt",axis=1).to_csv(path + history_name , mode = 'a' ,header=not os.path.exists(path + history_name))
            
            
            new_history = pd.read_csv(path + "vusa-history.csv" )
            
            new_history['Date'] = new_history['Date'].map(str_date_to_dt)

            return new_history
            
            
        else:
            print("No updates ")

            return history
     
    else:
        for message in ['history not updated', history , update]:
            
            if isinstance(message, str):

                print(message)

def plot(data : pd.DataFrame , start : datetime = TZ.localize(datetime(2018, 3, 12)) , name : str  = "VUSA.L Daily", x : str = "Date" , y : str = "Price" , cols : list = ['Close','Volume'] ) : 
    
    fig = go.Figure()
    
    data = data[data['dt'] >=  start ].copy()

    
    try:
        data.set_index('dt' , inplace=True)
    except KeyError:
        ''
        
        
    for col in data : 
        
        if 'Close' in col:
            
            fig.add_trace( go.Scatter(x = data.index , y = data[col] , name = col , mode = 'lines'))
            
        elif "Volume" in col:
            
            fig.add_trace(go.Bar(x = data.index , y = data[col] , name = col , yaxis='y2' , marker=dict(color = 'black' , opacity=1, line=dict(width=2)) ))
            
    fig.update_layout(
            title = name,
            xaxis_title = x,
            yaxis_title = y,
            yaxis2 = dict(title="Volume GBF", overlaying = 'y' , side = 'right' )
        )
    
    return fig

def run_dash(last_update : str, fig_0 : go.Figure, fig_1 : go.Figure, fig_2 : go.Figure, title  : str = "ISA Analysis"):
    """
    re-generates dashboard, takes figure pdocued by plotly and name is default 
    defined

    Parameters
    ----------
    fig : go.Figure
        price and volume figure in plotly.
    title : str, optional
        Title of the Dash Board. The default is "ISA Analysis".

    Returns
    -------
    None.

    """

    app = Dash(__name__ , external_stylesheets = [dbc.themes.SANDSTONE])

    #my_text = dcc.Markdown(children = title)
    
    my_text = html.H1(children = title)
    
    my_update = html.H4(children = f"Last Update: {last_update}")
 
    my_graph = dcc.Graph(figure={})

    dropdown = dcc.Dropdown(options=['Full History', 'Tax Year To Date','Last 30 Days'],
                        value='Full History',  # initial value displayed when page first loads
                        clearable=False)
    
    app.layout = dbc.Container([my_text, dropdown , my_graph , my_update])

    
    @app.callback(
        Output(my_graph, component_property='figure'),
        Input(dropdown , component_property='value')
    )
    
    def update_graph(user_input):
        
        if user_input == "Full History":
            
            fig = fig_0
            
        elif user_input == "Tax Year To Date":
            
            fig = fig_1
            
        elif user_input == "Last 30 Days":
            
            fig = fig_2
                 
        return fig


    app.run_server(port = 8051)
     
# %%


if __name__ == '__main__':

    data = poll()

    write_csv(data)

    history = join_update_with_hitso()

    all_histo = plot(history)
    
    day_30 = plot(history , TZ.localize(WINDOWS['LAST_30_DAYS']))
    
    tytd = plot(history , TZ.localize(WINDOWS['TAX_YEAR_TO_DATE']))

    run_dash(NOW.strftime("%H:%M:%S %d-%m-%Y"), all_histo, tytd, day_30, "ISA Analysis")

end = datetime.now().replace(microsecond=0)

print(f"EXITING DAILY UPDATE : {end}\n")
