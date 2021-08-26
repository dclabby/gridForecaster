#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 17:30:02 2021

@author: dclabby
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def getTimeSteps(df, timeSteps=0):
    data = {}
    colNames = []
    if type(timeSteps) == int:
        timeSteps = np.arange(1,np.abs(timeSteps)+1)*np.sign(timeSteps)
    for t in timeSteps:
        colName = 't' + str(t) #print(colName)
        # df.loc[:, colName] = df.loc[:,df.columns[0]].shift(-t) # issues with variable scope, needed to pass df as a copy
        
        data[colName] = list(df.loc[:,df.columns[0]].shift(-t))#np.array(df.loc[:,df.columns[0]].shift(-t))
        colNames.append(colName)
    return pd.DataFrame(data, index=df.index)#, colNames)


def gridFeatureEng(df, featureIndices, labelIndices):#, blockDiffs=False):
    """
    
    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    featureIndices : list or numpy array
        Can be defined as a list of lists, where each element is a numpy array specifying the indices for discontinuous blocks of previous time steps. 
        Alternatively can be defined as a numpy array specifying the index of a single continuous block of previous time steps 
    labelIndices : numpy array
        numpy array specifying the index of a single continuous block of future time steps (to be used as labels)

    Returns
    -------
    x : data frame
        features
    y : data frame
        labels
    
    """
    if type(featureIndices) == list: # multiple blocks
        prev = []
        for block in featureIndices:
            pTmp = getTimeSteps(df, block)
            # if blockDiffs:
            #     pTmp = dataDiff(pTmp) 
            prev.append(pTmp)
    else: # single block specified as a numpy array
        prev = [getTimeSteps(df, featureIndices)]
        # if blockDiffs:
        #     prev = dataDiff(prev) 
    
    if np.shape(prev)[0] == 1:
        x = prev[0]
    else:
        for i in range(0,np.shape(prev)[0]):
            if i == 0:   
                x = prev[0]
            else:
                x = pd.merge(x, prev[i], left_index=True, right_index=True)
    
    if len(labelIndices) > 0:
        y = getTimeSteps(df, labelIndices) 
        identifyNans = ~x.isnull().any(axis=1) & ~y.isnull().any(axis=1)
        x = x[identifyNans]
        y = y[identifyNans]
    else:
        identifyNans = ~x.isnull().any(axis=1) 
        x = x[identifyNans]
        y = []
    
    # prev1 = getTimeSteps(dfSystemGen, np.arange(1,nSteps+1)*-1) # first block of past timesteps to be used as features
    # prev2 = getTimeSteps(dfSystemGen, np.arange(1,nSteps+1)*(-1) - (7*24*4) + nSteps) # second block of past timesteps to be used as features
    # next1 = getTimeSteps(dfSystemGen, nSteps) # multi step 1) # single step # block of future timesteps to be used as features
    
    # differecces between successive timesteps in blocks of past timesteps
    # prev1 = dataDiff(prev1) 
    # prev2 = dataDiff(prev2) 
    
    # construct features (x) and labels (y), and remove NaNs
    # x = pd.merge(prev1, prev2, left_index=True, right_index=True)
    # y = next1
    # identifyNans = ~x.isnull().any(axis=1) & ~y.isnull().any(axis=1)
    # x = x[identifyNans]
    # y = y[identifyNans]
    
    return x, y

def standardizeFeatures(xTrain, xTest):
    sc = StandardScaler()
    xTrain = sc.fit_transform(xTrain)
    xTest = sc.transform(xTest)
    return xTrain, xTest, sc


# def dataDiff(df):
#     """    

#     Parameters
#     ----------
#     df : TYPE
#         DESCRIPTION.

#     Returns
#     -------
#     df : TYPE
#         DESCRIPTION.

#     """
#     dfTmp = df.diff(axis=1) # get differences between columns
#     #dfTmp = df.loc[:, df.columns[1:]].diff(axis=1) # need to exclude the first column since this is the label
    
#     # change column names
#     colNames = {}
#     for c in range(0,len(dfTmp.columns)):
#         colNames[dfTmp.columns[c]] = 'diff(' + str(c+1) + ',' + str(c) + ')'
#     dfTmp.rename(columns=colNames, inplace=True)
#     dfTmp.drop(columns = [dfTmp.columns[0]], inplace=True) # drop the first column
#     #df = df.join(dfTmp)# concatenate with original dataframe
#     return dfTmp