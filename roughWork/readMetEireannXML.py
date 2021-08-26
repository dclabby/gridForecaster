#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 16:13:17 2021

@author: dclabby
"""  
xmlPath = '/home/dclabby/Documents/Springboard/HDAIML_SEP/Semester03/Project/app/code/data/MetEireann/Forecast/'
xmlFile = xmlPath + 'DublinAirport_2021-08-11.xml'

# importing element tree under the alias of ET
import pandas as pd
import xml.etree.ElementTree as et
  
# Passing the path of the xml document to enable the parsing process
tree = et.parse(xmlFile)
  
# getting the parent tag of the xml document
root = tree.getroot()

columns = ['time', 'temperature', 'windSpeed']#, 'globalRadiation']

xmlData = []
# xmlData = {}
for timeTag in root.findall('product/time'):
    rowTmp = []
    if timeTag.attrib['from'] == timeTag.attrib['to']:
        rowTmp.append(timeTag.attrib['from'].replace('T', ' ').replace('Z', ''))
        
        for l in timeTag.find('location'): # iterates through children of location tag
            for col in columns[1:]:
                if l.tag == col:
                    try:
                        rowTmp.append(float(l.attrib['value']))
                    except:
                        rowTmp.append(float(l.attrib['mps']))
        xmlData.append(rowTmp)
        # xmlData[timeTag.attrib['from']] = rowTmp

xmlDf = pd.DataFrame(xmlData, columns=columns).set_index('time')
        

