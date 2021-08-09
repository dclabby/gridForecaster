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
        loopCounter += 1
    return df
    

def collectMetData():
    #TODO
    return None