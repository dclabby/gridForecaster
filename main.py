#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 18:54:04 2021

@author: dclabby

"""
import numpy as np
from datetime import datetime, timedelta #, date
import pickle

from preProc import loadEirgridData, cleanGridData, detrendData, readMetHistorical
from featureEng import gridFeatureEng, standardizeFeatures
from trainModels import trainModels, testModels, regression_results
from collectData import collectEirgridData
from visualizeData import plotTestPred, plotForecast
from postProc import intTestPreds, intForecast

# Inputs:
forecastVar = 'SystemDemand' #'WindGeneration' #        'SystemGeneration' #
modelsToTrain = {'LR':{}}
# modelsToTrain = {'LR':{},
#                   'NN':{'tol':25, 'verbose':True, }, 
#                   'KN':{'n_neighbors': 4}, 
#                   'RF':{'n_estimators': 10}}
# modelsToTrain = {'LR':{},
#                  'NN':{'hidden_layer_sizes':[(100), (100, 100), (100, 100, 100)], 'tol':[25], 'verbose':[True]},
#                  'KN':{'n_neighbors': [4,8]},
#                  'RF':{'n_estimators': [10,20]}}
saveFeaturesLabels = False
saveModels = False
testDatePlot = datetime(2021,2,23) 
generateForecast = False

# Load/Download Grid data
try:
    print('Attempting to load grid data from local file system...')
    gridData = loadEirgridData(forecastVar) # try to load data from previously downloaded files
    print('Grid data loaded successfully!')
except: # if files do not exist the data will need to be downloaded from the eirgrid dashboard
    print('Grid data not found on local file system. Downloading data from source...')
    collectEirgridData(datetime(2014,1,1), datetime(2021,6,30), forecastVar, saveFolder='data/Eirgrid')
    gridData = loadEirgridData(forecastVar)

# Clean Grid data
samplesPerHour = 4
featureResolution = 4 # time resolution of features & labels... can still train at 15 min resolution, but x & y can use coarser resolution
gridData = cleanGridData(gridData)
gridDataDtr = detrendData(gridData, featureResolution)

# load & clean meteorological data
if forecastVar == '':#'WindGeneration' or forecastVar == 'SystemGeneration':
    includeMet = True
    metFile = 'data/MetEireann/Historical/hly532.csv' # wind data taken from Dublin Airport
    # metFile = 'data/MetEireann/Historical/hly2275.csv' # wind data taken from Valentia Observatory
    metData = readMetHistorical(metFile, gridData.index[0], gridData.index[-1], cols=['wdsp'])
    # metData = metData.apply(lambda x: x**3) # wind power roughly proportional to cube of wind speed
    metDataDtr = detrendData(metData)# featureResolution not specified, defaults to one - ok for met data since it is at hourly resolution
    metDataDtr = metDataDtr.asfreq('15min', method='ffill') # convert to 15 min so that its on same resolution with grid data (need to do this after detrending, otherwise interpolated values will result in 0 difference)
else:
    includeMet = False

# Feature engineering
nSteps = 24*samplesPerHour
if forecastVar == '':#'WindGeneration':
    featureIndices = np.arange(featureResolution,nSteps+featureResolution,featureResolution)*-1 # don't include previous week's wind generation
else:
    featureIndices = [np.arange(featureResolution,nSteps+featureResolution,featureResolution)*-1, 
                      np.arange(featureResolution,nSteps+featureResolution,featureResolution)*(-1) - (7*24*samplesPerHour) + nSteps]

labelIndices = np.arange(featureResolution,nSteps+featureResolution,featureResolution)
x, y = gridFeatureEng(gridDataDtr, featureIndices, labelIndices)

if includeMet:
    xTmp, _ = gridFeatureEng(metDataDtr, labelIndices, []) # use labelIndices here since we want to use wind forecast in features
    x = x.join(xTmp, how='left')

# Split features & labels into test & train sets
splitYear = '2019'
xTrain = x[:splitYear] # 2014 to 2019. Verify: (6*365 + 1)*24*4 = 210336 rows - (no. prev tie steps)
yTrain = y[:splitYear]
xTest = x[str(int(splitYear)+1):] # 2020. Verify: (365 + 1)*24*4 = 35136 rows (note some 2021 data so future data for 2020-12-31 23:45 is available)
yTest = y[str(int(splitYear)+1):]

xTrain, xTest, sc = standardizeFeatures(xTrain, xTest)

if saveFeaturesLabels:
    featuresLabelsFile = 'data/featsLabs/' + forecastVar + 'FeatsLabs.dat'
    with open(featuresLabelsFile, "wb") as f:
        pickle.dump((xTrain, yTrain, xTest, yTest, sc), f)

# Train/Tune models
models = trainModels(xTrain, yTrain, modelsToTrain)

# Test models
yPred, testMetrics = testModels(xTest, yTest, models)
yTestInt, yPredInt = intTestPreds(yTest, yPred, gridData)
testMetricsInt = {}
print("...\nTest metrics on integrated data")
for model in yPredInt.keys():
    testMetricsInt[model] = regression_results(yTestInt, yPredInt[model])

# Visualize test results
plotTestPred(yTestInt, yPredInt, testDatePlot)#, gridData)

# Save models
if saveModels:
    modelFile = 'models/' + forecastVar + 'Models.dat'
    with open(modelFile, "wb") as f:
        pickle.dump((xTrain, yTrain, xTest, yTest, yTestInt, yPred, yPredInt, testMetrics, testMetricsInt, sc, models), f)

# Generate a forecast
if generateForecast:
    #endTime = datetime(2021,8,15,15)
    endTime = datetime.now().replace(second=0, microsecond=0, minute=15*(datetime.now().minute//15))
    startTime = endTime + timedelta(days=-7)
    forecastData = collectEirgridData(startTime, endTime, forecastVar)
    forecastData = cleanGridData(forecastData)
    forecastDataDtr = detrendData(forecastData, featureResolution)
    
    xForecast, _ = gridFeatureEng(forecastDataDtr, featureIndices, []) # note: labels are not necessary here, so labelIndices should not be included
    iForecast = np.where(xForecast.index == endTime.strftime("%Y-%m-%d %H:%M:%S"))[0].astype(int)[0]
    xForecast = sc.transform(xForecast)
    forecastResults = {}
    for key, value in models.items():
        print('\nGenerating forecast using ' + key + ' model...')
        yForecast = value.predict([xForecast[iForecast, :]])
        yForecast = intForecast(yForecast, forecastData.loc[endTime])
        forecastResults[key] = yForecast[0]
    timeVec = [endTime + timedelta(minutes = int(n*(samplesPerHour*60/featureResolution))) for n in range(1,np.shape(yForecast)[1]+1)]
    plotForecast(timeVec, forecastResults)


loadModel = False
if loadModel:
    modelFile = 'models/' + forecastVar + 'Models.dat'
    with open(modelFile, "rb") as f:
        xTrain, yTrain, xTest, yTest, yTestInt, yPred, yPredInt, testMetrics, testMetricsInt, sc, models = pickle.load(f)

saveGridData = False
if saveGridData:
    gridFile = 'data/featsLabs/' + forecastVar + 'GridData.dat'
    with open(gridFile, "wb") as f:
        pickle.dump((gridData, gridDataDtr), f)