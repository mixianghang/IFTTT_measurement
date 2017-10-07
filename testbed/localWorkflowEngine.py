#!/usr/bin/env python3
from hue import HueControlUtil as hue
from wemo import WemoControlUtil as wemo
from alexa import AlexaControlUtil as alexa
import time, os, sys, argparse
from datetime import datetime

class Recipe(object):
    def __init__(self):
        pass
    def run(self):
        pass
    def getTriggerState(self):
        pass
    def executeAction(self):
        pass
class WemoHueRecipe(Recipe):
    def __init__(self, wemoController, hueController, switchName, lightId):
        self.wemoController = wemoController
        self.hueController = hueController
        self.lightId = lightId
        self.switchName = switchName
        self.triggerStateList = [(self.wemoController.getSwitchState(switchName), datetime.now())]
        print("triggerState", self.triggerStateList)
        self.eventList = []
        self.queueSize = 50
    def run(self):
        newState = self.wemoController.getSwitchState(self.switchName)
        if newState == self.triggerStateList[-1][0]:
            return
        self.triggerStateList.append((newState, datetime.now()))
        print("triggerStateList", self.triggerStateList)
        if newState == 1:
            print("execute action")
            self.hueController.turnonLight(self.lightId)
            self.eventList.append(datetime.now())
        if len(self.triggerStateList) == self.queueSize:
            self.triggerStateList.pop(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-lightId", default = 2, type = int)
    parser.add_argument("-sleep", default = 1, type = float)
    parser.add_argument("-wemoport", type = int, default = 10085)
    options = parser.parse_args()
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
    recipe = WemoHueRecipe(wemoController, hueController, switchName, lightId)
    recipeList = [recipe]
    while True:
        time.sleep(options.sleep)
        for recipe in recipeList:
            recipe.run()
