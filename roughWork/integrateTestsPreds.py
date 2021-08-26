#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 20:42:12 2021

@author: dclabby
"""

import matplotlib.pyplot as plt
from postProc import intTestPreds, intForecast
from datetime import datetime

yTestInt, yPredInt = intTestPreds(yTest, yPred, gridData)

startDate = datetime(2021,1,15)
iPlot = np.where(yTest.index == startDate.strftime("%Y-%m-%d %H:%M:%S"))[0].astype(int)[0]

fig, ax = plt.subplots(figsize = (11,4))
ax.plot(np.array(gridData.loc[startDate + timedelta(hours=1): startDate+ timedelta(hours=24):4]))
ax.plot(np.array(yTestInt.loc[startDate]), linestyle='none', marker='.')
ax.legend(['Original', 'Integrated'])
ax.set_title(forecastVar + '; ' + startDate.strftime("%Y-%m-%d"))
ax.set_xlabel('time [hours]')
ax.set_ylabel('Power [MW]')


#***** Integrate test data and predicted data
intConsts = np.array(gridData.loc[yTest.index])
intMat = np.matmul(intConsts, np.ones((1,np.shape(yTest)[1])))

yTestInt = np.cumsum(yTest, axis=1) + intMat

import matplotlib.pyplot as plt
plt.figure()
plotDate = datetime(2020,6,11)
plt.plot(np.array(gridData[plotDate+ timedelta(hours=1):plotDate + timedelta(hours=24):4]))
plt.plot(np.array(yTestInt.loc[plotDate]), linestyle='none', marker='.')

yPredInt = {}
iPlot = np.where(yTest.index == plotDate.strftime("%Y-%m-%d %H:%M:%S"))[0].astype(int)[0]
for model in modelsToTrain:
    yPredInt[model] = np.cumsum(yPred[model], axis=1)  + intMat
    plt.plot(yPredInt[model][iPlot], linestyle='dotted')

    regression_results(yTestInt, yPredInt[model])
    regression_results(yTest, yPred[model])

#*****

