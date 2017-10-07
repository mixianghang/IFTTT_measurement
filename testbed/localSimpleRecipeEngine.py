from hue import HueControlUtil as hue
from wemo import WemoControlUtil as wemo
from alexa import AlexaControlUtil as alexa
from googleApis.googleSheetController import GoogleSheetController
from googleApis.googleDriveController import GoogleDriveController
from googleApis.gmailController import GmailController
import time, os, sys, argparse, datetime
import shutil
import uuid
datetimeFormat = "%Y-%m-%d %H-%M-%S.%f"

#turn on hue lights when wemo switch is turned on
def testWemoHueRecipe(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile")
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-lightId", default = 2, type = int)
    parser.add_argument("-interval", default = 1, type = float)
    parser.add_argument("-wemoport", type = int, default = 10085)
    options = parser.parse_args(argv)
    resultFile = options.resultFile
    hueController = hue.HueController()
    bind = "0.0.0.0:{}".format(options.wemoport)
    switchName = "WeMo Switch"
    lightId = options.lightId
    wemoController = wemo.WemoController(bind = bind)
    switch = wemoController.discoverSwitch(switchName)
    if switch is None:
      print("error to locate the switch")
      sys.exit(1)
    else:
      print("switch discoverred")
    #test recipe: when wemo switch is truned on, turn on lights in living room
    time.sleep(3)
    resultStatList = []
    resultFd = open(resultFile, "a")
    preState = wemoController.getState(switchName)
    for index in range(options.iterNum):
        print("start test iteration {}".format(index))

        #monitor trigger event
        while (True):
            currState = wemoController.getState(switchName)
            if currState != preState and currState == 1:
                triggerObservedTime = datetime.datetime.now()
                preState = currState
                break
            preState = currState
            time.sleep(options.interval)
        hueController.turnonLight(lightId)
        print("light turned one")
        endTime = datetime.datetime.now()
        timeDiff = endTime - triggerObservedTime
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        testUuid =  uuid.uuid4()
        statStr = "executionUuid: {}->triggerObservedTime: {}->wemo_hue".format(testUuid, triggerObservedTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->actionExecutionTime: {}->wemo_hue".format(testUuid, endTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->time cost for wemo_hue iter {} is {} seconds".format(testUuid, index, timeCost)
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        time.sleep(5)
    resultFd.close()


#when any new email arrives in gmail, blink lights.
#https://ifttt.com/applets/93876p-when-any-new-email-arrives-in-gmail-blink-lights
def testGmailHueRecipe(argv):
    '''
    test the following recipe:
    If You say "Alexa trigger turn on hue light", then turn on lights in  Living room
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile")
    parser.add_argument("-iterNum", default = 5, type = int)
    #parser.add_argument("-gmailSenderName", default = "senmuxing", type = str)
    parser.add_argument("-gmailName", default = "xianghangmi", type = str)
    parser.add_argument("-lightId", default = 2, type = int)
    parser.add_argument("-interval", default = 0.1, type = float)
    options = parser.parse_args(argv)
    hueController = hue.HueController()
    lightId = options.lightId
    gmailController = GmailController(options.gmailName)
    resultStatList = []
    resultFd = open(options.resultFile, "a")
    #test recipe: when wemo switch is truned on, turn on lights in living room
    preMsgList = gmailController.listMessagesMatchingQuery()
    for index in range(options.iterNum):
        #check new emails
        #hueController.clearAlert(lightId)
        nowDate = datetime.datetime.now()
        nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
        #detect reception of the email
        while True:
            latestMsgList = gmailController.listMessagesMatchingQuery()
            latestMsgId = latestMsgList[0]["id"]
            preMsgId = preMsgList[0]["id"]
            if latestMsgId == preMsgId:
                time.sleep(options.interval)
                continue
            else:
                preMsgList = latestMsgList
                triggerObservedTime = datetime.datetime.now()
                break
        print("receive email at ", triggerObservedTime.strftime("%Y-%m-%d %H-%M-%S"))
        hueController.alertLight(lightId)
        endTime = datetime.datetime.now()
        timeDiff = endTime - triggerObservedTime
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        testUuid =  uuid.uuid4()
        statStr = "testUuid: {}->triggerObservedTime: {}->gmail_hue".format(testUuid, triggerObservedTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->actionExecutionTime: {}->gmail_hue".format(testUuid, endTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->time cost for iter {} is {} seconds".format(testUuid, index, timeCost)
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
    resultFd.close()
    open(options.resultFile, "w").write("\n".join(resultStatList) + "\n")

#if my wemo switch is activated, add line to spreadsheet
#https://ifttt.com/applets/67307p-if-my-wemo-switch-is-activated-add-line-to-spreadsheet
def testWemoGoogleSheetRecipe(argv):
    '''
    test the following recipe:
    If You say "Alexa trigger turn on hue light", then turn on lights in  Living room
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile")
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-interval", default = 1, type = float)
    parser.add_argument("-wemoport", type = int, default = 10085)
    spreadsheetId = "1TwPsEXIQ0tZPnFABwKqePshDw3x0kFozaP69Nsw95ug"
    sheetName = "Sheet1"
    options = parser.parse_args(argv)
    bind = "0.0.0.0:{}".format(options.wemoport)
    switchName = "WeMo Switch"
    wemoController = wemo.WemoController(bind = bind)
    switch = wemoController.discoverSwitch(switchName)
    if switch is None:
      print("error to locate the switch")
      sys.exit(1)
    else:
      print("switch discoverred")
    sheetController = GoogleSheetController()
    spreadsheet = sheetController.getSpreadSheet(spreadsheetId)
    print("got spreadsheet: ",  sheetController.getSpreadSheet(spreadsheetId))
    retrievedSheetName = spreadsheet["sheets"][0]["properties"]["title"]
    print("title of first sheet is ", spreadsheet["sheets"][0]["properties"]["title"])
    if retrievedSheetName != sheetName:
        print("sheet name doesn't match, use retrieved one: preconfigured one: {}, retrieved one {}".format(sheetName, retrievedSheetName))
        sheetName = retrievedSheetName
    resultStatList = []
    resultFd = open(options.resultFile, "a")
    #test recipe: when wemo switch is truned on, write a log to the google spreadsheet
    preSwitchState = wemoController.getState(switchName)
    for index in range(options.iterNum):
        while True:
          currSwitchState = wemoController.getState(switchName)
          if currSwitchState == 1 and currSwitchState != preSwitchState:
            preSwitchState = currSwitchState
            triggerObservedTime = datetime.datetime.now()
            break
          preSwitchState = currSwitchState
          time.sleep(options.interval)

        print("switch turned on is observed")
        nowDate = datetime.datetime.now()
        nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
        values = [
              ["switch turned on", nowStr],
            ]
        responseAppend = sheetController.appendFile(spreadsheetId, range = "Sheet1", valueList = values)
        endTime = datetime.datetime.now()
        timeDiff = endTime - triggerObservedTime
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        testUuid =  uuid.uuid4()
        statStr = "testUuid: {}->triggerObservedTime: {}->wemo_sheet".format(testUuid, triggerObservedTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->actionExecutionTime: {}->wemo_sheet".format(testUuid, endTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->time cost for iter {} is {} seconds".format(testUuid, index, timeCost)
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        #generate trigger event: speak to alexa: change a music
    resultFd.close()
    print(resultStatList)

#automatically save new email attachments in gmail to google drive
#https://ifttt.com/applets/99068p-automatically-save-new-email-attachments-in-gmail-to-google-drive
def testGmailDrive(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile")
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-interval", default = 0.1, type = float)
    parser.add_argument("-gmailName", default = "xianghangmi", type = str)
    parentId = "0B2Edbo2pC3d4MzEzSzRBN1BnSVU"
    options = parser.parse_args(argv)
    gmailController = GmailController(options.gmailName)
    driveController = GoogleDriveController()
    resultStatList = []
    resultFd = open(options.resultFile, "a")
    for index in range(options.iterNum):
        preMsgList = gmailController.listMessagesMatchingQuery()
        nowDate = datetime.datetime.now()
        nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
        #send email from senmuxing@gmail.com to xianghangmi@gmail.com
        subject = "ifttt test at {}".format(nowStr)
        tempFile = "ifttTest_engine_{}.txt".format(nowStr)
        open(tempFile, "w").write(subject)

        #detect reception of the email
        while True:
            latestMsgList = gmailController.listMessagesMatchingQuery()
            latestMsgId = latestMsgList[0]["id"]
            preMsgId = preMsgList[0]["id"]
            if latestMsgId == preMsgId:
                time.sleep(options.interval)
                continue
            else:
                preMsgList = latestMsgList
                triggerObservedTime = datetime.datetime.now()
                break
        driveController.uploadFile(tempFile, tempFile, dstParentList = [ parentId ])
        endTime = datetime.datetime.now()
        timeDiff = endTime - triggerObservedTime
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        testUuid =  uuid.uuid4()
        statStr = "testUuid: {}->triggerObservedTime: {}->gmail_drive".format(testUuid, triggerObservedTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->actionExecutionTime: {}->gmail_drive".format(testUuid, endTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->time cost for iter {} is {} seconds".format(testUuid, index, timeCost)
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        os.remove(tempFile)
        time.sleep(10)
    print(resultStatList)
    resultFd.close()
recipeTypeDict = {
        #"alexa_wemo" : testAlexaWemoRecipe,
        #"alexa_hue" : testAlexaHueRecipe,
        "wemo_hue" : testWemoHueRecipe,
        #"alexa_sheet" : testAlexaGoogleSheetRecipe,
        "gmail_hue" : testGmailHueRecipe,
        "wemo_sheet" : testWemoGoogleSheetRecipe,
        "gmail_drive" : testGmailDrive,
}
if __name__ == "__main__":
    recipeName = sys.argv[1]
    print(recipeName)
    if recipeName not in recipeTypeDict:
      print("please provide recipeType from this list: ", recipeTypeDict.keys())
      sys.exit(1)
    recipeFunc = recipeTypeDict[recipeName]
    recipeFunc(sys.argv[2:])
