#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 20:19:06 2023

This short script splits any given excel file into seperate CSV sheets  

@author: theochapman
"""

import pandas as pd


excel_file_path = '/Users/theochapman/Documents/nutrition_data/McCance_Widdowsons_Composition_of_Foods_Integrated_Dataset_2021..xlsx'


excel_file = pd.ExcelFile(excel_file_path)


sheet_names = excel_file.sheet_names


for sheet_name in sheet_names:
    # Read the sheet
    df = excel_file.parse(sheet_name)
    
    df.drop([0,1],axis=0,inplace=True)

    csv_file_path = f"/Users/theochapman/Documents/nutrition_data/{sheet_name}.csv"

    df.to_csv(csv_file_path, index=False)

    print(f'Saved {sheet_name} as {csv_file_path}')
