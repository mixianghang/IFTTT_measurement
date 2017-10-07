#!/usr/bin/env python3
import re
import argparse
import os, sys
import datetime
import statistics as st

def calAverageAndDeviation(sourceFile, interval = 0):
    costRe = re.compile(".* ([0-9.]+)[ ]+seconds$", re.I)
    timecostList = []
    with open(sourceFile, "r") as fd:
        for line in fd:
            if line.startswith("#"):
                continue
            matchObj = costRe.match(line.strip())
            if matchObj is None:
                continue
                #print("error when parsing line: ", line.strip())
                #sys.exit(1)
            timeCost = float(matchObj.group(1)) - interval
            timecostList.append(timeCost)
    print("got {} time cost instances".format(len(timecostList)))
    meanValue = st.mean(timecostList)
    stDev = st.pstdev(timecostList, mu = meanValue)
    return meanValue, stDev

def calAverageAndDeviation2(sourceFile, interval = 0):
    timecostList = []
    with open(sourceFile, "r") as fd:
        for line in fd:
            if line.startswith("#"):
                continue
            line = line.strip()
            timeCost = float(line) - interval
            timecostList.append(timeCost)
    print("got {} time cost instances".format(len(timecostList)))
    meanValue = st.mean(timecostList)
    stDev = st.pstdev(timecostList, mu = meanValue)
    return meanValue, stDev
def retrieveTriggerActionSequence(triggerFile, actionFile, resultFile):
    overLogList = [] # time, name, type
    triggerGenRe = re.compile("^triggerGeneratedTime: ([0-9 -]+\.\d+)$", re.I)
    actionObserveRe = re.compile("^actionResultObservedTime: (\d+[0-9 -]+\.\d+)$", re.I)
    datetimeFormat = "%Y-%m-%d %H-%M-%S.%f"
    datetimeFormat1 = "%Y-%m-%d %H:%M:%S.%f"
    with open(triggerFile, "r") as fd:
        for line in fd:
            line = line.strip()
            attrs = line.split("->")
            attr = attrs[1]
            matchObj = triggerGenRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                overLogList.append((1, datetimeObj, datetimeStr, line))
                continue
            matchObj = actionObserveRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                overLogList.append((2, datetimeObj, datetimeStr, line))
                continue
            print("error when parsing line ", line)
            sys.exit(1)

    with open(actionFile, "r") as fd:
        for line in fd:
            line = line.strip()
            attrs = line.split("->")
            attr = attrs[1]
            matchObj = triggerGenRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                overLogList.append((1, datetimeObj, datetimeStr, line))
                continue
            matchObj = actionObserveRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                overLogList.append((2, datetimeObj, datetimeStr, line))
                continue
            print("error when parsing line ", line)
            sys.exit(1)
    #print(overLogList)
    sortedOverallLogList = sorted(overLogList, key = lambda item : item[1])
    startDateTime = sortedOverallLogList[0][1]
    iterNum = 0
    resultFd = open(resultFile, "w")
    triggerNum = 0
    actionNum = 0
    for log in sortedOverallLogList:
        type, dateObj, dateStr, msg = log
        timeDelta = dateObj - startDateTime
        deltaInSecond = timeDelta.seconds + timeDelta.microseconds / 1000000
        if type == 1:
          triggerNum += 1
          typeName = "trigger"
        else:
          typeName = "action"
          actionNum += 1
        statStr = "{},{}".format(typeName, deltaInSecond, dateStr)
        resultFd.write(statStr + "\n")
    resultFd.write("triggerNum: {}, actionNum {}\n".format(triggerNum, actionNum))
    print("triggerNum: {}, actionNum {}\n".format(triggerNum, actionNum))
    resultFd.close()

