#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 15:30:05 2021

@author: dclabby

based on tutorial: Time Series Analysis using Pandas in Python
by Varshita Sher
available from: https://towardsdatascience.com/time-series-analysis-using-pandas-in-python-f726d87a97d8
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def plotTrends(data, includeRaw=True):
    samplesPerHour = int(3600/data.index.freq.delta.seconds)
    
    data_7d_rol = data.rolling(window = 7*24*samplesPerHour, center = True).mean()
    data_365d_rol = data.rolling(window = 365*24*samplesPerHour, center = True).mean()
    
    fig, ax = plt.subplots(figsize = (11,4))# plotting daily data
    if includeRaw:
        ax.plot(data, marker='.', markersize=2,
                color='0.6',linestyle='None', label='Raw')# plotting 7-day rolling data
    ax.plot(data_7d_rol, linewidth=2, label='7-d RollingMean')# plotting annual rolling data
    ax.plot(data_365d_rol, color='0.2', linewidth=3, label='Trend(365-d Rolling Mean)')# Beautification of plot
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.legend()
    ax.set_xlabel('Year')
    ax.set_ylabel('Power [MW]')
    ax.set_title('Trends in ' + data.columns[0])

def plotAutoCorr(data, duration):
    pd.plotting.autocorrelation_plot(data[duration])
    plt.title('Autocorrelation of ' + data.columns[0] + ' over ' + duration)
    plt.xlim(plt.xlim((0,24*4*7*10)))


plotTrends(gridData)
plotTrends(gridDataDtr)#, includeRaw=False)
plotAutoCorr(gridData, '2020')