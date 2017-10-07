#!/usr/bin/env python3
from multiprocessing import Process
import argparse
import testSimpleRecipe_2 as sr
import os, sys
import re

recipeFuncDict = {
        "alexa_wemo" : sr.testAlexaWemoRecipe,
        "alexa_hue" : sr.testAlexaHueRecipe,
        "wemo_hue" : sr.testWemoHueRecipe,
        "alexa_sheet" : sr.testAlexaGoogleSheetRecipe,
        "hue_gmail" : sr.testGmailHueRecipe,
        "wemo_sheet" : sr.testWemoGoogleSheetRecipe,
        "gmail_drive" : sr.testGmailDrive,
}
recipeParamsDict = {
        "alexa_wemo" : "-wemoport 10085 ",
        "alexa_hue" : "",
        "wemo_hue" : "-wemoport 10085 ",
        "alexa_sheet" : "",
        "hue_gmail" : "",
        "wemo_sheet" : "-wemoport 10085 ",
        "gmail_drive" : "",
}
recipeIntervalDict = {
        "alexa_wemo" : 0.1,
        "alexa_hue" : 0.1,
        "wemo_hue" : 1,
        "alexa_sheet" : 0.1,
        "hue_gmail" : 1,
        "wemo_sheet" : 1,
        "gmail_drive" : 1,
}
recipeGroupList = [
            [
                "alexa_hue",
                "wemo_sheet",
                "gmail_drive",

                ],
            [
                "wemo_hue",
                "alexa_sheet",
                "gmail_drive",

                ],
            [
                "alexa_sheet",
                "hue_gmail",
                "wemo_sheet",
                #"gmail_drive",

                ],
        ]

def simpleConcurrent(argv):
    parser = argparse.ArgumentParser("simple concurrent")
    parser.add_argument("resultDir", type = str)
    parser.add_argument("-timeLimit", type = int, default = 300)
    parser.add_argument("-groupId", type = int, default = 0)
    options = parser.parse_args(argv)
    resultDir = options.resultDir
    timeLimit = options.timeLimit
    groupId   = options.groupId
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)
    if groupId >= len(recipeGroupList):
        print("error with wrong groupId ", groupId)
        sys.exit(1)
    recipeGroup = recipeGroupList[groupId]
    processList = []
    #set up processes
    for recipeName in recipeGroup:
        recipeFunction = recipeFuncDict[recipeName]
        recipeParamPrefix = recipeParamsDict[recipeName]
        recipeInterval = recipeIntervalDict[recipeName]
        resultFile = os.path.join(resultDir, "{}_interval-{}_timeLimit-{}.txt".format(recipeName, recipeInterval, timeLimit))
        if len(recipeParamPrefix) > 0:
            recipeParamStr = "{} -interval {} -timeLimit {} {}".format(recipeParamPrefix, recipeInterval, timeLimit, resultFile)
        else:
            recipeParamStr = "-interval {} -timeLimit {} {}".format(recipeInterval, timeLimit, resultFile)
        recipeParamList = re.split(r"[ ]+", recipeParamStr)
        print("recipe function: {}, recipe params: {}".format(recipeFunction, recipeParamList))
        recipeProcess = Process(target = recipeFunction, args = (recipeParamList,))
        processList.append(recipeProcess)
    print("got {} processes".format(len(processList)))
    #sys.exit(1)
    for recipeProcess in processList:
        recipeProcess.start()
    for recipeProcess in processList:
        recipeProcess.join()

def conflictConcurrent(argv):
    pass

def infiniteLoop(argv):
    pass

conFuncDict = {
        "concurr" : simpleConcurrent,
        "conflict" : conflictConcurrent,
        "infinite" : infiniteLoop,
        }
if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("provide at least function name from the set", conFuncDict.keys())
        sys.exit(1)
    funcName = sys.argv[1]
    if funcName not in conFuncDict:
        print("function name is not suported", conFuncDict.keys())
        sys.exit(1)

    function = conFuncDict[funcName]
    function(sys.argv[2:])