def retrieveRaceConditionSequence(triggerFile, actionFile1, actionFile2, resultFile):
    triggerGenRe = re.compile("^triggerGeneratedTime: ([0-9 -]+\.\d+)$", re.I)
    actionObserveRe = re.compile("^actionResultObservedTime: (\d+[0-9 -]+\.\d+)$", re.I)
    datetimeFormat = "%Y-%m-%d %H-%M-%S.%f"
    datetimeFormat1 = "%Y-%m-%d %H:%M:%S.%f"
    triggerLogList = []
    action1LogList = []
    action2LogList = []
    with open(triggerFile, "r") as fd:
        for line in fd:
            line = line.strip()
            attrs = line.split("->")
            attr = attrs[1]
            matchObj = triggerGenRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                triggerLogList.append((1, datetimeObj, datetimeStr, line))
                continue
            print("error when parsing line ", line)
            sys.exit(1)

    with open(actionFile1, "r") as fd:
        for line in fd:
            line = line.strip()
            attrs = line.split("->")
            attr = attrs[1]
            matchObj = actionObserveRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                action1LogList.append((2, datetimeObj, datetimeStr, line))
                continue
            print("error when parsing line ", line)
            sys.exit(1)
    with open(actionFile2, "r") as fd:
        for line in fd:
            line = line.strip()
            attrs = line.split("->")
            attr = attrs[1]
            matchObj = actionObserveRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                action2LogList.append((3, datetimeObj, datetimeStr, line))
                continue
            print("error when parsing line ", line)
            sys.exit(1)
    minLen = min(len(triggerLogList), len(action1LogList), len(action2LogList))
    index = 0
    resultFd = open(resultFile, "w")
    for trigger, action1, action2 in zip(triggerLogList[:minLen], action1LogList[:minLen], action2LogList[:minLen]):
        index += 1
        triggerDate = trigger[1]
        action1Date = action1[1]
        action2Date = action2[1]
        delta1 = action1Date - triggerDate
        delta2 = action2Date - triggerDate
        timeCost1 = delta1.seconds + delta1.microseconds / 1000000
        timeCost2 = delta2.seconds + delta2.microseconds / 1000000
        statStr = "{},{},{}".format(index, timeCost1, timeCost2)
        resultFd.write(statStr + "\n")
    resultFd.close()

def retrieveRaceConditionSequence2(combinedFile, resultFile):
    triggerGenRe = re.compile("^triggerGeneratedTime: ([0-9 -]+\.\d+)$", re.I)
    actionObserveRe = re.compile("^actionResultObservedTime: (\d+[0-9 -]+\.\d+)$", re.I)
    datetimeFormat = "%Y-%m-%d %H-%M-%S.%f"
    datetimeFormat1 = "%Y-%m-%d %H:%M:%S.%f"
    triggerLogList = []
    action1LogList = []
    action2LogList = []
    with open(combinedFile, "r") as fd:
        for line in fd:
            line = line.strip()
            attrs = line.split("->")
            attr = attrs[1]
            matchObj = triggerGenRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                triggerLogList.append((1, datetimeObj, datetimeStr, line))
                continue
            matchObj = actionObserveRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                if attrs[0].startswith("2"):
                  action1LogList.append((2, datetimeObj, datetimeStr, line))
                else:
                  action2LogList.append((3, datetimeObj, datetimeStr, line))
                continue
            print("error when parsing line ", line)
            sys.exit(1)

    minLen = min(len(triggerLogList), len(action1LogList), len(action2LogList))
    index = 0
    resultFd = open(resultFile, "w")
    for trigger, action1, action2 in zip(triggerLogList[:minLen], action1LogList[:minLen], action2LogList[:minLen]):
        index += 1
        triggerDate = trigger[1]
        action1Date = action1[1]
        action2Date = action2[1]
        delta1 = action1Date - triggerDate
        delta2 = action2Date - triggerDate
        timeCost1 = delta1.seconds + delta1.microseconds / 1000000
        timeCost2 = delta2.seconds + delta2.microseconds / 1000000
        statStr = "{},{},{}".format(index, timeCost1, timeCost2)
        resultFd.write(statStr + "\n")
    resultFd.close()
def retrieveCostList(sourceFile, resultFile = None, interval = 0):
    costRe = re.compile(".* ([0-9.]+)[ ]+seconds$", re.I)
    timecostList = []
    with open(sourceFile, "r") as fd:
        for line in fd:
            if line.startswith("#"):
                continue
            matchObj = costRe.match(line.strip())
            if matchObj is None:
                continue
                #print("error when parsing line: ", line.strip())
                #sys.exit(1)
            timeCost = float(matchObj.group(1)) - interval
            timecostList.append(timeCost)
    print("got {} time cost instances".format(len(timecostList)))
    if resultFile is not None:
        open(resultFile, "w").write("\n".join([str(value) for value in timecostList]) + "\n")
    return timecostList


