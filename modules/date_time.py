#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 20:30:02 2024

my own datetime module

@author: theochapman
"""

from datetime import datetime, timedelta
from pytz import timezone
import numpy as np

def ts_to_dt(ts: int) -> datetime:
    """
    Takes a timestamp int object and converts to a datetime object with the 
    timezone set to GMT.

    Parameters
    ----------
    ts : int
        timestamp integer not timestamp format.

    Returns
    -------
    dt: datetime
        datetime object with tzinfo set to GMT.

    """
    tz = timezone("GMT")
    
    dt = datetime.fromtimestamp(ts,tz)
    
    return dt


def dt_to_ts(dt: datetime) -> int:
    """
    takes a datetime.datetime object, does not require tzinfo set but beware 
    python may assume local tinezome if not defined in datetime.

    Parameters
    ----------
    dt : datetime
        datetime obj.

    Returns
    -------
    ts: int
        timestamp for input datetime.

    """
    
    date = int(datetime.timestamp(dt))
    
    return date 


def create_list_dates(start: datetime, end: datetime, freq: str)-> list:
    """
    takes 2 dates, start must be before end & a frequency. Tzinfo does not need 
    to be defined but reulsting list will carry tzinfo of inputs. 
    
    Note: tzinfo must be defined in both start and end or neither.

    Parameters
    ----------
    start : datetime
        first datetime.
    end : datetime
        last datetime.
    freq : str
        frequency of resulting list of dates ['minutes', 'hour','days'].

    Returns
    -------
    list
        list of dates at defined frequency between start and end (including both).

    """
    
    if freq == "days":
        
        dates = [
            start + timedelta(days=x) for x in range(int((end - start).total_seconds())) // 86400]
        
    if freq == "hours":
        
        dates = [
            start + timedelta(hours=x) for x in range(int((end - start).total_seconds())) // 3600]
        
        
    if freq == "days":
        
        dates = [
            start + timedelta(minutes=x) for x in range(int((end - start).total_seconds())) // 60]
        
        
    return dates


def create_list_ts(start: int, end: int, freq: str)-> list:
    """
    takes 2 dates, start must be before end & a frequency. Tzinfo does not need 
    to be defined but reulsting list will carry tzinfo of inputs. 
    
    Note: tzinfo must be defined in both start and end or neither.

    Parameters
    ----------
    start : datetime
        first datetime.
    end : datetime
        last datetime.
    freq : str
        frequency of resulting list of dates ['minutes', 'hour','days'].

    Returns
    -------
    list
        list of dates at defined frequency between start and end (including both).

    """
    
    if freq == "days":
        
        dates = [
            start + 86400* x for x in range(int(end - start)) // 86400]
        
    if freq == "hours":
        
        dates = [
            start + 3600* x for x in range(int(end - start)) // 3600]
        
        
    if freq == "days":
        
        dates = [
            start + 60* x for x in range(int(end - start)) // 60]
        
        
    return dates


def np_dt64_to_datetime(np_dt64: np.datetime64) -> datetime:
    """
    converts numpy datetime 64 to datetime object

    Parameters
    ----------
    np_dt64 : np.datetime64
        DESCRIPTION.

    Returns
    -------
    datetime
        DESCRIPTION.

    """
    
    return datetime.fromtimestamp(datetime.timestamp(np_dt64))

        
        
        
        
