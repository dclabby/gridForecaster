#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 20:40:58 2021

@author: dclabby
"""
from datetime import datetime, date
import time
from collectData import collectEirgridData, getMetForecast

targetTime = '00:01'
saveFolder='./data/Eirgrid/Forecasts'
print("Running started at: " + "{:02d}:{:02d}".format(datetime.now().hour, datetime.now().minute))
waitTime = 5
while True:
    #timeNow = "{:02d}:{:02d}:{:02d}".format(datetime.now().hour, datetime.now().minute, datetime.now().second)
    timeNow = "{:02d}:{:02d}".format(datetime.now().hour, datetime.now().minute)
    if timeNow == targetTime:
                
        today = date.today()
        startTime = datetime(today.year, today.month, today.day)#, 0,0,0)
        endTime = datetime(today.year, today.month, today.day+1)#, 23,59,59)
        
        gridError = True
        metError = True
        while gridError or metError:
            try:
                if gridError:
                    collectEirgridData(startTime, endTime, 'WindGeneration', saveFolder)
                    collectEirgridData(startTime, endTime, 'SystemDemand', saveFolder)
                    print("...\nGrid forecast data downloaded successfully!")
                    gridError = False
                    
                if metError:
                    getMetForecast() # no arguments - full forecast will be downloaded for Dublin airport & Valentia observatory
                    print("...\nWeather forecast data downloaded successfully!")
                    metError = False
                    
                time.sleep(60)
            except:                
                if gridError:
                    print("Error, grid forecast data was not downloaded. Will retry in " + str(waitTime) + "s")
                
                if metError:
                    print("Error, weather forecast  data was not downloaded. Will retry in " + str(waitTime) + "s")
                    
                time.sleep(waitTime)
                
    elif datetime.now().second == 0 and datetime.now().minute%10 == 0:
        print("Running: " + timeNow)
    time.sleep(waitTime)
