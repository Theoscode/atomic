#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 12:07:10 2024

@author: theo
"""

import utilities
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os
from pytz import timezone
import yaml

def run(read_path:str, save_path :str, start: datetime, end:datetime, freq:str, tz:str, close:int, window:int, partition:int, markets:list,ped:float, local : bool, first_last : bool ):
    """
    Main function for generating RR indices varying depending on inputs. Also has the ability to save data regarding the index
    depending on the list of bools parsed at the end. 
    
    No data is return but saved in path.

    Parameters
    ----------
    read_path : str
        path to read output data from.
    save_path : str
        path to save output data to.
    start : datetime
        First calc time.
    end : datetime
        Last Calc time.
    freq : str
        Frequency of cacluation: 'days' 'hours'
    tz : str
        Timezone used for EOD calc and for dates in output.
    close : int
        Close hour if calculating EOD.
    window : int
        Length of window minutes, default is 60.
    partition : int
        Partition length in minutes, default is 5 .
    markets : list
        List of markets to use as input in calc.
    ped : float
        The PED parameter as a %. i.e. a float of 10 means 10% PED PARAM. 
    local : bool
        If True will try to read .json trade files locally.
    first_last : bool
        If true will save first and last day.

    Returns
    -------
    None.

    """
    
    print(f"STARTING CALC \n START: {start} \n END: {end} \n FREQ: {freq} \n MARKETS: {markets} \n WINDOW: {window} \n K: {partition} \n SAVING: {save_path}")

    tz = timezone(tz)

    os.makedirs(save_path, exist_ok=True)

    dates = utilities.create_list_dates(
        tz.localize(start), tz.localize(end), freq
    )
    
    if freq == 'days':
        
        dates = [i.replace(hour=close) for i in dates]

    pe_ts = pd.DataFrame()

    volumes = pd.DataFrame()

    for date in dates:
        
        print(
            f"Starting: {date}"
        )
        
        if local == True:

            data = utilities.read_json(read_path, f"{date.date()}.json")
            
        else:
            
            ### download from s3 - not written yet 
            ''

        

        data = utilities.erroneous_check(data)

        df = utilities.filter_window(data, date)  # ASSUMES HOUR WINDOW TO FILTER. 

        ped_exchanges, vwm_e, median_vwm_e = utilities.potentially_errorneous_check(df, ped)
        
        if len(ped_exchanges) > 1:
            
            print(f"PED PARARM REMOVING: {ped_exchanges}")
            
            df = df[~df['exchange'].isin(ped_exchanges)] ## CHECK THIS WORKS. 
            

        # df["Volume"] = df["price"] * df["size"]

        # volumes = pd.concat(
        #     [
        #         volumes,
        #         df[["exchange", "Volume"]]
        #         .groupby("exchange")
        #         .sum()
        #         .rename(columns={"Volume": date + timedelta(hours=16)})
        #         .T,
        #     ]
        # )

        # wm_e.update(
        #     {
        #         "lowerThreshold": pe_median * 0.9,
        #         "upperThreshold": pe_median * 1.1,
        #         "AllExchangeMedian": pe_median,
        #     }
        # )

        # pe_ts = pd.concat([pe_ts, pd.DataFrame(wm_e, index=[date.date()])])



        ccrr, weighted_medians = utilities.calc(df, partition, datetime.timestamp(date) ,first_last)

        utilities.write_csv(
            "LTCUSD_RR",
            pd.DataFrame(
                {
                    "time": [data["time"]],
                    "Date": [utilities.ts_to_dt(int(data["time"]) / 1000)],
                    "LTCUSD_RR": [median.round(4)],
                }
            ),
            save_path,
        )

        utilities.write_csv("WeightedMedians", weighted_medians, save_path)

    # weights = volumes.apply(lambda x: x / volumes.sum(axis=1))

    # ltcusd_rr = pd.read_csv(save_path + "LTCUSD_RR.csv").set_index("Date")

    # ltcusd_rr["Volume"] = volumes.sum(axis=1)

    # utilities.plot_bar_and_scatter(
    #     ltcusd_rr["Volume"],
    #     ltcusd_rr["LTCUSD_RR"],
    #     "LTCUSD_RR Index Value and Volumes",
    #     "Date",
    #     "Volume USD",
    #     "Price USD",
    # )

    # palette = utilities.plotly_palette(len(weights.columns))

    # utilities.plot(
    #     weights,
    #     list(weights.mean().sort_values().index),
    #     palette,
    #     "LTCUSD_RR Input Weights",
    #     "Date",
    #     "Weight",
    #     save_path,
    #     "input_weights",
    # )

    # palette = utilities.plotly_palette(len(pe_ts.columns))

    # utilities.plot_lines(
    #     pe_ts,
    #     list(pe_ts.columns),
    #     palette,
    #     "Potentially Erroneous Exchange Medians",
    #     "Date",
    #     "Median Prices USD",
    #     save_path,
    #     "potential_errors",
    # )

    # bucket_data = pd.read_csv(
    #     save_path + "WeightedMedians.csv", parse_dates=["datetime"]
    # )

    # bucket_data["day"] = bucket_data["datetime"].dt.date

    # bucket_data["dummy"] = 10

    # count = (
    #     bucket_data[["day", "Exchange", "dummy"]]
    #     .groupby(["day", "Exchange"])
    #     .count()
    #     .reset_index()
    # )

    # utilities.plot_daily_bar_chart(
    #     count,
    #     "day",
    #     "dummy",
    #     "Exchange",
    #     "Exchange use in Bucket Count Daily",
    #     "Day",
    #     "Count",
    #     palette,
    # )

    # utilities.plot_bar_chart(
    #     bucket_data[["datetime", "Trades"]].set_index("datetime"),
    #     palette,
    #     "Bucket Count",
    #     "Bucket Start",
    #     "Trade Count",
    # )

    # for date in list(bucket_data.index):

    #     for e in bucket_data.loc[date]["NoTradesFrom"]:

    #         print(type(e))


if __name__ == "__main__":
    
    CONFIG = yaml.safe_load(open("config.yml"))
    
    READ_PATH = CONFIG['inputs']['read_path']

    SAVE_PATH = os.path.expanduser(f"~/{CONFIG['outputs']['root']}") + CONFIG['outputs']['expand']
    
    ASSET = CONFIG['inputs']['asset']
    
    QUOTE = CONFIG['inputs']['quote']

    START = CONFIG['inputs']['start']

    END = CONFIG['inputs']['end']
    
    FREQ = CONFIG['inputs']['freq']

    TZ = CONFIG['inputs']['tz']
    
    CLOSE = CONFIG['inputs']['close']
    
    WINDOW = CONFIG['inputs']['window_length']
    
    PARTITION = CONFIG['inputs']['partition_length']
    
    MARKETS = CONFIG['inputs']['markets']
    
    PED = CONFIG['inputs']['ped_parameter']
    
    READ_LOCALLY = CONFIG['inputs']['read_input_locally']
    
    SAVE_FIRST_LAST = CONFIG['outputs']['save_first_last']


    run(READ_PATH,SAVE_PATH, START, END, FREQ, TZ, CLOSE, WINDOW, PARTITION, MARKETS, PED, READ_LOCALLY, SAVE_FIRST_LAST)
