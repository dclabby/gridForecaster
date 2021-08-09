#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 09:46:47 2021

@author: dclabby
"""
from os import listdir
from os.path import sep
import datetime
import pandas as pd

def loadEirgridData(forecastVar, startDate = '', endDate = ''):
    # forecastVar = 'SystemGeneration'
    # startDate = ''#'2014-01-01'
    # endDate = ''#'2021-06-01'
    print('...\nloading ' + forecastVar + ' data...')
    if startDate == '':
        startDate = datetime.date.fromisoformat('2000-01-01')
    else:
        startDate = datetime.date.fromisoformat(startDate)
    
    if endDate == '':
        endDate = datetime.date.today()
    else:
        endDate = datetime.date.fromisoformat(endDate)
    
    pathName = '.' + sep + 'data' + sep + 'Eirgrid' + sep + forecastVar + sep
    files = listdir(pathName)
    files.sort()
    
    firstFile = True
    for file in files:
        splitFileName = file.split('.')[0].split('_')
        fileStart = datetime.date.fromisoformat(splitFileName[1])
        fileEnd = datetime.date.fromisoformat(splitFileName[2])
        if fileStart >= startDate and fileEnd <= endDate:
            #print(file)
            if firstFile:
                df = pd.read_csv(pathName + file)
                firstFile = False
            else:
                df = pd.concat([df, pd.read_csv(pathName + file)])
    print('loading of ' + forecastVar + ' complete!')
    return df

def cleanData(df):
    if any(['WIND' in l for l in df.columns]):
        forecastVar = 'WindGeneration'
    else:
        forecastVar = 'SystemGeneration'
    print('cleaning ' + forecastVar + ' data...')
        
    
    # drop REGION and FORECAST WIND columns
    if forecastVar == 'WindGeneration':
        df.drop(columns = [' REGION', ' FORECAST WIND(MW)'], inplace=True)
    else:
        df.drop(columns = [' REGION'], inplace=True)
    
    # convert DATE & TIME to datetime and set as index
    # print('converting DATE & TIME to datetime...')
    df['DATE & TIME'] = pd.to_datetime(df['DATE & TIME'])
    df.set_index('DATE & TIME', inplace=True)
    
    # rename the data column based on the forecast variable
    df.rename(columns={df.columns[0]: forecastVar}, inplace=True)
    
    # convert to numeric (coerce errors means that non-numeric data will be replaced by NaN)
    df[forecastVar] = pd.to_numeric(df[forecastVar], errors="coerce") 
    
    # remove non-unique indices
    if df.index.has_duplicates:
        df = df[~df.index.duplicated(keep='first')] # df.index.duplicated returns True for each index with a duplicate, ~ inverts it so that only duplicates are False
        
    # set frequency & impute missing values
    df = df.asfreq('15min', method='ffill') # fill based on previous value
    
    # check for null values & forward fill
    if df[forecastVar].isnull().values.any():
        df.fillna(method='ffill', inplace=True)
    
    print('cleaning of ' + forecastVar + ' complete!')
    return df




