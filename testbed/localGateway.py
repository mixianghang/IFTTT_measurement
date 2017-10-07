#!/usr/bin/env python3
from hue import HueControlUtil as hue
from wemo import WemoControlUtil as wemo
from selfService import selfServiceUtil as ssu
import logging
import time
import uuid
import argparse, os, sys
import datetime
import traceback
#monitor states of local devices, send  updates to server side once updates showed up 
#poll possible actions and execute

deviceIdDict = {
        1 : "WeMo Switch", #wemo switch 
        2 : 2, #light in the living room
        3 : 1, #light in the bedroom
        }
triggerIdentityDict  = {
        1 : "1eadfa264f6f398e5bd085284214959b580d3043",
        2 : None,
        3 : None,
        }
#logFormat = "%(asctime)s-%(levelno)s-%(message)s-%(processName)s-%(lineno)s-%(funcName)s-%(filename)s"
logFormat = "%(asctime)s-%(levelno)s-%(message)s"
datetimeFormat = "%Y-%m-%d %H-%M-%S.%f"
#monitor local devices for  state change events
#once state change is detected, send to server, 
def triggerMonitor(argv):
    parser = argparse.ArgumentParser("trigger monitor")
    parser.add_argument("resultFile", type = str)
    parser.add_argument("-targetDeviceId", default = None, choices = list(deviceIdDict.keys()), type = int)
    parser.add_argument("-targetDeviceState", default = None, type = int)
    parser.add_argument("-isRealTime", action = "store_true")
    parser.add_argument("-timeLimit", default = None, type = int)
    parser.add_argument("-interval", default = 1, type = float)
    options = parser.parse_args(argv)
    hueController = hue.HueController()
    bind = "0.0.0.0:10087"
    wemoController = wemo.WemoController(bind = bind)
    switchName = "WeMo Switch"
    switch = wemoController.discoverSwitch(switchName, timeout = 60)
    if switch is None:
      print("error to locate the switch")
      sys.exit(1)
    else:
      print("switch discoverred")
    deviceMonitorDict = {
            1 : wemoController,
            2 : hueController,
            3 : hueController,
            }
    resultFile = options.resultFile
    targetDeviceState = options.targetDeviceState
    targetDeviceId = options.targetDeviceId
    pollInterval = options.interval
    timeLimit = options.timeLimit
    isRealTime = options.isRealTime

    #configure logger
    formatter = logging.Formatter(logFormat)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    logger.info("start to monitor trigger events locally")

    startTime = time.time()
    if targetDeviceId is None:
        deviceListToMonitor = list(deviceIdDict.keys()) 
    else:
        deviceListToMonitor = [targetDeviceId]
    logger.info("targets are %s", deviceListToMonitor)
    preStateDict = {}
    statList = []
    resultFd = open(resultFile, "a")
    while True:
        try:
            #check possible timeout
            if timeLimit is not None:
                currTime = time.time()
                if currTime - startTime > timeLimit:
                    logger.info("time out, quit monitoring")
                    break
            #check latest states for the given list of devices
            for deviceId in deviceListToMonitor:
                monitor = deviceMonitorDict[deviceId]
                deviceLocalId = deviceIdDict[deviceId]
                deviceState = monitor.getState(deviceLocalId)
                #logger.debug("current device status is %d", deviceState)
                #initial state, no checking, no updates
                if deviceId not in preStateDict:
                    preStateDict[deviceId] = deviceState
                    continue
                preState = preStateDict[deviceId]
                isUpdate = False
                if targetDeviceState is None and deviceState != preState:
                    isUpdate = True
                if targetDeviceState is not None:
                    if targetDeviceState != preState and targetDeviceState == deviceState:
                        isUpdate = True

                #log update time, send updates to server, send realtime notification if needed
                if isUpdate:
                    updateUuid = uuid.uuid4()
                    updateTime = datetime.datetime.now()
                    tempStat = "triggerUUID: {}->triggerEventObservedTime: {}->deviceId: {}->devicePreState: {}->deviceNewState: {}".format(updateUuid, updateTime.strftime(datetimeFormat), deviceId, preState, deviceState)
                    statList.append(tempStat)
                    resultFd.write(tempStat + "\n")
                    resultFd.flush()
                    logger.info(tempStat)
                    preStateDict[deviceId] = deviceState
                    #send updates to server
                    sendUpdateResult = ssu.sendEvent2Server(deviceId, deviceState)
                    if sendUpdateResult == False:
                        logger.warning("error when sending updates to server")
                        continue
                    updateSentTime = datetime.datetime.now()
                    tempStat = "triggerUUID: {}->triggerEventSyncedTime: {}->deviceId: {}->devicePreState: {}->deviceNewState: {}".format(updateUuid, updateSentTime.strftime(datetimeFormat), deviceId, preState, deviceState)
                    statList.append(updateTime)
                    resultFd.write(tempStat + "\n")
                    resultFd.flush()
                    logger.info(tempStat)
                    
                    #send realtime notification if enabled
                    triggerIdentity = triggerIdentityDict[deviceId]
                    if isRealTime and triggerIdentity is not None:
                        realtimeResult = ssu.realtimeApi([triggerIdentity])
                        if realtimeResult == False:
                            logger.warning("error when sending realtime notifications")
                            continue
                        realtimeSentTime = datetime.datetime.now()
                        tempStat = "triggerUUID: {}->realTimeSentTime: {}->deviceId: {}->devicePreState: {}->deviceNewState: {}".format(updateUuid, realtimeSentTime.strftime(datetimeFormat), deviceId, preState, deviceState)
                        statList.append(updateTime)
                        resultFd.write(tempStat + "\n")
                        resultFd.flush()
                        logger.info(tempStat)
                preStateDict[deviceId] = deviceState
            time.sleep(pollInterval)
        except Exception as e:
            logger.error("exception occurred: %s", traceback.format_exc())
            continue
    resultFd.close()
    #logger.info("all logs %s", statList)

