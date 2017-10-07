from hue import HueControlUtil as hue
from wemo import WemoControlUtil as wemo
from alexa import AlexaControlUtil as alexa
import time, os, sys, argparse, datetime
from threading import Thread
class BurstWemoThread(Thread):
    def __init__(self, wemoController, switchName,  interval = 10):
        self.switchName = switchName
        self.wemoController = wemoController
        self.interval = interval
        self.isStop = False
        self.triggerList = []
        super().__init__()

    def run(self):
        while not self.isStop:
            self.wemoController.turnonSwitch(self.switchName)
            timeStamp = datetime.datetime.now()
            timeStr = timeStamp.strftime("%Y-%m-%d %H:%M:%S:%f")
            self.triggerList.append((timeStamp, timeStr, "trigger"))
            print("new trigger at {}".format(timeStr))
            time.sleep(1)
            self.wemoController.turnoffSwitch(self.switchName)
            time.sleep(self.interval)
def testWemoWebRecipe(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile", type = str)
    parser.add_argument("-timeLimit", default = 50, type = int)
    parser.add_argument("-triggerInterval", default = 1, type = int)
    parser.add_argument("-wemoport", type = int, default = 10085)
    options = parser.parse_args(argv)
    bind = "0.0.0.0:{}".format(options.wemoport)
    switchName = "WeMo Switch1"
    wemoController = wemo.WemoController(bind = bind)
    switch = wemoController.discoverSwitch(switchName)
    if switch is None:
      print("error to locate the switch")
      sys.exit(1)
    else:
      print("switch discoverred")
    #test recipe: when wemo switch is truned on, turn on lights in living room
    switchThread = BurstWemoThread(wemoController, switchName, interval = options.triggerInterval)
    switchThread.start()
    actionBurstList = []
    startTime = time.time()
    while True:
      currTime = time.time()
      if currTime >= startTime + options.timeLimit:
        break
      time.sleep(1)
    switchThread.isStop = True
    switchThread.join()
    eventList = []
    eventList.extend(switchThread.triggerList)
    sortedEventList = sorted(eventList, key = lambda item : item[0])
    with open(options.resultFile, mode = "w", encoding = "utf-8") as fd:
        for event in sortedEventList:
            timeStr = event[1]
            type = event[2]
            fd.write("{}: {}\n".format(type, timeStr))

def testWemoHueRecipe(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("resultFile", type = str)
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-actionDuration", default = 10, type = int)
    parser.add_argument("-triggerInterval", default = 10, type = int)
    parser.add_argument("-lightId", default = 2, type = int)
    parser.add_argument("-actionInterval", default = 0.5, type = float)
    parser.add_argument("-wemoport", type = int, default = 10085)
    options = parser.parse_args(argv)
    hueController = hue.HueController()
    bind = "0.0.0.0:{}".format(options.wemoport)
    switchName = "WeMo Switch1"
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
    hueController.turnoffLight(lightId)
    switchThread = BurstWemoThread(wemoController, switchName, interval = options.triggerInterval)
    switchThread.start()
    actionBurstList = []
    for index in range(options.iterNum):
      print("start test iteration {}".format(index))
      oneBurst = []
      hueController.turnoffLight(lightId)
      overallStartTime = datetime.datetime.now()
      lastTime = None
      while (True):
        if lastTime != None:
            timeDiff = datetime.datetime.now() - lastTime
            if timeDiff.seconds >= options.actionDuration:
                burstEndTime = lastTime
                break
        if hueController.isLightOn(lightId):
          actionTime = datetime.datetime.now()
          timeStr = actionTime.strftime("%Y-%M-%d %H:%M:%S:%f")
          print("new action at time ", timeStr)
          oneBurst.append((actionTime, timeStr, "action"))
          if lastTime is None:
              burstStartTime = actionTime
          lastTime = actionTime
          hueController.turnoffLight(lightId)
        time.sleep(options.actionInterval)
      overallEndTime = datetime.datetime.now()
      overallTimeDiff = overallEndTime - overallStartTime
      overallTimeDiff = overallTimeDiff.seconds + overallTimeDiff.microseconds / 1000000
      burstDuration = burstEndTime - burstStartTime
      burstDuration = burstDuration.seconds + burstDuration.microseconds / 1000000
      actionBurstList.append((oneBurst, overallTimeDiff, burstDuration))
      print("iteration: {}, overall: {:.2f} seconds, burst: {:.2f} seconds, actions: {}".format(index, overallTimeDiff, burstDuration, len(oneBurst)) )
    switchThread.isStop = True
    switchThread.join()
    eventList = []
    for burstTuple in actionBurstList:
        burst = burstTuple[0]
        for action in burst:
            eventList.append(action)
    eventList.extend(switchThread.triggerList)
    sortedEventList = sorted(eventList, key = lambda item : item[0])
    with open(options.resultFile, mode = "w", encoding = "utf-8") as fd:
        for event in sortedEventList:
            timeStr = event[1]
            type = event[2]
            fd.write("{}: {}\n".format(type, timeStr))

def testAlexaHueRecipe(argv):
    '''
    test the following recipe:
    If You say "Alexa trigger turn on hue light", then turn on lights in  Living room
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-lightId", default = 2, type = int)
    options = parser.parse_args(argv)
    hueController = hue.HueController()
    lightId = options.lightId
    alexaController = alexa.AlexaController()
    #test recipe: when wemo switch is truned on, turn on lights in living room
    for index in range(options.iterNum):
      hueController.turnoffLight(lightId)

      #generate trigger event: speak to alexa: turn on hue light
      alexaController.turnonHueLight()
      print("send out voice command to alexa")
      startTime = datetime.datetime.now()
      while (True):
        if hueController.isLightOn(lightId):
          break
        time.sleep(0.1)
      endTime = datetime.datetime.now()
      timeDiff = endTime - startTime
      print("time cost for iter {} is {} seconds and microseconds {}".format(index, timeDiff.seconds, timeDiff.microseconds))
recipeTypeDict = {
    "alexaHue" : testAlexaHueRecipe,
    "wemoHue" : testWemoHueRecipe,
    "wemoWeb" : testWemoWebRecipe,
}
if __name__ == "__main__":
    recipeName = sys.argv[1]
    if recipeName not in recipeTypeDict:
      print("please provide recipeType from this list: ", recipeTypeDict)
      sys.exit(1)
    recipeFunc = recipeTypeDict[recipeName]
    recipeFunc(sys.argv[2:])