if __name__ == "__main__":
    parser = argparse.ArgumentParser("analysis")
    parser.add_argument("testFile", type = str)
    parser.add_argument("logFile", type = str)
    parser.add_argument("resultFile", type = str)
    parser.add_argument("-triggerFile", type = str, default = None)
    parser.add_argument("-actionFile", type = str, default = None)
    options = parser.parse_args()

    testFile = options.testFile
    logFile  = options.logFile
    resultFile = options.resultFile
    triggerFile = options.triggerFile
    actionFile = options.actionFile
    overLogList = [] # time, name, type
    timeCostRe = re.compile("time cost for .*iter (\d+) is ([0-9.]+) seconds", re.I)
    triggerGenRe = re.compile("^triggerGeneratedTime: ([0-9 -]+\.\d+)$", re.I)
    actionObserveRe = re.compile("^actionResultObservedTime: (\d+[0-9 -]+\.\d+)$", re.I)
    timeCostList = []
    datetimeFormat = "%Y-%m-%d %H-%M-%S.%f"
    datetimeFormat1 = "%Y-%m-%d %H:%M:%S.%f"
    typeDict = {
            10 : "trigger generated locally",
            20 : "trigger observed locally",
            25 : "trigger synced to server",
            30 : "trigger request from IFTTT",
            40 : "action request from IFTTT",
            50 : "action executed locally",
            60 : "action result observed locally",
            }
    with open(testFile, "r") as fd:
        for line in fd:
            line = line.strip()
            attrs = line.split("->")
            attr = attrs[1]
            matchObj = timeCostRe.match(attr)
            if matchObj is not None:
                timeCost = float(matchObj.group(2))
                timeCostList.append(timeCost)
                continue
            matchObj = triggerGenRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                type = 10
                overLogList.append((type, datetimeObj, datetimeStr, line))
                continue
            matchObj = actionObserveRe.match(attr)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                type = 60
                overLogList.append((type, datetimeObj, datetimeStr, line))
                continue
            print("error when parsing line ", line)
            sys.exit(1)
    triggerRequestRe = re.compile(".*->logTime: ([ 0-9.:-]+)->.*->logType: 1", re.I)
    triggerRequestDetectionRe = re.compile(".*->logDetectionTime: ([ 0-9.:-]+)->.*->logType: 1", re.I)
    actionRequestRe = re.compile(".*->logTime: ([ 0-9.:-]+)->.*->logType: 2$", re.I)
    actionRequestDetectionRe = re.compile(".*->logDetectionTime: ([ 0-9.:-]+)->.*->logType: 2", re.I)
    with open(logFile, "r") as fd:
        for line in fd:
            line = line.strip()
            matchObj = triggerRequestRe.match(line)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat1) 
                type = 30
                overLogList.append((type, datetimeObj, datetimeStr, line))
                continue
            matchObj = actionRequestRe.match(line)
            if matchObj is not None:
                datetimeStr = matchObj.group(1)
                datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat1) 
                type = 40
                overLogList.append((type, datetimeObj, datetimeStr, line))
                continue
            #print("error when parsing line ", line)
            ##sys.exit(1)

    triggerObserveRe = re.compile("^triggerEventObservedTime: ([0-9 -]+\.\d+)$", re.I)
    triggerSyncRe = re.compile("^triggerEventSyncedTime: (\d+[0-9 -]+\.\d+)$", re.I)
    if triggerFile is not None:
        with open(triggerFile, "r") as fd:
            for line in fd:
                line = line.strip()
                attrs = line.split("->")
                attr = attrs[1]
                matchObj = triggerObserveRe.match(attr)
                if matchObj is not None:
                    datetimeStr = matchObj.group(1)
                    datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                    type = 20
                    overLogList.append((type, datetimeObj, datetimeStr, line))
                    continue
                matchObj = triggerSyncRe.match(attr)
                if matchObj is not None:
                    datetimeStr = matchObj.group(1)
                    datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                    type = 25
                    overLogList.append((type, datetimeObj, datetimeStr, line))
                    continue
                #print("error when parsing line ", line)
                #sys.exit(1)

    actionExecuteRe = re.compile("^actionDetectTime: ([0-9 -]+\.\d+)$", re.I)
    if actionFile is not None:
        with open(actionFile, "r") as fd:
            for line in fd:
                line = line.strip()
                attrs = line.split("->")
                attr = attrs[1]
                matchObj = actionExecuteRe.match(attr)
                if matchObj is not None:
                    datetimeStr = matchObj.group(1)
                    datetimeObj = datetime.datetime.strptime(datetimeStr, datetimeFormat) 
                    type = 50
                    overLogList.append((type, datetimeObj, datetimeStr, line))
                    continue

    #print(overLogList)
    sortedOverallLogList = sorted(overLogList, key = lambda item : item[1])
    iterNum = 0
    resultFd = open(resultFile, "w")
    for log in sortedOverallLogList:
        type, dateObj, dateStr, msg = log
        typeName = typeDict[type]
        statStr = "iter{},{}: {}".format(iterNum, typeName, dateStr)
        resultFd.write(statStr + "\n")
        if type == 60:
            timeCost = timeCostList[iterNum]
            resultFd.write("iter{} timeCost: {} seconds\n".format(iterNum, timeCost))
            iterNum += 1
    resultFd.close()

