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
#turn on lights connected to wemo smart plug
#https://ifttt.com/applets/346650p-amazon-echo-turn-on-light-connected-to-wemo-switch
def testAlexaWemoRecipe(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile")
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-wemoport", type = int, default = 10085)
    parser.add_argument("-interval", default = 0.1, type = float)
    options = parser.parse_args(argv)
    audioFile = "alexa/audioFiles/AlexaTriggerTurnOnSwitch.wav"
    alexaController = alexa.AlexaController()
    bind = "0.0.0.0:{}".format(options.wemoport)
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
    time.sleep(3)
    resultStatList = []
    for index in range(options.iterNum):
        print("start test iteration {}".format(index))
        alexaController.saySomething(audioFile)
        print("alexa phrase said")
        startTime = datetime.datetime.now()
        while (True):
            if wemoController.isSwitchOn(switchName):
              break
            time.sleep(options.interval)
        endTime = datetime.datetime.now()
        timeDiff = endTime - startTime
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        statStr = "time cost for iter {} is {} seconds".format(index, timeCost)
        print(statStr)
        resultStatList.append(statStr)
        wemoController.turnoffSwitch(switchName)
        print("sleep before next test")
        time.sleep(5)
    open(options.resultFile, "w").write("\n".join(resultStatList) + "\n")

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
    hueController.turnonLight(lightId)
    time.sleep(3)
    resultStatList = []
    resultFd = open(resultFile, "a")
    for index in range(options.iterNum):
        print("start test iteration {}".format(index))
        hueController.turnoffLight(lightId)
        wemoController.turnoffSwitch(switchName)
        time.sleep(3)

        #generate trigger event: turn on switch
        wemoController.turnonSwitch(switchName)
        print("switch turned one")
        triggerGeneratedTime = datetime.datetime.now()
        startTime = datetime.datetime.now()
        while (True):
            if hueController.isLightOn(lightId):
              break
            time.sleep(options.interval)
        endTime = datetime.datetime.now()
        timeDiff = endTime - startTime
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        testUuid =  uuid.uuid4()
        statStr = "testUuid: {}->triggerGeneratedTime: {}->wemo_hue".format(testUuid, triggerGeneratedTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->actionResultObservedTime: {}->wemo_hue".format(testUuid, endTime.strftime(datetimeFormat))
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
    hueController.turnoffLight(lightId)
    wemoController.turnoffSwitch(switchName)
#trigger bedtime: turn off hue lights in the living room
#applet url: https://ifttt.com/applets/342115p-turn-lights-out-for-bed-with-alexa-and-hue
def testAlexaHueRecipe(argv):
    '''
    test the following recipe:
    If You say "Alexa trigger turn on hue light", then turn on lights in  Living room
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile")
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-lightId", default = 2, type = int)
    parser.add_argument("-interval", default = 0.1, type = float)
    audioFile = "alexa/audioFiles/alexa_trigger_bedtime.wav"
    options = parser.parse_args(argv)
    hueController = hue.HueController()
    lightId = options.lightId
    alexaController = alexa.AlexaController()
    resultStatList = []
    #test recipe: when wemo switch is truned on, turn on lights in living room
    for index in range(options.iterNum):
        time.sleep(5)
        hueController.turnonLight(lightId)

        #generate trigger event: speak to alexa: turn on hue light
        alexaController.saySomething(audioFile = audioFile)
        print("send out voice command to alexa")
        startTime = datetime.datetime.now()
        while (True):
            if not hueController.isLightOn(lightId):
              break
            time.sleep(options.interval)
        endTime = datetime.datetime.now()
        timeDiff = endTime - startTime
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        statStr = "time cost for iter {} is {} seconds".format(index, timeCost)
        print(statStr)
        resultStatList.append(statStr)
    open(options.resultFile, "w").write("\n".join(resultStatList) + "\n")

#test alexa and google sheet applet
#Keep a Google spreadsheet of the songs you listen to on Alexa
#sheetId : 1M8uG1TwVg53hXbaluqLspYXoxPf0PhibyH-bEHCo96o
#https://ifttt.com/applets/298147p-keep-a-google-spreadsheet-of-the-songs-you-listen-to-on-alexa
def testAlexaGoogleSheetRecipe(argv):
    '''
    test the following recipe:
    If You say "Alexa trigger turn on hue light", then turn on lights in  Living room
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile")
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-interval", default = 0.5, type = float)
    playAudioFile = "alexa/audioFiles/playMusic.wav"
    changeAudioFile = "alexa/audioFiles/alexaNextMusic.wav"
    spreadsheetId = "1M8uG1TwVg53hXbaluqLspYXoxPf0PhibyH-bEHCo96o"
    sheetName = "Sheet1"
    options = parser.parse_args(argv)
    alexaController = alexa.AlexaController()
    sheetController = GoogleSheetController()
    spreadsheet = sheetController.getSpreadSheet(spreadsheetId)
    print("got spreadsheet: ",  sheetController.getSpreadSheet(spreadsheetId))
    retrievedSheetName = spreadsheet["sheets"][0]["properties"]["title"]
    print("title of first sheet is ", spreadsheet["sheets"][0]["properties"]["title"])
    if retrievedSheetName != sheetName:
        print("sheet name doesn't match, use retrieved one: preconfigured one: {}, retrieved one {}".format(sheetName, retrievedSheetName))
        sheetName = retrievedSheetName
    currentRowList = sheetController.getRowList(spreadsheetId, range = sheetName)
    resultStatList = []
    alexaController.saySomething(playAudioFile)
    #test recipe: when wemo switch is truned on, turn on lights in living room
    for index in range(options.iterNum):
        startTime = datetime.datetime.now()
        while (True):
            latestRowList = sheetController.getRowList(spreadsheetId, range = sheetName)
            if len(latestRowList) > len(currentRowList):
                print(currentRowList[-1])
                currentRowList = latestRowList
                break
            time.sleep(options.interval)
        endTime = datetime.datetime.now()
        timeDiff = endTime - startTime
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        statStr = "time cost for iter {} is {} seconds".format(index, timeCost)
        print(statStr)
        resultStatList.append(statStr)
        #generate trigger event: speak to alexa: change a music
        alexaController.saySomething(changeAudioFile)
        print("send out voice command to alexa")
    open(options.resultFile, "w").write("\n".join(resultStatList) + "\n")


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
    parser.add_argument("-gmailSenderName", default = "senmuxing", type = str)
    parser.add_argument("-gmailName", default = "xianghangmi", type = str)
    parser.add_argument("-lightId", default = 2, type = int)
    parser.add_argument("-interval", default = 0.1, type = float)
    options = parser.parse_args(argv)
    hueController = hue.HueController()
    lightId = options.lightId
    gmailController = GmailController(options.gmailName)
    gmailSenderController = GmailController(options.gmailSenderName)
    resultStatList = []
    hueController.turnoffLight(lightId)
    resultFd = open(options.resultFile, "a")
    #test recipe: when wemo switch is truned on, turn on lights in living room
    for index in range(options.iterNum):
        time.sleep(10)
        preMsgList = gmailController.listMessagesMatchingQuery()
        nowDate = datetime.datetime.now()
        nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
        #send email from senmuxing@gmail.com to xianghangmi@gmail.com
        subject = "ifttt test at {}".format(nowStr)
        messageBody = subject
        message = GmailController.create_message(sender = "senmuxing@gmail.com", to = "xianghangmi@gmail.com", subject = subject, message_text = messageBody)
        gmailSenderController.sendMessage(message)
        sentTime = datetime.datetime.now()
        print("sent email at ", sentTime.strftime("%Y-%m-%d %H-%M-%S"))

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
                receiveTime = datetime.datetime.now()
                break
        print("receive email at ", receiveTime.strftime("%Y-%m-%d %H-%M-%S"))
        triggerGeneratedTime = datetime.datetime.now()
        while (True):
            if hueController.isLightAlert(lightId):
                hueController.clearAlert(lightId)
                break
            time.sleep(options.interval)
        endTime = datetime.datetime.now()
        timeDiffSent =  receiveTime - sentTime
        timeDiff = endTime - sentTime
        timeCostForSend = timeDiffSent.seconds + timeDiffSent.microseconds / float(1000000)
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        testUuid =  uuid.uuid4()
        statStr = "testUuid: {}->triggerGeneratedTime: {}->gmail_hue".format(testUuid, triggerGeneratedTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->actionResultObservedTime: {}->gmail_hue".format(testUuid, endTime.strftime(datetimeFormat))
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

#when any new email arrives in gmail, blink lights.
#https://ifttt.com/applets/93876p-when-any-new-email-arrives-in-gmail-blink-lights
def testGmailHueWemoRecipe(argv):
    '''
    test the following recipe:
    If You say "Alexa trigger turn on hue light", then turn on lights in  Living room
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile")
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-gmailSenderName", default = "senmuxing", type = str)
    parser.add_argument("-gmailName", default = "xianghangmi", type = str)
    parser.add_argument("-lightId", default = 2, type = int)
    parser.add_argument("-interval", default = 1, type = float)
    parser.add_argument("-wemoport", type = int, default = 10085)
    options = parser.parse_args(argv)
    hueController = hue.HueController()
    lightId = options.lightId
    gmailController = GmailController(options.gmailName)
    gmailSenderController = GmailController(options.gmailSenderName)
    bind = "0.0.0.0:{}".format(options.wemoport)
    switchName = "WeMo Switch"
    wemoController = wemo.WemoController(bind = bind)
    switch = wemoController.discoverSwitch(switchName)
    if switch is None:
      print("error to locate the switch")
      sys.exit(1)
    else:
      print("switch discoverred")
    resultStatList = []
    hueController.turnoffLight(lightId)
    resultFd = open(options.resultFile, "a")
    #test recipe: when wemo switch is truned on, turn on lights in living room
    for index in range(options.iterNum):
        time.sleep(5)
        hueController.clearAlert(lightId)
        wemoController.turnoffSwitch(switchName)
        preMsgList = gmailController.listMessagesMatchingQuery()
        nowDate = datetime.datetime.now()
        nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
        #send email from senmuxing@gmail.com to xianghangmi@gmail.com
        subject = "ifttt test at {}".format(nowStr)
        messageBody = subject
        message = GmailController.create_message(sender = "senmuxing@gmail.com", to = "xianghangmi@gmail.com", subject = subject, message_text = messageBody)
        gmailSenderController.sendMessage(message)
        sentTime = datetime.datetime.now()
        print("sent email at ", sentTime.strftime("%Y-%m-%d %H-%M-%S"))
        triggerGeneratedTime = datetime.datetime.now()

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
                receiveTime = datetime.datetime.now()
                break
        print("receive email at ", receiveTime.strftime("%Y-%m-%d %H-%M-%S"))
        actionHue = False
        actionWemo = False
        actionHueTime = None
        actionWemoTime = None
        while (True):
            if actionHue == False and hueController.isLightAlert(lightId):
                print("got hue action")
                hueController.clearAlert(lightId)
                actionHueTime = datetime.datetime.now()
                actionHue = True
            if actionWemo == False and wemoController.isSwitchOn(switchName):
                actionWemo = True
                print("got wemo action")
                actionWemoTime = datetime.datetime.now()
                wemoController.turnoffSwitch(switchName)
            if actionHue and  actionWemo:
                break
            time.sleep(options.interval)
        endTime = datetime.datetime.now()
        timeDiffSent =  receiveTime - sentTime
        timeDiff = endTime - sentTime
        timeCostForSend = timeDiffSent.seconds + timeDiffSent.microseconds / float(1000000)
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        testUuid =  uuid.uuid4()
        statStr = "1testUuid: {}->triggerGeneratedTime: {}->gmail".format(index, triggerGeneratedTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "2testUuid: {}->actionResultObservedTime: {}->hue".format(index, actionHueTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        statStr = "3testUuid: {}->actionResultObservedTime: {}->wemo".format(index, actionWemoTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

    resultFd.close()

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
    currentRowList = sheetController.getRowList(spreadsheetId, range = sheetName)
    print("current row list", currentRowList)
    resultStatList = []
    wemoController.turnoffSwitch(switchName)
    resultFd = open(options.resultFile, "a")
    #test recipe: when wemo switch is truned on, write a log to the google spreadsheet
    for index in range(options.iterNum):
        time.sleep(5)
        wemoController.turnonSwitch(switchName)
        triggerGeneratedTime = datetime.datetime.now()
        print("switch turned on")
        startTime = datetime.datetime.now()
        while (True):
            latestRowList = sheetController.getRowList(spreadsheetId, range = sheetName)
            if latestRowList is not None and len(latestRowList) > len(currentRowList):
                print(latestRowList[-1])
                currentRowList = latestRowList
                break
            if latestRowList is None:
                print("error when requesting latest row list")
            time.sleep(options.interval)
        endTime = datetime.datetime.now()
        timeDiff = endTime - startTime
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        testUuid =  uuid.uuid4()
        statStr = "testUuid: {}->triggerGeneratedTime: {}->wemo_sheet".format(testUuid, triggerGeneratedTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->actionResultObservedTime: {}->wemo_sheet".format(testUuid, endTime.strftime(datetimeFormat))
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()

        statStr = "testUuid: {}->time cost for iter {} is {} seconds".format(testUuid, index, timeCost)
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        wemoController.turnoffSwitch(switchName)
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
    parser.add_argument("-gmailSenderName", default = "senmuxing", type = str)
    parser.add_argument("-gmailName", default = "xianghangmi", type = str)
    parentId = "0B2Edbo2pC3d4MzEzSzRBN1BnSVU"
    options = parser.parse_args(argv)
    gmailController = GmailController(options.gmailName)
    gmailSenderController = GmailController(options.gmailSenderName)
    driveController = GoogleDriveController()
    resultStatList = []
    resultFd = open(options.resultFile, "a")
    for index in range(options.iterNum):
        preMsgList = gmailController.listMessagesMatchingQuery()
        preFileList = driveController.ls(parentId = parentId, isFolder = False)
        print("pre File list is ", preFileList)
        nowDate = datetime.datetime.now()
        nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
        #send email from senmuxing@gmail.com to xianghangmi@gmail.com
        subject = "ifttt test at {}".format(nowStr)
        tempFile = "ifttTest_{}.txt".format(nowStr)
        open(tempFile, "w").write(subject)
        messageBody = subject
        message = GmailController.create_message_with_attachment(sender = "senmuxing@gmail.com", to = "xianghangmi@gmail.com", subject = subject, message_text = messageBody, file = tempFile)
        gmailSenderController.sendMessage(message)
        sentTime = datetime.datetime.now()

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
                receiveTime = datetime.datetime.now()
                break
        #detect new attachments
        while True:
            currentFileList = driveController.ls(parentId = parentId, isFolder = False)
            if len(currentFileList) != len(preFileList):
                print("current File list is ", currentFileList)
                break
            else:
                time.sleep(options.interval)
        endTime = datetime.datetime.now()
        timeDiffSent =  receiveTime - sentTime
        timeDiff = endTime - sentTime
        timeCostForSend = timeDiffSent.seconds + timeDiffSent.microseconds / float(1000000)
        timeCost = timeDiff.seconds + timeDiff.microseconds / float(1000000)
        statStr = "time cost for iter {} is send {} seconds and  applet  {} seconds".format(index, timeCostForSend, timeCost)
        print(statStr)
        resultStatList.append(statStr)
        resultFd.write(statStr + "\n")
        resultFd.flush()
        os.remove(tempFile)
        time.sleep(10)
    #print(resultStatList)
    resultFd.close()

recipeTypeDict = {
        "alexa_wemo" : testAlexaWemoRecipe,
        "alexa_hue" : testAlexaHueRecipe,
        "wemo_hue" : testWemoHueRecipe,
        "alexa_sheet" : testAlexaGoogleSheetRecipe,
        "gmail_hue" : testGmailHueRecipe,
        "gmail_hue_wemo" : testGmailHueWemoRecipe,
        "wemo_sheet" : testWemoGoogleSheetRecipe,
        "gmail_drive" : testGmailDrive,
}
if __name__ == "__main__":
    recipeName = sys.argv[1]
    print(recipeName)
    print("niaho")
    if recipeName not in recipeTypeDict:
      print("please provide recipeType from this list: ", recipeTypeDict.keys())
      sys.exit(1)
    recipeFunc = recipeTypeDict[recipeName]
    recipeFunc(sys.argv[2:])
