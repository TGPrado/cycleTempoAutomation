import json

def getConfigs():
    arq = open("utils/config.json")
    arq = json.load(arq)
    return arq

def getAppDataContent(config):
    inFile = open(config["inFilePath"])
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