#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 09:30:25 2021

@author: dclabby
"""
import numpy as np

def intTestPreds(yTest, yPred, gridData):
    intConsts = np.array(gridData.loc[yTest.index])
    intMat = np.matmul(intConsts, np.ones((1,np.shape(yTest)[1])))
    yTestInt = np.cumsum(yTest, axis=1) + intMat
    yPredInt = {}
    for model in yPred.keys():
        yPredInt[model] = np.cumsum(yPred[model], axis=1)  + intMat
    return (yTestInt, yPredInt)


def intForecast(yForecast, gridData):
    intConsts = np.array(gridData)
    intMat = np.matmul(intConsts, np.ones((1,np.shape(yForecast)[1])))
    yForecastInt = np.cumsum(yForecast, axis=1)  + intMat
    return yForecastInt

