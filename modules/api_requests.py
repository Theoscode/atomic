#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 21:50:51 2024

@author: theochapman
"""

import requests
import urllib


def make_requests(url: str, key:str) -> dict:
    """
    simple function for requesting data from an API and reurns the response 
    decoded from json to python dict object. 

    Parameters
    ----------
    url : str
        the url path for data requested.
    key : str
        your api key .

    Returns
    -------
    dict
        DESCRIPTION.

    """
    
    url = url + key 
    
    try:
        
        response = requests.get(url).json()
        
        return response
    
    except urllib.error.HTTPError:
        
        print(f"HTTP Error: {url}")