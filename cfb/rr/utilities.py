#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 12:04:12 2024

@author: theo
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import json
from pytz import timezone
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots

pio.renderers.default = "browser"


def read_json(path: str, file: str) -> dict:
    """
    attempts to read a json file for a given path/directory and file name.
    If file not found error returns none

    Parameters
    ----------
    path : str
        directory path of file.
    file : str
        file name.

    Returns
    -------
    dict
        the requested file as python dict obj.

    """

    try:
        dct = json.load(open(f"{path}{file}"))

        return dct

    except FileNotFoundError:

        print(f"WARNING FILE NOT FOUND: {path}{file}")


def ts_to_dt(ts: int) -> datetime:
    """
    takes a timestamp 'ts' (can also be a float) and converts to a datetime
    object with tz info set as GMT

    Parameters
    ----------
    ts : int
        timestamp.

    Returns
    -------
    datetime
        GMT datetime.

    """

    tz = timezone("GMT")
    dt = datetime.fromtimestamp(ts, tz)

    return dt


def create_list_dates(start: datetime, end: datetime, freq: str) -> list:
    """
    takes 2 dates (tz info does not need to be defined but resulting list
                   will have the tz info of the inputs)
    and returns a list of  datetimes between them.

    Parameters
    ----------
    start : datetime
        first date you want, furthest back in time.
    end : datetime
        last date you want , most recent.
    freq : str
        'day','hour','minute'

    Returns
    -------
    dates : list
        List of dates between and including start/end at freq defined

    """

    if freq == "days":
        dates = [
            start + timedelta(days=x)
            for x in range(int((end - start).total_seconds()) // 86400 +1)
        ]
    elif freq == "hours":
        dates = [
            start + timedelta(hours=x)
            for x in range(int((end - start).total_seconds()) // 3600+1)
        ]
    elif freq == "minutes":
        dates = [
            start + timedelta(minutes=x)
            for x in range(int((end - start).total_seconds()) // 60+1)
        ]

    return dates


def filter_window(data: dict, date: datetime):
    """


    Parameters
    ----------
    data : dict
        DESCRIPTION.
    date : datetime
        DESCRIPTION.

    Returns
    -------
    None.

    """

    df = pd.DataFrame(data["trades"])

    df["time"] = df["time"].astype(float)

    df["datetime"] = (df["time"] / 1000).map(ts_to_dt)

    df.sort_values("datetime", inplace=True)

    df = df[
        (df["time"] >= float(data["time"]) - 3600 * 1000)
        & (df["time"] < float(data["time"]))
    ]

    if (
        len(
            df[
                (df["time"] < float(data["time"]) - 3600 * 1000)
                & (df["time"] >= float(data["time"]))
            ]
        )
        > 0
    ):

        print(
            df[
                (df["time"] < float(data["time"]) - 3600 * 1000)
                & (df["time"] >= float(data["time"]))
            ]
        )

    return df



def erroneous_check(data: dict) -> dict:
    """


    Parameters
    ----------
    data : dict
        DESCRIPTION.

    Returns
    -------
    None.

    """

    for trade in data["trades"]:

        error = False

        index = data["trades"].index(trade)

        for i in ["exchange", "time", "price", "size"]:

            if i not in trade:

                data["trades"][index].update({f"missingField {i}": True})

                print(f"Trade missing {i} : \n{trade}")

                error = True

        if error == False:

            if not isinstance(trade["price"], (float, int)):

                data["trades"][index].update({"price_non_numerical": True})

                print("ERROR")

            if not isinstance(trade["size"], (float, int)):

                data["trades"][index].update({"size_non_numerical": True})

                print("ERROR")

            try:

                if trade["price"] < 0:

                    data["trades"][index].update({"price_negative": True})

                    print("ERROR")

                if trade["size"] < 0:

                    data["trades"][index].update({"size_negative": True})

                    print("ERROR")

            except TypeError:

                print("Data Not Numerical")

    return data


def weighted_median(df: pd.DataFrame) -> float:
    """


    Parameters
    ----------
    df : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    float
        DESCRIPTION.

    """
    df = df.sort_values("price").reset_index().copy()

    df["cumvol_percent"] = df["size"].cumsum() / df["size"].sum()

    if df["cumvol_percent"].iloc[0] >= 0.5:

        w_median = df["price"].iloc[0]

        exchange = df["exchange"].iloc[0]

    else:

        w_median_index = df[df["cumvol_percent"] < 0.5].index[-1] + 1

        if df["cumvol_percent"].iloc[w_median_index] == 0.5:

            w_median = (
                df["price"].iloc[w_median_index]
                + df["price"].iloc[w_median_index + 1]
            ) / 2

            exchange = df["exchange"].iloc[w_median_index]

        else:
            w_median = df["price"].iloc[w_median_index]

            exchange = df["exchange"].iloc[w_median_index]

    return w_median, exchange


def potentially_errorneous_check(data:pd.DataFrame,ped_param:float ):
    
    wm_e = {}

    medians = []

    for exchange in list(data["exchange"].unique()):

        wm_e.update(
            {
                exchange: weighted_median(
                    data[data["exchange"] == exchange]
                )[0]
            }
        )

        medians.append(
            weighted_median(data[data["exchange"] == exchange])[0]
        )

    median_wm_e = np.median(medians)

    potentially_erroneous = [
        i for i in wm_e if abs(wm_e[i] / median_wm_e - 1) > ped_param/100
    ]
    
    return potentially_erroneous, wm_e, median_wm_e


def calc(df: pd.DataFrame, partition: int,  calc_time: float, first_last : bool) -> [pd.DataFrame, float]:
    """
    function to calc _RR indices: Partitions into buckets, 
    Calculates the VWM of each bucket & averages into the final TWAP _RR
    price for the hour. 
    
    Each stage of the calculation is returned.
    
    !!! Still fixed to one hour. 


    Parameters
    ----------
    df : pd.DataFrame
        input data consissting of trades, formateed and all erroneous and potentially
        errorneous data removed.
    partition : int
        The length of the partition windows in minutes. i.e. 5 is 5 minutes. 
    calc_time : float
        The Time assiciated with the _RR final price. 
    first_last : bool
        TRUE: The first and last trade of each bucket will be saved.
        FALSE: Not saved. 

    Returns
    -------
    

    """

    start = int(calc_time) - 3600

    bucket_starts = [start + 60 * i for i in range(0, 60, partition)]

    output = pd.DataFrame()
    
    weighted_medians = []

    for bs in bucket_starts:

        print(f"Calcing Bucket : {ts_to_dt(bs)}")

        bucket = df[
            (df["time"] >= bs* 1000) & (df["time"] < (bs + 60 * partition) * 1000)
        ].copy()

        if len(bucket) > 0:

            vwm, exchange = weighted_median(bucket)
            
            weighted_medians.append(vwm)
            
            if first_last == True:
                
                first = bucket.head(1).copy().reset_index(drop=True).drop('time',axis=1).rename(columns={"exchange": "first_trade_exchange","datetime":"first_trade_datetime","size":"first_trade_size","price":"first_trade_prtice"})
                
                last = bucket.tail(1).copy().reset_index(drop=True).drop('time',axis=1).rename(columns={"exchange": "last_trade_exchange","datetime":"last_trade_datetime","size":"last_trade_size","price":"last_trade_prtice"})

                output = pd.concat([output, pd.concat([pd.DataFrame({"ExecTime":[datetime.fromtimestamp(bs)], "VWM_Price":[vwm], "VWM_Exchange":[exchange]}),first, last],axis=1)])
                
            else: 
                
                output = pd.concat([output, pd.DataFrame({"ExecTime":[datetime.fromtimestamp(bs)], "VWM_Price":[vwm], "VWM_Exchange":[exchange]})])
                
    return np.mean(weighted_medians), output


def write_csv(index_name: str, data: pd.DataFrame, output_path: str):
    """
    writes dataframe to CSV

    Parameters
    ----------
    index_name : str
        DESCRIPTION.
    data : pd.DataFrame
        DESCRIPTION.
    output_path : str
        DESCRIPTION.

    Returns
    -------
    None.

    """

    data.to_csv(
        output_path + f"{index_name}.csv",
        mode="a",
        header=not os.path.exists(output_path + f"{index_name}.csv"),
        index=False,
    )


def plot(
    df_plot: pd.DataFrame,
    order: list,
    palette: list,
    title: str,
    x_title: str,
    y_title: str,
    path: str,
    name: str,
):
    """
    plots via plotly in browser the df input.

    Parameters
    ----------
    df_plot : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    plotly plot in browser

    """
    fig = go.Figure()

    for col in order:

        index = order.index(col)

        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot[col],
                mode="lines",
                name=col,
                stackgroup="one",
                line=dict(color=palette[index]),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        barmode="stack",
    )
    fig.show()

    pio.write_image(
        fig,
        f"{path}/{name}.png",
        width=1500,
        height=1000,
    )
    
    
def write_excel_append(path: str, file_name: str,sheet_name:str, data:dict):
    """
    function takes a path and a file name and a data to save. Function uses 
    keys in dictionary as workbook sheet names and values must be dataframes 
    but apparently you have to send dict data to df only.

    Parameters
    ----------
    path : str
        File path to save output in.
    file_name : str
        The name of the file for.
    sheet_name : str
        Name for the sheet you wish to write too. 
    data : dict
        DESCRIPTION.

    Returns
    -------
    None.

    """
    with pd.ExcelWriter(f"{path}{file_name}.xlsx", mode='a', engine='openpyxl') as writer:
        
        
        
        


def plotly_palette(
    number: int,
    base: list = [
        "#0C1B37",  # dark navy
        "#186AED",  # blue
        "#00D8C7",  # teal
        "#D4D7E0",  # grey.
    ],
) -> list:
    """


    Parameters
    ----------
    number : int
        the minimum number of colours needed - normally columns to plot.
    base : list, optional
        list of colours to create a palette between. The default is ["#0C1B37",  # dark navy
                                     "#186AED",  # blue
                                     "#00D8C7",  # teal
                                     "#D4D7E0"  # grey.    ].

    Returns
    -------
    interpolated_palette : list
        list of rgb colours to use in plotting should be CCdata colours if default
        is used.

    """
    if number <= 4:

        return base

    else:

        segs = (number - len(base)) / len(base)

        interpolated_palette = []

        for i in range(0, len(base) - 1):

            start_color = np.array(px.colors.hex_to_rgb(base[i]))

            end_color = np.array(px.colors.hex_to_rgb(base[i + 1]))

            color_range = np.linspace(
                0, 1, 2 + int(np.ceil(segs)), endpoint=True
            )

            for t in color_range:

                interpolated_color = rgb_to_hex(
                    tuple((1 - t) * start_color + t * end_color)
                )

                if interpolated_color not in interpolated_palette:

                    interpolated_palette.append(interpolated_color)

        return interpolated_palette


def rgb_to_hex(rgb: tuple) -> str:
    """
    takes a tuple to be rbg - must have 3 components and figures
    out hex equivalant - which it returns

    Parameters
    ----------
    rgb : tuple
        rgb tuple - must have 3 components.

    Returns
    -------
    hex : str
        hex string  e.g.'#ffa10'.

    """
    r = int(rgb[0])
    g = int(rgb[1])
    b = int(rgb[2])
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def plot_bar_and_scatter(bar, line, title, x_name, y1_name, y2_name):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=bar.index, y=bar, name=bar.name, marker_color="#186AED"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=line.index,
            y=line,
            mode="lines",
            name=line.name,
            line=dict(color="black"),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=title,
        xaxis_title=x_name,
        yaxis_title=y1_name,
        yaxis2_title=y2_name,
        # legend=dict(x=0, y=1, traceorder="normal"),
    )

    fig.show()


def plot_lines(
    df_plot: pd.DataFrame,
    order: list,
    palette: list,
    title: str,
    x_title: str,
    y_title: str,
    path: str,
    name: str,
):
    """
    plots via plotly in browser the df input.

    Parameters
    ----------
    df_plot : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    plotly plot in browser

    """
    fig = go.Figure()

    for col in order:

        index = order.index(col)

        if "Threshold" in col:

            fig.add_trace(
                go.Scatter(
                    x=df_plot.index,
                    y=df_plot[col],
                    mode="lines",
                    name=col,
                    line=dict(color="black", dash="dash"),
                )
            )

        if col == "AllExchangeMedian":

            fig.add_trace(
                go.Scatter(
                    x=df_plot.index,
                    y=df_plot[col],
                    mode="lines",
                    name=col,
                    line=dict(color="black", dash="dash"),
                )
            )

        elif col not in [
            "AllExchangeMedian",
            "lowerThreshold",
            "upperThreshold",
        ]:

            fig.add_trace(
                go.Scatter(
                    x=df_plot.index,
                    y=df_plot[col],
                    mode="lines",
                    name=col,
                    line=dict(color=palette[index]),
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
    )
    fig.show()

    pio.write_image(
        fig,
        f"{path}/{name}.png",
        width=1500,
        height=1000,
    )


def plot_daily_bar_chart(
    df, x_column, y_column, color_column, title, x_label, y_label, palette
):

    i = 0

    traces = []
    for color_value in df[color_column].unique():
        subset = df[df[color_column] == color_value]
        trace = go.Bar(
            x=subset[x_column],
            y=subset[y_column],
            name=str(color_value),
            # marker_color=palette[i],
        )
        traces.append(trace)

        i += 0

    # Create layout
    layout = go.Layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        barmode="group",
    )

    # Create figure
    fig = go.Figure(data=traces, layout=layout)

    # Show the plot
    fig.show()


def plot_bar_chart(df, palette, title, x_title, y_title):

    i = 0

    fig = go.Figure()

    for col in df:

        fig.add_trace(
            go.Bar(x=df.index, y=df[col], name=col, marker_color=palette[i])
        )

        i += 1

    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
    )
    fig.show()
