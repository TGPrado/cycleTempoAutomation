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
        appDataContent.append(line)
        try:
            int(line[0])
            return appDataContent
        except:
            continue