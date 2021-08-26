#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 14:59:40 2021

@author: dclabby
"""

import pickle
import matplotlib.pyplot as plt
import numpy as np

import os
root = '/home/dclabby/Documents/Springboard/HDAIML_SEP/Semester03/Project/app/code'
os.chdir(root)

def barPlot(data, seriesName, xticklabels, seriesLabels):
        
    # x = np.arange(len(seriesLabels))  # the label locations
    x = np.arange(len(data[0]))  # the label locations
    width = 0.3  # the width of the bars

    fig, ax = plt.subplots(figsize = (11,4))
    series1 = ax.bar(x - width/4, data[0], width/2, label=seriesName[0])
    # rects2 = ax.bar(x , rec, width/3, label='Recall')
    series2 = ax.bar(x + width/4, data[1], width/2, label=seriesName[1])
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(seriesName)
    #ax.set_title('Presion, Recall, & F score')
    ax.set_xticks(x)
    ax.set_xticklabels(xticklabels)
    ax.legend(seriesLabels, loc='best')
    ax.set_title(seriesName + ' evaluated over the test data set (01 Jan 2020 to 29 June 2021)')
    
    fig.tight_layout()
    plt.show()
    #plt.ylim((0.9, 1))

forecastVars = ['SystemDemand', 'WindGeneration']
metrics = {}
rSquared = []
expVar = []
MAE = []
MSE = []
RMSE = []
for forecastVar in forecastVars:
    modelFile = 'models/' + forecastVar + 'Models.dat'
    with open(modelFile, "rb") as f:
        #xTrain, yTrain, xTest, yTest, yTestInt, yPred, yPredInt, testMetrics, testMetricsInt, sc, models = pickle.load(f)
        _, _, _, _, _, _, _, _, testMetricsInt, _, _ = pickle.load(f)
    metrics[forecastVar] = testMetricsInt
    rSquared.append([testMetricsInt[k][0] for k in testMetricsInt.keys()] )
    expVar.append([testMetricsInt[k][1] for k in testMetricsInt.keys()] )
    MAE.append([testMetricsInt[k][2] for k in testMetricsInt.keys()] )
    MSE.append([testMetricsInt[k][3] for k in testMetricsInt.keys()] )
    RMSE.append([testMetricsInt[k][4] for k in testMetricsInt.keys()] )

barPlot(rSquared, 'R squared', testMetricsInt.keys(), forecastVars)
barPlot(expVar, 'Explained Variance', testMetricsInt.keys(), forecastVars)
barPlot(MAE, 'Mean Absolute Error [MW]', testMetricsInt.keys(), forecastVars)
barPlot(MSE, 'Mean Squares Error [MW^2]', testMetricsInt.keys(), forecastVars)
barPlot(RMSE, 'Root Mean Squares Error [MW]', testMetricsInt.keys(), forecastVars)
