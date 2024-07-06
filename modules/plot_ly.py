#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 20:48:05 2024

some simple functions for creating plotly figures: lines, bars & subplots.

@author: theochapman
"""

import plotly.graph_objects as go 
import plotly.io as pio
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np


def rgb_to_hex(rgb: tuple) -> str:
    """
    takes a tuple which should be rgb - must hvae 3 components and converts to 
    hex equivalent which is returns. 

    Parameters
    ----------
    rgb : tuple
        rgb tuple - must have 3 components.

    Returns
    -------
    hex: str
        hex string e.g. '#ffa10'.

    """
    r = int(rgb[0])
    g = int(rgb[0])
    b = int(rgb[0])
    
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def plotly_palette(length: int,
                   base: list =["#0C1B37","#186AED", "#00D8C7", "#D4D7E0" ]) -> list:
    """
    Takes length as the number of colours needed, and a base set of colours to interpolate between. 
    If length is less than or equal to 4 then just returns base. 

    Parameters
    ----------
    length : int
        number of colours needed.
    base : list, optional
        base list of colours to interpolate between. The default is ["#0C1B37","#186AED", "#00D8C7", "#D4D7E0" ].

    Returns
    -------
    list
        list of interpolated colours.

    """
    
    if length <= 4:
        
        return base
    
    else:
        
        segs = (length - len(base)) / len(base)
        
        interpolated = []
        
        for i in range(0, len(base) -1):
            
            start_colour = np.array(px.colors.hex_to_rgb(base[i]))
            
            end_colour = np.array(px.colors.hex_to_rgb(base[i+1]))
            
            colour_range = np.linespace(0,1,2 + int(np.ceil(segs)), endpoint=True)
            
            for t in colour_range:
                
                interpolated_colour = rgb_to_hex(tuple(1-t) * start_colour + t * end_colour)
                
                if interpolated_colour not in interpolated:
                    
                    interpolated.append(interpolated_colour)
                    
        return interpolated


def plot_lines(df: pd.DataFrame, order:list, palette: list,stack: bool, fig_name: str, x_title:str, y_title: str, path:str, name:str):
    """
    Simple plotly function that plots from a dataframe (all columns), anotates with titles 
    and saves with name.png in path provided.
    
    X axis is assumed to be the index

    Parameters
    ----------
    df : pd.DataFrame
        DESCRIPTION.
    order: list
        column names in order to plot. 
    palette: list
        plotly palette, i.e. colours for lines. 
    fig_name : str
        DESCRIPTION.
    x_title : str
        DESCRIPTION.
    y_title : str
        DESCRIPTION.
    path : str
        DESCRIPTION.
    name : str
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    fig  = go.figure()
    
    for col in order:
        
        index = list(df.columns).index(col)
        
        if stack == False:
        
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col, line=dict(color=palette[index])))
        
        elif stack == True:
            
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col, stackgroup="one", line=dict(color=palette[index])))

        
    fig.update_layout(
        title=fig_name,
        xaxis_title=x_title,
        yaxis_title = y_title)
    
    fig.show()
    
    pio.write_image(
        fig,
        f"{path}/{name}.png",
        width=1500,
        height=1000
        )
    
    
    
def plot_bars(df: pd.DataFrame, order: list, palette: list, title:str,  x_title:str, y_title: str,stack:bool, path:str, name:str):
    """
    plots a bar chart using data in dataframe, in order defined and with colours in palette annotated with 
    titles provided & saves with name in path. 

    Parameters
    ----------
    df : pd.Dataframe
        data to plot, uses index as x axis.
    order : list
        order to plot columns in. Order is a list of column names
    palette : list
        plotly pallette, list of colours to use in figure - in hex form.
    title : str
        title of figure.
    x_title : str
        title of x axis.
    y_title : str
        title for y axis.
    stack : bool
        if true will stack bars, false does not stack bars
    path : str
        path to save figure in.
    name : str
        name of .png file.

    Returns
    -------
    None.

    """

    fig = go.Figure()

    for col in order:

        index = order.index(col)
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y = df[col],
                name=col,
                marker_color=palette[index]))
        
        
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title
        )
    
    if stack == True:
        
        fig.update_layout(barmode="stack")
        
        
    fig.show()
    
    pio.write_image(
        fig,
        f"{path}/{name}.png",
        width=1500,
        height=1000
        )
        
        
        
def bar_and_scatter(bar: pd.Series, line: pd.Series, palette: list, title:str,  x_title:str, y_title: str, y2_title: str, path:str, name:str):
    """
    Sets 2 axis, one to plot data in line df another to plot bar data. 

    Parameters
    ----------
    bar : pd.DataFrame
        DESCRIPTION.
    line : pd.DataFrame
        DESCRIPTION.
    palette : list
        DESCRIPTION.
    title : str
        DESCRIPTION.
    x_title : str
        DESCRIPTION.
    y_title : str
        DESCRIPTION.
    y2_title : str
        DESCRIPTION.
    path : str
        DESCRIPTION.
    name : str
        DESCRIPTION.

    Returns
    -------
    None.

    """    
        
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=bar.index, y=bar, name=bar.name, marker_color=palette[0]), secondary_y=False)
    
    fig.add_trace(go.Scatter(x=line.index, y=line,
                             mode= "lines",name=line.name, line=dict(color=palette[1])), secondary_y=True)
    
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        yaxis2_title= y2_title
        )
    
    fig.show()
    
    pio.write_image(
        fig,
        f"{path}/{name}.png",
        width=1500,
        height=1000
        )
        
        
        
        
        
        
        
        
        