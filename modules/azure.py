#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 19:30:33 2024

@author: theochapman
"""

import os 
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobServiceClient
import os 
import requests
import urllib

def list_blobs_in_container(storage_account:str, container_name:str, name_starts_wtih:str, key:str) -> list:
    """
    Function takes a storage account name, the name of the container and name starts with (add file path) and will
    return a list of file that match the criteria. 

    Parameters
    ----------
    storage_account : str
        sotrage account name i.e. 'crypto-data'.
    container_name : str
        Name of container data is stored in within storage account i.e. 'trades'.
    name_starts_wtih : str
        Full file path of name starts with, i.e. '/kraken/btc-usd/2024/march/' will list all trade files for btc-usd kraken in march 2024.
        can be left blank i.e. ''
    key : str
        your api key.

    Returns
    -------
    blobs: list
        list of blobs in storage account & container combo that start with given name.

    """
    
    container = ContainerClient(
        account_url=f"https://{storage_account}.blob.core.windows.net/",
        container_name = container_name,
        credential = key
        )
    
    list_blobs = []
    
    for blob_name in container.list_blob_names(name_starts_wtih = name_starts_wtih):
        
        list_blobs.append(blob_name)
        
    return list_blobs


def download_blob_json(url:str, key:str)->dict:
    """
    Function downloads .json objects from either api or blob depending on 
    url and key

    Parameters
    ----------
    url : str
        url where data is stored.
    key : str
        your api/sas key to access data.

    Returns
    -------
    blob : dict
        the blob you have requessted if no HTTP eorr is raised.

    """
    url = url + key
    
    try:
        
        blob = requests.get(url).json()
        
        return blob
    
    except urllib.error.HTTPError:
        
        print(f"HTTP ERROR, check url: {url}")
        
        
        
def download_blob_csv(url:str,file:str, key:str, path:str, name:str):
    """
    Function downloads csv file from azure using the file url and sas_key provided. 
    
    Note: As CSV data may not have uniform lenght of columns & rows reading directly into a df 
    is not advised. This function reads data and saves to CSV locally to inspect. 

    Parameters
    ----------
    url : str
        url location of file desired.
    file : str
        The file name 
    key : str
        key associated with storage account.
    path : str
        path to save locally in - must exist.
    name : str
        Name of file to be save. If it need be different than the file name used to download, otherwise just put the same. 

    Returns
    -------
    None.

    """
    
    url = url + file + key
    
    r = requests.get(url)
    
    if "Error" in str(r.content):
        
        print(f"Error reading {file}")
        
    else:
        
        with open(path + name, "wb") as f:
            
            f.write(r.content)
            

def delete_blob(storage_account:str, container:str, blob:str):
    """
    Function deletes blob in container & storage account 

    Parameters
    ----------
    storage_account : str
        storage account name.
    container : str
        container name.
    blob : str
        blob name.

    Returns
    -------
    None.

    """
    
    bsc = BlobServiceClient(account_url = f"https://{storage_account}.blob.core.windows.net/")
    
    cc = bsc.get_container_client(container)
    
    bc = cc.get_blob_client(blob)
    
    bc.delete_blob()
    
    
def upload_blob_to_azure(path:str, name:str, storage_account:str, container:str, key:str):
    """
    function uploads a blob saved locally to azure in the storage account 

    Parameters
    ----------
    path : str
        path of local file.
    name : str
        name of local file.
    storage_account : str
        storage account name.
    container : str
        container name.
    key : str
        .

    Returns
    -------
    None.

    """
    
    bsc = BlobServiceClient(account_url= f"https://{storage_account}.blob.core.windows.net/")
    
    cc = bsc.get_container_client(container)
    
    with open(path + name, "rb") as file:
        
        bc = cc.get_blob_client(blob=os.path.basename(path))
        
        bc.upload_blob(file, overwrite=True)
        
        
def rename_blob(storage_account:str, container:str, current_blob_name:str, new_blob_name:str) -> str:
    """
    For a given blob in a given container & sotrage account renames the blob. 
    
    Returns new blob url should you need. 
    
    WARNING: Deletes old blob!!!!!

    Parameters
    ----------
    storage_account : str
        account name not url, base url is included.
    container : str
        container name.
    current_blob_name : str
        current name of file in blobs. believe this should be full url from container
    new_blob_name : str
        New file name, if same enter old name here.

    Returns
    -------
    url : str
        the new url .

    """
    
    bsc = BlobServiceClient(account_url= f"https://{storage_account}.blob.core.windows.net/")
    
    cc = bsc.get_container_client(container)
    
    bc = cc.get_blob_client(current_blob_name)
    
    new_bc = cc.get_blob_client(new_blob_name)
    
    new_bc.start_copy_from_url(bc.url)
    
    bc.delete_blob()
    
    return new_bc.url

    
        
    
    
    