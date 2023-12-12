from src.cycletempo import *

config = getConfigs()
appDataContent = getAppDataContent(config)
appDataDict = parseApparatus(appDataContent)
changeDataParams(config, appDataDict, {})
removeOutputFiles(config)
executeWinTempo(config)
result = getResultsFromOutfile(config)