#monitor server side for action commands,
#once an action command is detected, execute it and update it as finished on server side
def actionMonitor(argv):
    parser = argparse.ArgumentParser("action monitor")
    parser.add_argument("resultFile", type = str)
    parser.add_argument("-targetDeviceId", default = None, choices = list(deviceIdDict.keys()), type = int)
    parser.add_argument("-targetDeviceState", default = None, type = int)
    parser.add_argument("-timeLimit", default = None, type = int)
    parser.add_argument("-interval", default = 1, type = float)
    options = parser.parse_args(argv)
    hueController = None
    wemoController = None
    hueController = hue.HueController()
    bind = "0.0.0.0:10088"
    wemoController = wemo.WemoController(bind = bind)
    switchName = "WeMo Switch"
    switch = wemoController.discoverSwitch(switchName, timeout = 60)
    if switch is None:
      print("error to locate the switch")
      sys.exit(1)
    else:
      print("switch discoverred")
    deviceMonitorDict = {
            1 : wemoController,
            2 : hueController,
            3 : hueController,
            }
    resultFile = options.resultFile
    targetDeviceState = options.targetDeviceState
    targetDeviceId = options.targetDeviceId
    pollInterval = options.interval
    timeLimit = options.timeLimit

    #configure logger
    formatter = logging.Formatter(logFormat)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    startTime = time.time()
    preStateDict = {}
    statList = []
    resultFd = open(resultFile, "a")
    while True:
        try:
            #check possible timeout
            if timeLimit is not None:
                currTime = time.time()
                if currTime - startTime > timeLimit:
                    logger.info("time out, quit monitoring")
                    break
            #check latest states for the given list of devices
            newActionList = ssu.getActionFromServer(deviceId = targetDeviceId, deviceState = targetDeviceState)
            if len(newActionList) <= 0:
                time.sleep(pollInterval)
                continue
            #logger.debug("got those new actions %s", newActionList)
            #try to execute those ,4
            for action in newActionList:
                actionUuid = uuid.uuid4()
                deviceId = int(action["deviceId"])
                deviceState = int(action["deviceState"])
                actionId = int(action["id"])
                actionCreateTime = action["createTime"]
                deviceMonitor = deviceMonitorDict[deviceId]
                deviceLocalId = deviceIdDict[deviceId]

                #execute the action command
                actionResult = True
                actionResult = deviceMonitor.setState(deviceLocalId, deviceState)
                if actionResult == False:
                    logger.warning("error when executing action command")
                    continue
                actionTime = datetime.datetime.now()
                tempStat = "actionUUID: {}->actionCreateTime: {}->deviceId: {}->deviceState: {}->actionId: {}".format(actionUuid, actionCreateTime, deviceId, deviceState, actionId)
                statList.append(tempStat)
                resultFd.write(tempStat + "\n")
                resultFd.flush()
                logger.info(tempStat)
                tempStat = "actionUUID: {}->actionDetectTime: {}->deviceId: {}->deviceState: {}->actionId: {}".format(actionUuid,  actionTime.strftime(datetimeFormat), deviceId, deviceState, actionId)
                statList.append(tempStat)
                resultFd.write(tempStat + "\n")
                resultFd.flush()
                logger.info(tempStat)

                #send action results to server
                actionIdList = [actionId]
                actionStateList = [1]
                actionSyncResult = ssu.updateActionResult2Server(actionIdList, actionStateList)
                if actionSyncResult == False:
                    logger.warning("error when sync action results to server side")
                    continue
                actionSyncTime = datetime.datetime.now()
                tempStat = "actionUUID: {}->actionSyncTime: {}->deviceId: {}->deviceState: {}->actionId: {}".format(actionUuid, actionSyncTime.strftime(datetimeFormat), deviceId, deviceState, actionId)
                statList.append(tempStat)
                resultFd.write(tempStat + "\n")
                resultFd.flush()
                logger.info(tempStat)
            time.sleep(pollInterval)
        except Exception as e:
            logger.error("exception occurred: %s", traceback.format_exc())
            continue
    resultFd.close()
    #logger.info("all logs %s", statList)
            
