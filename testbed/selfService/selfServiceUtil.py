#!/usr/bin/env python3
import requests
import json
import logging
import argparse
import time
import sys
import datetime

def sendTriggerQuery2Server(deviceState = 1):
    logger = logging.getLogger(__name__)
    basicTriggerFieldName = "which_light_is_turned_on"
    payload = {
            "triggerFields" : {
                basicTriggerFieldName : 1,
                }
            }
    requestUrl = "http://129.79.242.194:8081/ifttt/v1/triggers/light_turned_on.php"
    headers = {
            "IFTTT-CHANNEL-KEY" : "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd0",
            }
    response = requests.post(requestUrl, headers = headers, json=payload)
    print(response.text)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return False
    else:
        return True

#sync device events to the server side
def sendEvent2Server(deviceId, deviceState):
    logger = logging.getLogger(__name__)
    currTimeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    payload = {
            "userId" : 1,
            "deviceId" : deviceId,
            "deviceState" : deviceState,
            "eventTime" : currTimeStr,
            }
    #payload = json.dumps(payload)
    requestUrl = "http://129.79.242.194:8081/ifttt/v1/updateState.php"
    headers = {
            "Self-Channel-Key" : "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd",
            }
    response = requests.post(requestUrl, headers = headers, json=payload)
    print(response.text)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return False
    else:
        return True

#get actions from the server side
def getActionFromServer(deviceId, deviceState):
    logger = logging.getLogger(__name__)
    currTimeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    payload = {
            "userId" : 1,
            "deviceId" : deviceId,
            "deviceState" : deviceState,
            "eventTime" : currTimeStr,
            }
    #payload = json.dumps(payload)
    requestUrl = "http://129.79.242.194:8081/ifttt/v1/updateState.php"
    headers = {
            "Self-Channel-Key" : "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd",
            }
    response = requests.post(requestUrl, headers = headers, json=payload)
    print(response.text)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return False
    else:
        return True
def getLogFromServer(startTime = None, endTime = None, type = None, startId = 0, numLimit = 10):
    logger = logging.getLogger(__name__)
    currTimeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    payload = {
            "startTime" : startTime,
            "endTime" : endTime,
            "type" : type,
            "startId" : startId,
            "numLimit" : numLimit,
            }
    #payload = json.dumps(payload)
    requestUrl = "http://129.79.242.194:8081/ifttt/v1/getLog.php"
    headers = {
            "Self-Channel-Key" : "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd",
            }
    response = requests.post(requestUrl, headers = headers, json=payload)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return None
    else:
        #print(response.text)
        return json.loads(response.text)["data"]

def insertLog2Server(logType,  logMessage, logTime = None):
    logger = logging.getLogger(__name__)
    currTimeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    if logTime is None:
        logTime = currTimeStr
    payload = {
            "logType" : logType,
            "logMessage" : logMessage,
            "logTime" : logTime,
            }
    #payload = json.dumps(payload)
    requestUrl = "http://129.79.242.194:8081/ifttt/v1/addLog.php"
    headers = {
            "Self-Channel-Key" : "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd",
            }
    response = requests.post(requestUrl, headers = headers, json=payload)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return False
    else:
        print(response.text)
        return True

def getActionFromServer(startTime = None, endTime = None, deviceId = None, deviceState = None, startId = 0, numLimit = 10, isFinished = 0):
    logger = logging.getLogger(__name__)
    currTimeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    payload = {
            "startTime" : startTime,
            "endTime" : endTime,
            "deviceId" : deviceId,
            "deviceState" : deviceState,
            "startId" : startId,
            "numLimit" : numLimit,
            "isFinished" : isFinished,
            }
    #payload = json.dumps(payload)
    requestUrl = "http://129.79.242.194:8081/ifttt/v1/getAction.php"
    headers = {
            "Self-Channel-Key" : "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd",
            }
    response = requests.post(requestUrl, headers = headers, json=payload)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return None
    else:
        #print(response.text)
        actionListResult = json.loads(response.text)
        actionList = actionListResult["data"] if "data" in actionListResult else []
        return actionList

def updateActionResult2Server(actionIdList, actionStateList):
    logger = logging.getLogger(__name__)
    currTimeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    payload = []
    for actionId, actionState in zip(actionIdList, actionStateList):
        actionObj = {
                "actionId" : actionId,
                "actionState" : actionState,
                }
        payload.append(actionObj)
    #payload = json.dumps(payload)
    requestUrl = "http://129.79.242.194:8081/ifttt/v1/updateActionResult.php"
    headers = {
            "Self-Channel-Key" : "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd",
            }
    response = requests.post(requestUrl, headers = headers, json=payload)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return False
    else:
        print(response.text)
        return True
def realtimeApi(triggerIdList):
    defaultTriggerId = "1eadfa264f6f398e5bd085284214959b580d3043"
    currTimeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(currTimeStr)
    logger = logging.getLogger(__name__)
    iftttChannelKey = "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd0"
    url = "http://realtime.ifttt.com/v1/notifications"
    dataList = []
    for triggerId in triggerIdList:
        dataList.append({"trigger_identity" : triggerId})
    payload = {
            "data" : dataList,
            }
    headers = {
            "IFTTT-Channel-Key" : iftttChannelKey,
            }
    response = requests.post(url, json = payload, headers = headers)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return False
    else:
        #print(response.text)
        #return json.loads(response.text)
        return True
    

