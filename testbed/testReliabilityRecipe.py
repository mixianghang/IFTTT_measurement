from hue import HueControlUtil as hue
from wemo import WemoControlUtil as wemo
from alexa import AlexaControlUtil as alexa
from googleApis.googleSheetController import GoogleSheetController
from googleApis.googleDriveController import GoogleDriveController
from googleApis.gmailController import GmailController
import time, os, sys, argparse, datetime
import shutil
import uuid
from multiprocessing import Process
datetimeFormat = "%Y-%m-%d %H-%M-%S.%f"
def triggerAlexaMusic(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    playAudioFile = "alexa/audioFiles/playMusic.wav"
    changeAudioFile = "alexa/audioFiles/alexaNextMusic.wav"
    resultFd = open(resultFile, "a")
    alexaController = alexa.AlexaController()
    testUuid =  uuid.uuid4()
    startTime = time.time()
    for index in range(iterNum):
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        if index == 0:
            alexaController.saySomething(playAudioFile)
            triggerTime = datetime.datetime.now()
            time.sleep(5)
        else:
            alexaController.saySomething(changeAudioFile)
            triggerTime = datetime.datetime.now()
        print("send out voice command to alexa")
        statStr = "testUuid: {}->triggerGeneratedTime: {}->alexaMusic".format(testUuid, triggerTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        time.sleep(interval)
    resultFd.close()
def triggerAlexaBed(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    audioFile = "alexa/audioFiles/alexa_trigger_bedtime.wav"
    resultFd = open(resultFile, "a")
    alexaController = alexa.AlexaController()
    testUuid =  uuid.uuid4()
    startTime = time.time()
    for index in range(iterNum):
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        alexaController.saySomething(audioFile = audioFile)
        triggerTime = datetime.datetime.now()
        print("send out voice command to alexa")
        statStr = "testUuid: {}->triggerGeneratedTime: {}->hueBed".format(testUuid, triggerTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        time.sleep(interval)
    resultFd.close()

def triggerAlexaSwitch(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    audioFile = "alexa/audioFiles/AlexaTriggerTurnOnSwitch.wav"
    resultFd = open(resultFile, "a")
    alexaController = alexa.AlexaController()
    testUuid =  uuid.uuid4()
    startTime = time.time()
    for index in range(iterNum):
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        alexaController.saySomething(audioFile = audioFile)
        triggerTime = datetime.datetime.now()
        print("send out voice command to alexa")
        statStr = "testUuid: {}->triggerGeneratedTime: {}->hueBed".format(testUuid, triggerTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        time.sleep(interval)
    resultFd.close()
    pass

def triggerNewGmail(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    #gmailController = GmailController("xianghangmi")
    gmailSenderController = GmailController("senmuxing")
    testUuid =  uuid.uuid4()
    startTime = time.time()
    for index in range(iterNum):
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        nowDate = datetime.datetime.now()
        nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
        #send email from senmuxing@gmail.com to xianghangmi@gmail.com
        subject = "ifttt test at {}".format(nowStr)
        messageBody = subject
        message = GmailController.create_message(sender = "senmuxing@gmail.com", to = "xianghangmi@gmail.com", subject = subject, message_text = messageBody)
        gmailSenderController.sendMessage(message)
        triggerTime = datetime.datetime.now()
        statStr = "testUuid: {}->triggerGeneratedTime: {}->hueBed".format(testUuid, triggerTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        time.sleep(interval)
    resultFd.close()

def triggerNewGmailWithAttach(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    #gmailController = GmailController("xianghangmi")
    gmailSenderController = GmailController("senmuxing")
    testUuid =  uuid.uuid4()
    startTime = time.time()
    for index in range(iterNum):
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        nowDate = datetime.datetime.now()
        nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
        #send email from senmuxing@gmail.com to xianghangmi@gmail.com
        subject = "ifttt test at {}".format(nowStr)
        tempFile = "ifttTest_{}.txt".format(nowStr)
        open(tempFile, "w").write(subject)
        messageBody = subject
        message = GmailController.create_message_with_attachment(sender = "senmuxing@gmail.com", to = "xianghangmi@gmail.com", subject = subject, message_text = messageBody, file = tempFile)
        gmailSenderController.sendMessage(message)
        triggerTime = datetime.datetime.now()
        statStr = "testUuid: {}->triggerGeneratedTime: {}->hueBed".format(testUuid, triggerTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        os.remove(tempFile)
        time.sleep(interval)
    resultFd.close()

def triggerWemoTurnon(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    testUuid =  uuid.uuid4()
    bind = "0.0.0.0:{}".format(10085)
    switchName = "WeMo Switch"
    wemoController = wemo.WemoController(bind = bind)
    switch = wemoController.discoverSwitch(switchName)
    if switch is None:
      print("error to locate the switch")
      sys.exit(1)
    else:
      print("switch discoverred")
    startTime = time.time()
    index = 0
    while True:
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        wemoController.turnonSwitch(switchName)
        triggerTime = datetime.datetime.now()
        print("send out voice command to alexa")
        statStr = "testUuid: {}->triggerGeneratedTime: {}->wemo Turned on".format(index, triggerTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        time.sleep(1)
        wemoController.turnoffSwitch(switchName)
        index += 1
        if index >= iterNum:
            break
        time.sleep(interval)
    resultFd.close()
    pass

def actionMusicLog(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    spreadsheetId = "1M8uG1TwVg53hXbaluqLspYXoxPf0PhibyH-bEHCo96o"
    sheetName = "Sheet1"
    testUuid =  uuid.uuid4()
    startTime = time.time()
    sheetController = GoogleSheetController()
    spreadsheet = sheetController.getSpreadSheet(spreadsheetId)
    retrievedSheetName = spreadsheet["sheets"][0]["properties"]["title"]
    print("title of first sheet is ", spreadsheet["sheets"][0]["properties"]["title"])
    if retrievedSheetName != sheetName:
        print("sheet name doesn't match, use retrieved one: preconfigured one: {}, retrieved one {}".format(sheetName, retrievedSheetName))
        sheetName = retrievedSheetName
    currentRowList = sheetController.getRowList(spreadsheetId, range = sheetName)
    index = 0
    while True:
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        latestRowList = sheetController.getRowList(spreadsheetId, range = sheetName)
        actionTime = datetime.datetime.now()
        appendNum = len(latestRowList) - len(currentRowList)
        if appendNum > 0:
            index += 1
        for appendIndex in range(appendNum):
            statStr = "testUuid: {}->actionResultObservedTime: {}->sheet".format(testUuid, actionTime.strftime(datetimeFormat))
            print(statStr)
            resultFd.write(statStr + "\n")
            resultFd.flush()
        if index >= iterNum:
            break
        currentRowList = latestRowList
        time.sleep(interval)
    resultFd.close()
    print("finished, quit")

def actionHueTurnon(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    testUuid =  uuid.uuid4()
    startTime = time.time()
    hueController = hue.HueController()
    lightId = 2
    for index in range(iterNum):
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        if not hueController.isLightOn(lightId):
            time.sleep(interval)
            continue
        actionTime = datetime.datetime.now()
        statStr = "testUuid: {}->actionResultObservedTime: {}->sheet".format(testUuid, actionTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        hueController.turnoffLight(lightId)
        time.sleep(interval)
    resultFd.close()

def actionHueTurnoff(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    testUuid =  uuid.uuid4()
    startTime = time.time()
    hueController = hue.HueController()
    lightId = 2
    hueController.turnonLight(lightId)
    index = 0
    while True:
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        if  hueController.isLightOn(lightId):
            print("light is one, sleep for updates")
            time.sleep(interval)
            continue
        actionTime = datetime.datetime.now()
        index += 1
        statStr = "testUuid: {}->actionResultObservedTime: {}->sheet".format(testUuid, actionTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        if index >= iterNum:
            break
        time.sleep(1)
        hueController.turnonLight(lightId)
        time.sleep(interval)
    resultFd.close()
    print("finished ,quit")

def actionSwitchTurnon(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    testUuid =  uuid.uuid4()
    startTime = time.time()
    bind = "0.0.0.0:{}".format(10085)
    switchName = "WeMo Switch"
    wemoController = wemo.WemoController(bind = bind)
    switch = wemoController.discoverSwitch(switchName)
    if switch is None:
      print("error to locate the switch")
      sys.exit(1)
    else:
      print("switch discoverred")
    #test recipe: when wemo switch is truned on, turn on lights in living room
    wemoController.turnoffSwitch(switchName)
    for index in range(iterNum):
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        if not  wemoController.isSwitchOn(switchName):
            time.sleep(interval)
            continue
        actionTime = datetime.datetime.now()
        statStr = "testUuid: {}->actionResultObservedTime: {}->sheet".format(testUuid, actionTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        wemoController.turnoffSwitch(switchName)
        time.sleep(interval)
    resultFd.close()
    pass
def actionHueBlink(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    testUuid =  uuid.uuid4()
    startTime = time.time()
    hueController = hue.HueController()
    lightId = 2
    index = 0
    while True:
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        if  not hueController.isLightAlert(lightId):
            time.sleep(interval)
            print("hue not blink, sleep for updates")
            continue
        actionTime = datetime.datetime.now()
        statStr = "testUuid: {}->actionResultObservedTime: {}->sheet".format(testUuid, actionTime.strftime(datetimeFormat))
        print(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        hueController.clearAlert(lightId)
        index += 1
        if index >= iterNum:
            break
        time.sleep(interval)
    resultFd.close()
    print("finished actions, quit")

def actionWemoLog(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    spreadsheetId = "1TwPsEXIQ0tZPnFABwKqePshDw3x0kFozaP69Nsw95ug"
    sheetName = "Sheet1"
    testUuid =  uuid.uuid4()
    startTime = time.time()
    sheetController = GoogleSheetController()
    spreadsheet = sheetController.getSpreadSheet(spreadsheetId)
    retrievedSheetName = spreadsheet["sheets"][0]["properties"]["title"]
    print("title of first sheet is ", spreadsheet["sheets"][0]["properties"]["title"])
    if retrievedSheetName != sheetName:
        print("sheet name doesn't match, use retrieved one: preconfigured one: {}, retrieved one {}".format(sheetName, retrievedSheetName))
        sheetName = retrievedSheetName
    currentRowList = sheetController.getRowList(spreadsheetId, range = sheetName)
    index = 0
    while True:
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        latestRowList = sheetController.getRowList(spreadsheetId, range = sheetName)
        actionTime = datetime.datetime.now()
        appendNum = len(latestRowList) - len(currentRowList)
        for appendIndex in range(appendNum):
            statStr = "testUuid: {}->actionResultObservedTime: {}->wemoLog".format(index, actionTime.strftime(datetimeFormat))
            print(statStr)
            resultFd.write(statStr + "\n")
            resultFd.flush()
        currentRowList = latestRowList
        index += 1
        if index >= iterNum:
            break
        time.sleep(interval)
    resultFd.close()

def actionDriveAttach(resultFile, iterNum = 100, interval = 1, timeLimit = 1000):
    resultFd = open(resultFile, "a")
    testUuid =  uuid.uuid4()
    startTime = time.time()
    parentId = "0B2Edbo2pC3d4MzEzSzRBN1BnSVU"
    driveController = GoogleDriveController()
    currentFileList = driveController.ls(parentId = parentId, isFolder = False)
    index = 0
    while True:
        currTimeCost = time.time() - startTime
        if currTimeCost > timeLimit:
            print("time out, quit")
            return
        latestFileList = driveController.ls(parentId = parentId, isFolder = False)
        actionTime = datetime.datetime.now()
        appendNum = len(latestFileList) - len(currentFileList)
        if appendNum <= 0:
            time.sleep(interval)
            continue
        for appendIndex in range(appendNum):
            statStr = "testUuid: {}->actionResultObservedTime: {}->sheet".format(testUuid, actionTime.strftime(datetimeFormat))
            print(statStr)
            resultFd.write(statStr + "\n")
            resultFd.flush()
        index += 1
        if index >= iterNum:
            break
        currentFileList = latestFileList
        time.sleep(interval)
    resultFd.close()
    print("actions finished, quit")

triggerGenerators = {
        "alexaMusic" : triggerAlexaMusic,
        "alexaBed" : triggerAlexaBed,
        "alexaSwitch": triggerAlexaSwitch,
        "newGmail" : triggerNewGmail,
        "newGmailWithAttach" : triggerNewGmailWithAttach,
        "wemo" : triggerWemoTurnon,
        }
actionMonitors = {
        "musicSheet" : actionMusicLog,
        "hueTurnon" : actionHueTurnon,
        "hueTurnoff" : actionHueTurnoff,
        "switchTurnon" : actionSwitchTurnon,
        "hueBlink" : actionHueBlink,
        "driveAttach" : actionDriveAttach,
        "wemoTurnonLog": actionWemoLog,
        }
recipeTypeDict = {
        "alexa_wemo" : (triggerAlexaSwitch, actionSwitchTurnon),
        "alexa_hue" : (triggerAlexaBed, actionHueTurnoff),
        "wemo_hue" : (triggerWemoTurnon, actionHueTurnon),
        "alexa_sheet" : (triggerAlexaMusic, actionMusicLog),
        "gmail_hue" : (triggerNewGmail, actionHueBlink),
        "wemo_sheet" : (triggerWemoTurnon, actionWemoLog),
        "gmail_drive" : (triggerNewGmailWithAttach, actionDriveAttach),
}
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("testName")
    parser.add_argument("triggerResultFile")
    parser.add_argument("actionResultFile")
    parser.add_argument("-iterNum", default = 100, type = int)
    parser.add_argument("-triggerInterval", default = 5, type = float)
    parser.add_argument("-actionInterval", default = 1, type = float)
    parser.add_argument("-timeLimit", default = 1000, type = int)
    options = parser.parse_args()
    testName = options.testName
    triggerResultFile = options.triggerResultFile
    actionResultFile  = options.actionResultFile
    iterNum = options.iterNum
    triggerInterval = options.triggerInterval
    actionInterval = options.actionInterval
    timeLimit = options.timeLimit
    if testName not in recipeTypeDict:
        print("choose from the following testNames", list(recipeTypeDict.keys()))
        sys.exit(1)
    triggerFunc, actionFunc = recipeTypeDict[testName]
    triggerProcess = Process(target = triggerFunc, args = (triggerResultFile, iterNum, triggerInterval, timeLimit))
    actionProcess = Process(target = actionFunc, args = (actionResultFile, iterNum, actionInterval, timeLimit))
    overallStartTime = time.time()
    triggerProcess.start()
    actionProcess.start()
    triggerProcess.join()
    actionProcess.join()
    overallEndTime = time.time()
    print("time cost in seconds is ", overallEndTime - overallStartTime)
