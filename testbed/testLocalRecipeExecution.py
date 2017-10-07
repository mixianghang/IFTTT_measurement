from hue import HueControlUtil as hue
from wemo import WemoControlUtil as wemo
from alexa import AlexaControlUtil as alexa
import time, os, sys, argparse, datetime
def testWemoHueLocalRecipe(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-iterNum", default = 5, type = int)
    parser.add_argument("-lightId", default = 2, type = int)
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
    for index in range(options.iterNum):
      print("start test iteration {}".format(index))
      hueController.turnoffLight(lightId)
      wemoController.turnoffSwitch(switchName)

      #generate trigger event: turn on switch
      wemoController.turnonSwitch(switchName)
      print("switch turned one")
      startTime = datetime.datetime.now()
      while (True):
        if hueController.isLightOn(lightId):
          break
        time.sleep(0.5)
      endTime = datetime.datetime.now()
      timeDiff = endTime - startTime
      print("time cost for iter {} is {} seconds and microseconds {}".format(index, timeDiff.seconds, timeDiff.microseconds))
      print("sleep before next test")
      time.sleep(5)
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
}
if __name__ == "__main__":
    recipeName = sys.argv[1]
    if recipeName not in recipeTypeDict:
      print("please provide recipeType from this list: ", recipeTypeDict)
      sys.exit(1)
    recipeFunc = recipeTypeDict[recipeName]
    recipeFunc(sys.argv[2:])
