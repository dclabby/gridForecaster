#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 18:54:04 2021

@author: dclabby

Implements the following use cases:
    1. Train a Model
    2. Generate a forecast
    3. Compare forecast (to publicly available forecasts) 
    4. Visualize forecasts
"""
import numpy as np
from preProc import loadEirgridData, cleanData
from featureEng import systemGenFeatureEng
from trainModels import trainModels, testModels
from collectData import collectEirgridData
from datetime import datetime, date, timedelta

print("Welcome to GridForecaster 1.0, an application for generating forecasts for Ireland's electricity Grid using Machine Learning. GridForecaster was developed by Darragh Clabby.")

tmp = input("What type of data do you want to forecast? Enter:\n   1 for Total System Power Generation (Default)  \n   2 for Total Power Demand \n   3 for Total Wind Power Generation \n")
if tmp == '1':
    forecastVar = 'SystemGeneration'
elif tmp == '2':
    forecastVar = 'SystemDemand'
elif tmp == '3':
    forecastVar = 'WindGeneration'
else:
    forecastVar = 'SystemGeneration'
    print('Invalid input received, default of SystemGeneration will be used as forecast variable\n')
# forecastVar = 'SystemGeneration'

try:
    print('Attempting to load data from local file system...')
    gridData = loadEirgridData(forecastVar) # try to load data from previously downloaded files
    #TODO: metData = loadMetData(forecastVar)
    print('Data loaded successfully!')
except: # if files do not exist the data will need to be downloaded from the eirgrid dashboard
    print('Data not found on local file system. Downloading data from source...')
    collectEirgridData(datetime(2014,1,1), datetime(2021,6,30), forecastVar, saveFolder='data/Eirgrid')
    gridData = loadEirgridData(forecastVar)
    #TODO: collectMetData(datetime(2014,1,1), datetime(2021,6,30), forecastVar, saveFolder='data/MetEireann')
    #TODO: metData = loadMetData(forecastVar)
    
# Clean data
gridData = cleanData(gridData)

# Feature engineering
dt = 4 # time resolution of features & labels... can still train at 15 min resolution, but x & y can use coarser resolution
nSteps = 24*dt
prevSteps = [np.arange(1,nSteps+1,dt)*-1, np.arange(1,nSteps+1,dt)*(-1) - (7*24*4) + nSteps]
nextSteps = np.arange(0,nSteps,dt)
x, y = systemGenFeatureEng(gridData, prevSteps, nextSteps)

# Split features & labels into test & train sets
splitYear = '2019'
xTrain = x[:splitYear] # 2014 to 2019. Verify: (6*365 + 1)*24*4 = 210336 rows - (no. prev tie steps)
yTrain = y[:splitYear]
xTest = x[str(int(splitYear)+1)] # 2020. Verify: (365 + 1)*24*4 = 35136 rows (note some 2021 data so future data for 2020-12-31 23:45 is available)
yTest = y[str(int(splitYear)+1)]

# Train/Tune models
modelsToTrain = {'LR': {}, 'KNN':{}, 'RF':{'n_estimators': 10}} # train all models with default parameters, except RF
# modelsToTrain = {'LR': {}, 'KNN':{'n_neighbors': 4}, 'RF':{'n_estimators': 10}} # specify some parameters
# modelsToTrain = {
#     'LR': {}, 
#     'RF': {'n_estimators': [20, 50, 100], 'max_features': ['auto', 'sqrt', 'log2'], 'max_depth' : [i for i in range(5,15)]}, 
#     'KNN':{'n_neighbors': [2,5,8], 'weights': ['uniform', 'distance']} 
#     } # specify parameters to tune
models = trainModels(xTrain, yTrain, modelsToTrain)
yPred = testModels(xTest, yTest, models)

# Visualize test results
#TODO
import matplotlib.pyplot as plt
startDate = datetime(2020,3,20)
iPlot = np.where(yTest.index == startDate.strftime("%Y-%m-%d %H:%M:%S"))[0].astype(int)[0]
timeVec = [(startDate + timedelta(minutes=int(n*15))).strftime("%H:%M") for n in nextSteps]
plt.figure(iPlot,figsize = (16,4))
# plt.plot(np.array(yTest)[iPlot,:])
plt.plot(timeVec, yTest.loc[startDate])
for modelkey in yPred:
    plt.plot(timeVec, yPred[modelkey][iPlot, :], linestyle='--')
plt.title(startDate.strftime('%d-%b-%Y'))
plt.ylabel('System Generation [MW]')
plt.legend(['test'] + [k for k in yPred.keys()])
plt.ylim((0, 7000))


# Save models
#TODO

# Generate a forecast
endTime = date.today()
startTime = endTime + timedelta(days=-7)
forecastData = collectEirgridData(startTime, endTime, forecastVar)
forecastData = cleanData(forecastData)
x, y = systemGenFeatureEng(forecastData, prevSteps, []) # note: labels are not necessary here, so nextSteps should not be included




# # Feature engineering
# timeSteps = 4#[1,2,3,4]
# gridData = prevTimeSteps(gridData, timeSteps)
# gridData = dataDiff(gridData)
# gridData.dropna(inplace=True)

# # Split data into features/labels, and test/train
# splitYear = '2019'
# xTrain = gridData[:splitYear].drop([forecastVar], axis=1) # 2014 to 2019 - verify (6*365 + 1)*24*4 = 210336 rows - (no. time steps for difference, will produce NaNs)
# yTrain = gridData.loc[:splitYear, forecastVar]
# xTest = gridData[str(int(splitYear)+1)].drop([forecastVar], axis=1) # 2020 - verify (365 + 1)*24*4 = 35136 rows
# yTest = gridData.loc[str(int(splitYear)+1), forecastVar]



# # test the pre processing
# gridData = loadData('SystemGeneration')
# dfWindGen = loadData('WindGeneration')

# gridData = cleanData(gridData)
# dfWindGen = cleanData(dfWindGen)
# # verify no. rows from 01/01/2014 to 30/06/2021 = (365*7 + 2 (leap years) + 31+28+31+30+31+30 (J,F,M,A,M,J) ) (24 hours x 4 per hour) = 262848

# # test feature engineering
# timeSteps = 4#[1,2,3,4]

# gridData = prevTimeSteps(gridData, timeSteps)
# gridData = dataDiff(gridData)
# gridData.dropna(inplace=True)

# dfWindGen = prevTimeSteps(dfWindGen, timeSteps)
# dfWindGen = dataDiff(dfWindGen)
# dfWindGen.dropna(inplace=True)


# import matplotlib.pyplot as plt
# data = gridData
# data_columns = 'SystemGeneration'
# data_365d_rol = data[data_columns].rolling(window = 365, center = True).mean()
# data_7d_rol = data[data_columns].rolling(window = 7, center = True).mean()
# fig, ax = plt.subplots(figsize = (11,4))# plotting daily data
# ax.plot(data[data_columns], marker='.', markersize=2,
# color='0.6',linestyle='None', label='Daily')# plotting 7-day rolling data
# ax.plot(data_7d_rol, linewidth=2, label='7-d Rolling Mean')# plotting annual rolling data
# ax.plot(data_365d_rol, color='0.2', linewidth=3, label='Trend (365-d Rolling Mean)')# Beautification of plot
# # ax.xaxis.set_major_locator(mdates.YearLocator())
# ax.legend()
# ax.set_xlabel('Year')
# ax.set_ylabel('Consumption (GWh)')
# ax.set_title('Trends in Electricity Consumption')



