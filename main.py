from src.cycletempo import *

config = getConfigs()
appDataContent = getAppDataContent(config)
appDataDict = parseApparatus(appDataContent)
changeDataParams(config, appDataDict, {})