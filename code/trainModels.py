#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 19:53:10 2021

@author: dclabby
"""

import numpy as np
import sklearn.metrics as metrics
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit


def tuneModel(xTrain, yTrain, model, modelParams, cvSplit):
    # model = RandomForestRegressor()
    # modelParams = {
    # 'n_estimators': [20, 50, 100],
    # 'max_features': ['auto', 'sqrt', 'log2'],
    # 'max_depth' : [i for i in range(5,15)]}
    # cvSplit = 5
    
    tscv = TimeSeriesSplit(n_splits=cvSplit)
    gsearch = GridSearchCV(estimator=model, cv=tscv, param_grid=modelParams, scoring = 'r2', verbose=1) # https://scikit-learn.org/stable/modules/model_evaluation.html#the-scoring-parameter-defining-model-evaluation-rules
    gsearch.fit(xTrain, yTrain)
    # best_score = gsearch.best_score_
    best_model = gsearch.best_estimator_
    return best_model

def regression_results(y_true, y_pred):
    # Regression metrics
    r2=metrics.r2_score(y_true, y_pred)
    explained_variance=metrics.explained_variance_score(y_true, y_pred)
    mean_absolute_error=metrics.mean_absolute_error(y_true, y_pred)
    mse=metrics.mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    #mean_squared_log_error=metrics.mean_squared_log_error(y_true, y_pred)
    #median_absolute_error=metrics.median_absolute_error(y_true, y_pred)
    print('r2: ', round(r2,4))
    print('explained_variance: ', round(explained_variance,4))
    #print('mean_squared_log_error: ', round(mean_squared_log_error,4))
    print('MAE: ', round(mean_absolute_error,4))
    print('MSE: ', round(mse,4))
    print('RMSE: ', round(rmse,4))
    return [r2, explained_variance, mean_absolute_error, mse, rmse]

def trainModels(xTrain, yTrain, modelsToTrain, cvSplit=5):        
    models = {}
    for modelName, modelParams in modelsToTrain.items():
        print('\nTraining ' + modelName + '...')
        if modelName == 'RF':
            model = RandomForestRegressor()
        elif modelName == 'KN':
            model = KNeighborsRegressor()
        elif modelName == 'NN':
            model = MLPRegressor()
        elif modelName == 'SV':
            model = SVR()
        else:# modelName == 'LR':
            model = LinearRegression()
        
        if len(modelParams) == 0: # no parameters specified so the models are trained based on default parameters
            model.fit(xTrain, yTrain)
        elif any([type(v)==list for v in modelParams.values()]): # if any of the parameters are passed as a list then it implies that multiple parameters have been defined and tuning is required
            model = tuneModel(xTrain, yTrain, model, modelParams, cvSplit)
        else: # in this case parameters have been defined, with single values given for each parameter, so no need for tuning, just need to set the attributes
            model.set_params(**modelParams)
            model.fit(xTrain, yTrain)
        models[modelName] = model
        print('Training of ' + modelName + ' complete!')
    
    return models

def testModels(xTest, yTest, models):
    testPreds = {}
    testMetrics = {}
    for key, value in models.items():
        print('\nTesting ' + key + ':')
        yPred = value.predict(xTest)
        
        testPreds[key] = yPred
        testMetrics[key] = regression_results(yTest, yPred)
    return (testPreds, testMetrics)

# def multiRecurs(xHistorical, timeSteps, nPred, models):
#     y = {}
#     x = {}
    
#     if type(timeSteps) == int:
#         timeSteps = np.arange(0,timeSteps) # note that this is zero indexed since the first time step is not the label (as is the case in featureEng.prevTimeSteps) 
        
#     x0 = xHistorical[timeSteps]
#     x0 = np.append(x0, np.array(x0[1:]) - np.array(x0[:-1]))
#     x0 = x0.reshape(1,-1)
#     # note this approach is fine for continuous timeSteps (e.g. last 4 time steps), 
#     # but will need to cahnge for discontinuous timeSteps (e.g. last 4, and 4 from one week ago)
#     # this could be implemented by defining timesteps as a list of lists, 
#     # e.g. timeSteps = [[0,1,2,3], [669,670,671,672]] where 672 steps is 1 week before & 669 is an hour after this (i.e. in the future relative to 672)
    
#     for key, value in models.items():
#         x[key] = x0
#         for s in range(0, nPred):            
#             if key in y:
#                 y[key].append(value.predict(x[key]))
#             else:
#                 y[key] = [value.predict(x[key])]
#             # update x
#             xNew = y[key][-1]
#             xNew = np.append(xNew, x[key][0][0:len(timeSteps)-1])
#             xNew = np.append(xNew, xNew[1:] - xNew[:-1])
#             x[key][0] = xNew
    
#     return y

# def trainModels(xTrain, yTrain, modelsToTrain):#trainLR=True, trainKNN=True, trainRF=True, trainLR=True, trainLR=True):
#     # incorporate ability to implement tuning by passing modelsToTrain as a dictionary (with parameters for each model)
#     # if a given model's parameters is empty, then just fit it without tuning
#     models = {}
#     if 'LR' in modelsToTrain:
#         print('\nTraining LinearRegression...')
#         lr = LinearRegression()
#         lr.fit(xTrain, yTrain)
#         models['LR'] = lr
#         print('Training of LinearRegression complete!')
    
#     if 'KNN' in modelsToTrain:      
#         print('\nTraining KNeighborsRegressor...')  
#         knn = KNeighborsRegressor()
#         knn.fit(xTrain, yTrain)
#         models['KNN'] = knn
#         print('Training of KNeighborsRegressor complete!')

#     if 'RF' in modelsToTrain:
#         print('\nTraining RandomForestRegressor...')
#         rf = RandomForestRegressor()
#         rf.fit(xTrain, yTrain)
#         models['RF'] = rf
#         print('Training of RandomForestRegressor complete!')
        
#     if 'SVR' in modelsToTrain:
#         print('\nTraining SVR...')
#         svr = SVR(gamma='auto')
#         svr.fit(xTrain, yTrain)
#         models['SVR'] = svr
#         print('Training of SVR complete!')

#     if 'NN' in modelsToTrain:
#         print('\nTraining MLPRegressor...')
#         nn = MLPRegressor(solver = 'lbfgs')
#         # TODO: standardize data, see: https://scikit-learn.org/stable/modules/preprocessing.html
#         nn.fit(xTrain, yTrain)
#         models['NN'] = nn
#         print('Training of MLPRegressor complete!')
    
#     return models

# nPred = 7*4*24
# prevSteps = 4
# xHistorical = np.flip(np.array(xTest['t-1'][:prevSteps]))
# yFuture = np.array(xTest['t-1'][prevSteps:prevSteps+nPred])
# yMultiPred = multiRecurs(xHistorical, prevSteps, nPred, models)

# import matplotlib.pyplot as plt
# plt.figure()
# plt.plot(yFuture)
# plt.plot(yMultiPred['LR'])
# plt.plot(yMultiPred['KNN'])


# from sklearn.model_selection import TimeSeriesSplit, cross_val_score
# forecastVar = 'SystemGeneration';
# xTrain = df[:'2019'].drop([forecastVar], axis=1) # 2014 to 2019 - verify (6*365 + 1)*24*4 = 210336 rows - (no. time steps for difference, will produce NaNs)
# yTrain = df.loc[:'2019', forecastVar]
# xTest = df['2020'].drop([forecastVar], axis=1) # 2020 - verify (365 + 1)*24*4 = 35136 rows
# yTest = df.loc['2020', forecastVar]


# from sklearn.linear_model import LinearRegression
# from sklearn.neural_network import MLPRegressor
# from sklearn.neighbors import KNeighborsRegressor
# import matplotlib.pyplot as plt
# models = []
# models.append(('LR', LinearRegression()))
# models.append(('NN', MLPRegressor(solver = 'lbfgs'))) #neural network
# models.append(('KNN', KNeighborsRegressor()))
# models.append(('RF', RandomForestRegressor(n_estimators = 10))) # Ensemble method - collection of many decision trees
# models.append(('SVR', SVR(gamma='auto'))) # kernel = linear# Evaluate each model in turn
# results = []
# names = []
# for name, model in models:
#     # TimeSeries Cross validation
#     tscv = TimeSeriesSplit(n_splits=5)
#     cv_results = cross_val_score(model, np.array(xTrain), np.array(yTrain), cv=tscv, scoring='r2')
#     results.append(cv_results)
#     names.append(name)
#     print('%s: %f (%f)' % (name, cv_results.mean(), cv_results.std()))
# # Compare Algorithms
# plt.boxplot(results, labels=names)
# plt.title('Algorithm Comparison')
# plt.show()