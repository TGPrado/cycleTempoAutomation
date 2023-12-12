import json
import os
import re
from time import sleep
from subprocess import Popen

def getConfigs():
    arq = open("utils/config.json")
    arq = json.load(arq)
    return arq

def getAppDataContent(config):
    inFile = open(config["inFilePath"] + "INFILE1")
    lines = inFile.readlines()
    appDataContent = []
    lineWithAPData = 0
    for line in lines:
        if line.find(" &APDATA") == 0:
            lineWithAPData = lines.index(line)
            break

    lines = lines[lineWithAPData: ]

    for line in lines:
        try:
            int(line[0])
            return appDataContent
        except:
            appDataContent.append(line)
            continue

def getApName(line):
    apName = line[2]
    apName = apName.split("'")
    apName = apName[1]
    return apName

def getApNumber(line):
    apNumber = line[0]
    apNumber = apNumber.split("=")
    apNumber = apNumber[1]
    return apNumber

def getParams(line):
    params = {}
    if line == []:
        return {}
    if line[-1] == " \n":
        del(line[-1])

    for param in line:
        param = param.replace(" ", "")
        param = param.split("=")
        key = param[0] 
        value = param[1] 
        params[key] = value

    return params 


def parseApparatus(appDataContent):
    appDataDict = {}
    oldApparatus = 0
    for line in appDataContent:
        fullLine = line
        line = line.split("&APDATA\t" )
        lineWidth = len(line)
        line = line[lineWidth - 1]
        line = line.replace("\t", "")
        line = line.split("  &END")[0]
        line = line.split(",")

        if lineWidth == 1:
            params = getParams(line)
            appDataDict[oldApparatus]["params"].update(params)
            appDataDict[apNumber]["line"].append(fullLine)
            continue

        apName = getApName(line)
        apNumber = getApNumber(line)    
        params = getParams(line[3:])
        appDataDict[apNumber] = {}
        appDataDict[apNumber]["params"] = params
        appDataDict[apNumber]["apName"] = apName
        appDataDict[apNumber]["line"] = [fullLine]
        oldApparatus = apNumber
    
    return appDataDict

def checkParams(newParams, apparatus):
    oldParams = apparatus["params"]
    for param in newParams:
        if param not in oldParams:
            raise Exception(f"Invalid param {param} of {apparatus['apName']}")


def getLine(apparatus, param):
    lines = apparatus["line"]
    for line in lines:
        if param in line:
            return line


def replaceParamsValue(arq, newParams, apparatus):
    for param in newParams:
        oldLine = getLine(apparatus, param)
        oldValue = apparatus["params"][param]
        
        newValue = newParams[param]
        newLine = oldLine.replace(f"{param}={oldValue}", f"{param}={newValue}")
        if newLine == oldLine:
            newLine = oldLine.replace(f"{param}=  {oldValue}", f"{param}=  {newValue}")
        
        arq = arq.replace(oldLine, newLine)
    
    return arq

def changeDataParams(config, appDataDict, paramsValues):
    arq = open(config["inFilePath"] + "INFILE1")
    arq = arq.read()
    for apNumber in paramsValues:
        if  apNumber not in appDataDict:
            raise Exception(f"Invalid apNumber: {apNumber}")

        apparatus = appDataDict[apNumber]
        newParams = paramsValues[apNumber]
        checkParams(newParams, apparatus)
        arq = replaceParamsValue(arq, newParams, apparatus)
    
    oldArq = open(config["inFilePath"] + "INFILE1", "w")
    oldArq.write(arq)
    oldArq.close()

def removeOutputFiles(config):
    path = config["inFilePath"]
    files = os.listdir(path)
    for file in files:
        if "OUTFIL" in file:
            os.remove(path + file)

def executeWinTempo(config):
    os.chdir(config["inFilePath"])
    process = Popen(config["winTempoPath"])
    files = os.listdir(config["inFilePath"])
    cont = 0.05
    while "OUTFIL4" not in files:
        sleep(cont)
        files = os.listdir(config["inFilePath"])
        cont += 0.05
    
    sleep(cont)
    process.terminate()

def apparatusParser(apparatusData):
    apparatusDict = {}

    for apparatus in apparatusData:
        data = apparatus.split(",")
        key = int(data[0])
        appType = int(data[2])
        content = {
            "AppName": data[1],
            "AppType": appType,
            "Energy Loss (enthalpy) [kW]":float(data[3]),
            "Energy Loss (HHV) [kW]":float(data[4]),
            "Energy Loss (LHV) [kW]":float(data[5]),
            "Energy": 0
        }
        if len(data) == 18 or appType == 8:
            content["Energy"] = float(data[9])

        apparatusDict[key] = content

    return apparatusDict

def getApparatusResult(lines):
    apparatusData = []
    for line in lines:
        result = re.search("^ {2,6}\d{1,2},[A-Z][a-z]{1,10}", line)
        if result:
            apparatusData.append(line)
    return apparatusParser(apparatusData)

def getGeneratorsResult(lines):
    index = 0
    generatorDict = {}
    for line in lines:
        result = re.search("^\d", line)
        if result:
            index = lines.index(line)
            break
    
    while True:
        index -= 1
        line = lines[index].split(",")
        if len(line) == 2:
            return generatorDict
        
        key = int(line[0])
        content = {
            "Energy": float(line[-1])
        }
        generatorDict[key] = content


def getTotalResults(generatorsDict, apparatusDict):
    absorvedPower = 0
    auxPowerConsumption = 0
    for apparatus in apparatusDict:
        value = apparatusDict[apparatus]

        if value["AppType"] == 8:
            auxPowerConsumption += value["Energy"]
            continue

        absorvedPower += value["Energy"]
    
    deliveredGrossPower = 0
    for generator in generatorsDict:
        value = generatorsDict[generator]
        deliveredGrossPower += value["Energy"]

    deliveredNetPower = deliveredGrossPower + auxPowerConsumption
    efficiencyGross = deliveredGrossPower/absorvedPower * 100
    efficiencyNet = deliveredNetPower/absorvedPower * 100
    totalDict = {
        "absorverd Power": absorvedPower,
        "delivered Gross Power": deliveredGrossPower,
        "aux Power Consumption": auxPowerConsumption,
        "delivered Net Power": deliveredNetPower,
        "efficency Gross": efficiencyGross,
        "efficiency Net": efficiencyNet
    }

    return totalDict

def getResultsFromOutfile(config):
    path = config["inFilePath"]
    lines = open(f"{path}OUTFIL4").readlines()

    apparatusDict = getApparatusResult(lines)
    generatorsDict = getGeneratorsResult(lines)
    totalDict = getTotalResults(generatorsDict, apparatusDict)
    results = {
        "apparatus": apparatusDict,
        "generators": generatorsDict,
        "totals": totalDict
    }
    return results