#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 10 16:00:14 2021

@author: dclabby
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta #datetime, date, 
from preProc import integrateData

def plotTestPred(yTest, yPred, startDate, gridData=[], intData=False):
    #startDate = datetime(2020,6,20) 
    iPlot = np.where(yTest.index == startDate.strftime("%Y-%m-%d %H:%M:%S"))[0].astype(int)[0]
    
    featureResolution = int(3600/yTest.index.freq.delta.seconds)
    timeVec = [int(t.strip('t'))*(int(60/featureResolution)) for t in yTest.columns]
    timeVec = [startDate + timedelta(minutes=t) for t in timeVec]
    timeHrsMins = [t.strftime('%H:%M') for t in timeVec]
    
    plt.figure(iPlot,figsize = (16,4))
    legStr = ['test']
    if intData: # data input as differences and must be integrated
        if len(gridData) > 0:
            bias = gridData.loc[startDate][0]
        else:
            bias=0
        
        plt.plot(timeHrsMins, integrateData(yTest.loc[startDate], bias))
        if len(gridData)> 0:
            plt.plot(timeHrsMins, gridData.loc[timeVec].values, linestyle='dotted', color='r')
            legStr = ['integrated test data', 'original test data']
        for modelkey in yPred:
            # plt.plot(timeVec, yPred[modelkey][iPlot, :], linestyle='--')
            plt.plot(timeHrsMins, integrateData(yPred[modelkey][iPlot, :], bias), linestyle='--')
        plt.title(startDate.strftime('%d-%b-%Y'))
        plt.ylabel('Power [MW]')
        plt.legend(legStr + [k for k in yPred.keys()])
    else: # data has already been integrated
        plt.plot(timeHrsMins, yTest.loc[startDate])
        if len(gridData)> 0:
            plt.plot(timeHrsMins, gridData.loc[timeVec].values, linestyle='dotted', color='r')
            legStr = ['integrated test data', 'original test data']
        for modelkey in yPred:
            # plt.plot(timeVec, yPred[modelkey][iPlot, :], linestyle='--')
            plt.plot(timeHrsMins, yPred[modelkey][iPlot, :], linestyle='--')
        plt.title(startDate.strftime('%d-%b-%Y'))
        plt.ylabel('Power [MW]')
        plt.legend(legStr + [k for k in yPred.keys()])

def plotForecast(timeVec, forecastResults):
    timeHrsMins = [t.strftime('%H:%M') for t in timeVec]
    plt.figure(1, figsize = (16,4))
    legStr = []
    for modelkey in forecastResults:
        plt.plot(timeHrsMins, forecastResults[modelkey], linestyle='--')
        legStr.append(modelkey)
        plt.title("Forecast from " + timeVec[0].strftime('%d-%b-%Y'))
        plt.ylabel('Power [MW]')
        plt.legend(legStr)
    

