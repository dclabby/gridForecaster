#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 20:04:35 2021

@author: dclabby
"""

import datetime
import time
import requests
from os.path import join, isdir
from os import makedirs
import pandas as pd
import io
import zipfile

def collectEirgridData(startTime, endTime, tableName, saveFolder=''):
    """
    
    Parameters
    ----------
    startTime : datetime object
        DESCRIPTION.
    endTime : datetime object
        DESCRIPTION.
    tableName : string
        DESCRIPTION.
    saveFolder : string, optional
        DESCRIPTION. The default is './dataTest/Eirgrid'. In this case the data will be saved as csv files and the function will return None. 
        If set to an empty string then the data will be loaded to a dataframe which will be returned by the function

    Returns
    -------
    df : None or dataframe
        DESCRIPTION.

    """
    
    # saveFolder='./dataTest/Eirgrid'
    blockSize = 30
    maxLoops = 100
    linkStr = "http://smartgriddashboard.eirgrid.com/DashboardService.svc/csv?area=<tableID>&region=ALL&datefrom=<blockStart>%2000:00&dateto=<blockEnd>%2023:59"
    # linkStr = "NOT A LINK<tableID>&region=ALL&datefrom=<blockStart>%2000:00&dateto=<blockEnd>%2023:59"
    
    # savePath = "/home/dclabby/Documents/DataScience/Data Sets/EirgridDashboardAnalysis/" + tableName + "/"
    savePath = join(saveFolder, tableName)
    
    blockStart = startTime
    blockEnd = blockStart + datetime.timedelta(blockSize-1)
    loopCounter = 0
    
    if tableName == "WindGeneration":
        tableID = "windActual"
    elif tableName == "SystemDemand":
        tableID = "demandActual"
    elif tableName == "SystemGeneration":
        tableID = "generationActual"
    
    while (blockEnd.toordinal() < endTime.toordinal() + blockSize) and (loopCounter < maxLoops): 
        try:
            if blockEnd.toordinal() > endTime.toordinal():
                url = linkStr.replace("<blockStart>", blockStart.strftime("%d-%b-%Y")).replace("<blockEnd>", endTime.strftime("%d-%b-%Y")).replace("<tableID>", tableID)
                filename = tableName + "_" + blockStart.strftime("%Y-%m-%d") + "_" + endTime.strftime("%Y-%m-%d") + ".csv"
            else:
                url = linkStr.replace("<blockStart>", blockStart.strftime("%d-%b-%Y")).replace("<blockEnd>", blockEnd.strftime("%d-%b-%Y")).replace("<tableID>", tableID)
                filename = tableName + "_" + blockStart.strftime("%Y-%m-%d") + "_" + blockEnd.strftime("%Y-%m-%d") + ".csv"
            print("...")
            print("Downloading " + filename)
            
            t1 = time.time()   
            r = requests.get(url, allow_redirects=True)    
            if len(saveFolder) > 0: 
                if not isdir(savePath):
                    if savePath[0] == '/':
                        makedirs(savePath[1:])
                    else:
                        makedirs(savePath)
                open(join(savePath, filename), "wb").write(r.content)
                print("Download completed & file written in " + "{:.2f}".format(time.time() - t1) + "s")
                df = None
            else:
                print("Download completed in " + "{:.2f}".format(time.time() - t1) + "s")
                if loopCounter == 0:
                    df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
                else:
                    df = pd.concat([df, pd.read_csv(io.StringIO(r.content.decode('utf-8')))])
            
            blockStart = blockEnd + datetime.timedelta(1)
            blockEnd = blockStart + datetime.timedelta(blockSize-1)
        except:
            print('Connection to Eirgrid Dashboard was not successful. Will retry in 10s, and make a maximum of ' + str(maxLoops - loopCounter - 1) + ' more attempts')
            time.sleep(10)
            df = None
        loopCounter += 1
    return df
    
def collectMetData(stationID=[]):
    if len(stationID) == 0:
        stationID = {'Dublin Airport': ['532', [53.428 ,-6.241]], 'Valentia Observatory': ['2275', [51.938, -10.241]]}
    for station in stationID:
        print('...\nDownloading historical weather data for ' + station + ' (station ID: ' +  stationID[station][0] + ')')
        url = 'https://cli.fusio.net/cli/climate_data/webdata/hly' + stationID[station][0] + '.zip'
        r = requests.get(url, allow_redirects=True)
        savePath = 'data/MetEireann/Historical'
        zipTmp = 'hly' + stationID[station][0] + '.zip' #station + '.zip'
        open(join(savePath, zipTmp), "wb").write(r.content)
        # unzip csv
        with zipfile.ZipFile(join(savePath, zipTmp),"r") as zip_ref:
            zip_ref.extract('hly' + stationID[station][0] + '.csv', savePath)
    return None

def getMetForecast(startTime='', endTime='', stationID=[]):
    if len(stationID) == 0:
        stationID = {'Dublin Airport': ['532', [53.428 ,-6.241]], 'Valentia Observatory': ['2275', [51.938, -10.241]]}
        
    if startTime == '':
        startStr = ''
    else:
        startStr = startTime.strftime(';from=%Y-%m-%dT%H:%M')
    
    if endTime == '':
        endStr = ''
    else:
        endStr = endTime.strftime(';to=%Y-%m-%dT%H:%M')
    
    for station in stationID:
        print('...\nDownloading weather forecast data for ' + station + ' (station ID: ' +  stationID[station][0] + ')')
        coords = stationID[station][1]
        url='http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast?lat=<LAT>;long=<LNG>'.replace('<LAT>', str(coords[0])).replace('<LNG>', str(coords[1]))
        url =  url + startStr + endStr
        r = requests.get(url, allow_redirects=True)    
        savePath = 'data/MetEireann/Forecast'
        filename = station.replace(' ', '') + '_' + datetime.date.today().strftime('%Y-%m-%d') + '.xml'
        if not isdir(savePath):
            makedirs(savePath)
        open(join(savePath, filename), "wb").write(r.content)
    #TODO - convert xml to csv
    return None

