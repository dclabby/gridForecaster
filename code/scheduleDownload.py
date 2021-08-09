#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 20:40:58 2021

@author: dclabby
"""
from datetime import datetime, date
import time
from collectData import collectEirgridData

targetTime = '00:01'
saveFolder='./data/Eirgrid/Forecasts'
print("Running started at: " + "{:02d}:{:02d}".format(datetime.now().hour, datetime.now().minute))
while True:
    #timeNow = "{:02d}:{:02d}:{:02d}".format(datetime.now().hour, datetime.now().minute, datetime.now().second)
    timeNow = "{:02d}:{:02d}".format(datetime.now().hour, datetime.now().minute)
    if timeNow == targetTime:
                
        today = date.today()
        startTime = datetime(today.year, today.month, today.day, 0,0,0)
        endTime = datetime(today.year, today.month, today.day, 23,59,59)
        
        downloadError = True
        while downloadError:
            try:
                collectEirgridData(startTime, endTime, 'WindGeneration', saveFolder)
                collectEirgridData(startTime, endTime, 'SystemDemand', saveFolder)
                print("...\nAll downloads were successful")
                downloadError = False
                time.sleep(60)
            except:
                waitTime = 5
                print("Error, data was not downloaded. Will retry in " + str(waitTime) + "s")
                downloadError = True
                time.sleep(5)
    elif datetime.now().second == 0 and datetime.now().minute%10 == 0:
        print("Running: " + timeNow)
    time.sleep(1)