logTypeDict = {
        1 : "trigger request",
        2 : "action request",
        10 : "new device state detected",
        20 : "new device state synced to server",
        50 : "action synced from server and runs locally",
        60 : "action execution reuslt syneced to server",
        70 : "action result observed locally",
        }
#monitor trigger/action requests from IFTTT to our server side
#once a request is detected, write back to log
def logMonitor(argv):
    parser = argparse.ArgumentParser("log monitor")
    parser.add_argument("resultFile", type = str)
    parser.add_argument("-timeLimit", default = None, type = int)
    parser.add_argument("-interval", default = 1, type = float)
    options = parser.parse_args(argv)
    resultFile = options.resultFile
    pollInterval = options.interval
    timeLimit = options.timeLimit

    #configure logger
    formatter = logging.Formatter(logFormat)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    logger.info("start logging monitor")

    startMonitorTime = time.time()
    timeFormat = "%Y-%m-%d %H:%M:%S.%f"
    nextStartTime = datetime.datetime.now().strftime(timeFormat)
    statList = []
    resultFd = open(resultFile, "a")
    while True:
        try:
            #check possible timeout
            if timeLimit is not None:
                currTime = time.time()
                if currTime - startMonitorTime > timeLimit:
                    logger.info("time out, quit monitoring")
                    break
            #check latest states for the given list of devices
            #logger.debug("queries new logs after %s", nextStartTime)
            newLogList = ssu.getLogFromServer(startTime = nextStartTime)
            if len(newLogList) <= 0:
                time.sleep(pollInterval)
                continue
            logDetectionTime = datetime.datetime.now().strftime(timeFormat)
            #try to execute those ,4
            for index, log in enumerate(newLogList):

                logTime = log["time"]
                if index == 0:
                    nextStartTime = logTime
                logUuid = uuid.uuid4()
                logType = int(log["type"])
                logTypeName = logTypeDict[logType]
                tempStat = "logUuid: {}->logTime: {}->logName: {}->logType: {}".format(logUuid, logTime, logTypeName, logType)
                statList.append(tempStat)
                resultFd.write(tempStat + "\n")
                resultFd.flush()
                logger.info(tempStat)

                tempStat = "logUuid: {}->logDetectionTime: {}->logName: {}->logType: {}".format(logUuid, logDetectionTime, logTypeName, logType)
                statList.append(tempStat)
                resultFd.write(tempStat + "\n")
                resultFd.flush()
                logger.info(tempStat)

            time.sleep(pollInterval)
        except Exception as e:
            logger.error("exception occurred: %s", traceback.format_exc())
            continue
    resultFd.close()
    #logger.info("all logs %s", statList)

monitorDict = {
        "trigger" : triggerMonitor,
        "action"  : actionMonitor,
        "log"     : logMonitor,
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("error: missing parameters")
        sys.exit(1)
    funcName = sys.argv[1]
    if funcName not in monitorDict:
        print("choose from availabel functions: ", monitorDict.keys())
        sys.exit(1)
    function = monitorDict[funcName]
    function(sys.argv[2:])
