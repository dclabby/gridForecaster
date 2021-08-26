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
import numpy as np
import xml.etree.ElementTree as et


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


def cleanGridData(df):
    if any(['WIND' in l for l in df.columns]):
        forecastVar = 'WindGeneration'
    elif any(['DEMAND' in l for l in df.columns]):
        forecastVar = 'SystemDemand'        
    else:
        forecastVar = 'SystemGeneration'
    print('...\ncleaning ' + forecastVar + ' data...')
        
    
    # drop REGION and FORECAST WIND columns
    if forecastVar == 'WindGeneration':
        df.drop(columns = [' REGION', ' FORECAST WIND(MW)'], inplace=True)
    elif forecastVar == 'SystemDemand':
        df.drop(columns = [' REGION', ' FORECAST DEMAND(MW)'], inplace=True)
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


def cleanMetData(df, startTime='', endTime='', freqStr='H'):
    # discard all rows outside the range specified by startTime and endTime
    if startTime != '' and endTime != '':
        df = df[startTime:endTime]
    elif startTime == '':
        df = df[:endTime]
    else:
        df = df[startTime:]
    
    # convert to numeric (coerce errors means that non-numeric data will be replaced by NaN)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")         
    
    # remove non-unique indices
    if df.index.has_duplicates:
        df = df[~df.index.duplicated(keep='first')] # df.index.duplicated returns True for each index with a duplicate, ~ inverts it so that only duplicates are False
        
    # set frequency & impute missing values
    df = df.asfreq('H', method='ffill') # fill based on previous value
    
    # check for null values & forward fill
    if df.isnull().values.any():
        df.fillna(method='ffill', inplace=True)
    
    return df


def readMetForecast(xmlFile, startTime='', endTime=''):
    tree = et.parse(xmlFile)
    root = tree.getroot()
    
    columns = ['time', 'temperature', 'windSpeed']#, 'globalRadiation']
    
    xmlData = []
    for timeTag in root.findall('product/time'):
        rowTmp = []
        if timeTag.attrib['from'] == timeTag.attrib['to']:
            rowTmp.append(timeTag.attrib['from'].replace('T', ' ').replace('Z', ''))
            
            for l in timeTag.find('location'): # iterates through children of location tag
                for col in columns[1:]:
                    if l.tag == col:
                        try:
                            rowTmp.append(float(l.attrib['value']))
                        except:
                            rowTmp.append(float(l.attrib['mps']))
            xmlData.append(rowTmp)
    
    df = pd.DataFrame(xmlData, columns=columns)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df = cleanMetData(df, startTime, endTime)
    
    return df


def readMetHistorical(filename, startTime='', endTime='', cols=[]):
    df = pd.read_csv(filename, header=20, low_memory=False)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    #discard all columns other than those specified in cols (e.g. cols = ['temp', 'wdsp']; or cols = [] to discard none)
    if len(cols) > 0:
        df = df.loc[:, cols]
    
    df = cleanMetData(df, startTime, endTime)
    
    return df


def detrendData(df, featureResolution=1):
    dfDtr = df.diff(periods=featureResolution).dropna()
    return dfDtr


def integrateData(diffs, intConst, dt=1):
    return np.cumsum(diffs)*dt + intConst