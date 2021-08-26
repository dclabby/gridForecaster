import numpy as np 
import pickle
from flask import Flask, render_template, request
from datetime import timedelta, datetime#, date,

from trainModels import regression_results
from collectData import collectEirgridData
from preProc import cleanGridData, detrendData
from featureEng import gridFeatureEng, standardizeFeatures
from postProc import intForecast

samplesPerHour = 4
featureResolution = 4 
nSteps = 24*samplesPerHour

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/forecast", methods=["GET", "POST"])
def show_forecast():
    if request.method == "POST":
        modelName = request.form.get("modelName")
        forecastVar = request.form.get("forecastVar")

        modelFile = './models/' + forecastVar + 'Models.dat'
        with open(modelFile, "rb") as f:
            _, _, _, _, yTestInt, _, yPredInt, _, testMetricsInt, sc, models = pickle.load(f)
        
        featureIndices = [np.arange(featureResolution,nSteps+featureResolution,featureResolution)*-1, 
                        np.arange(featureResolution,nSteps+featureResolution,featureResolution)*(-1) - (7*24*samplesPerHour) + nSteps]
        #if forecastVar == 'WindGeneration':
        #    featureIndices = np.arange(featureResolution,nSteps,featureResolution)*-1 # don't include previous week's wind generation
        #else:
        #    featureIndices = [np.arange(featureResolution,nSteps,featureResolution)*-1, 
        #                    np.arange(featureResolution,nSteps,featureResolution)*(-1) - (7*24*samplesPerHour) + nSteps]

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
        timeVec = [endTime + timedelta(minutes = int((n+1)*(featureResolution*60/samplesPerHour))) for n in range(0,np.shape(yForecast)[1])]
        timeVec = [t.strftime('%H:%M') for t in timeVec]            
        plotData = list(forecastResults[modelName])
        plotDate = endTime.strftime("%d %B %Y")
    else:
        timeVec = []
        plotData = []
        plotDate = ''
        modelName = ''
        forecastVar = ''
    return render_template("forecast.html", xValues=timeVec, yValues=plotData, modelName=modelName, plotDate=plotDate, forecastVar=forecastVar)

@app.route("/test", methods=["GET", "POST"])
def show_test():
    if request.method == "POST":
        modelName = request.form.get("modelName")
        startDate = request.form.get("date")
        forecastVar = request.form.get("forecastVar")

        modelFile = './models/' + forecastVar + 'Models.dat'
        with open(modelFile, "rb") as f:
            _, _, _, _, yTestInt, _, yPredInt, _, testMetricsInt, sc, models = pickle.load(f)
                
        startDateNum = [int(n) for n in startDate.split("-")]
        startDate = datetime(startDateNum[0], startDateNum[1], startDateNum[2])
        iPlot = np.where(yTestInt.index == startDate.strftime("%Y-%m-%d %H:%M:%S"))[0].astype(int)[0]
        
        #featureResolution = int(3600/yTest.index.freq.delta.seconds)
        timeVec = [int(t.strip('t'))*(int(60/featureResolution)) for t in yTestInt.columns]
        timeVec = [(startDate + timedelta(minutes=t)).strftime('%H:%M') for t in timeVec]

        #timeVec = list(np.arange(1,len(yTestInt.columns) + 1))
        yTruePlot = list(yTestInt.loc[startDate])
        yPredPlot = list(yPredInt[modelName][iPlot, :])
        testResults = testMetricsInt[modelName]

        testResults = [round(n,2) for n in testResults]
        plotDate = startDate.strftime("%d %B %Y")
        testResults.append(yTestInt.index[0].strftime("%d %B %Y"))
        testResults.append(yTestInt.index[-1].strftime("%d %B %Y"))

        testResultsPlot = regression_results(yTestInt.loc[startDate], yPredInt[modelName][iPlot])
        testResultsPlot = [round(n,2) for n in testResultsPlot]
        testResultsPlot.append(plotDate)
        testResultsPlot.append(plotDate)

    else:
        timeVec = []
        yTruePlot = []
        yPredPlot = []
        modelName = ''
        #testResults = ['','','','','',yTestInt.index[0].strftime("%d %B %Y"),yTestInt.index[-1].strftime("%d %B %Y")]
        testResults = ['','','','','','01 January 2020','29 June 2021']
        testResultsPlot = ['','','','','','','']
        plotDate = ''
        forecastVar = ''
    return render_template("test.html", xValues=timeVec, yValues1=yTruePlot, yValues2=yPredPlot, modelName=modelName, testResults=testResults, testResultsPlot=testResultsPlot, plotDate=plotDate, forecastVar=forecastVar)


"""
forecastVar = 'SystemDemand'
modelFile = './models/' + forecastVar + 'Models.dat'
with open(modelFile, "rb") as f:
    _, _, _, _, yTestInt, _, yPredInt, _, testMetricsInt, sc, models = pickle.load(f)

samplesPerHour = 4
featureResolution = 4 
nSteps = 24*samplesPerHour
if forecastVar == 'WindGeneration':
    featureIndices = np.arange(featureResolution,nSteps,featureResolution)*-1 # don't include previous week's wind generation
else:
    featureIndices = [np.arange(featureResolution,nSteps,featureResolution)*-1, 
                      np.arange(featureResolution,nSteps,featureResolution)*(-1) - (7*24*samplesPerHour) + nSteps]
"""