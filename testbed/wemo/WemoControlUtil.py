import os, sys, requests, json, time, argparse
from ouimeaux.environment import Environment
from ouimeaux.signals import *
class WemoController(object):
  def __init__(self, bind = "0.0.0.0:10085"):
    self.bind = bind
    self.env = Environment(with_subscribers = False,  bind=self.bind)
    self.env.start()

  def discoverSwitch(self, switchName, timeout = 10):
    startTime = time.time()
    while True:
      self.env.discover(seconds=3)
      switchList = self.env.list_switches()
      if switchName in switchList:
        return self.env.get_switch(switchName)
      currTime = time.time()
      if currTime >= startTime + timeout:
        return None
    return None
  
  def getState(self, switchName):
      result = self.isSwitchOn(switchName)
      if result == True:
          return 1
      else:
          return 0

  def setState(self, switchName, state):
      return self.setSwitchState(switchName, state)

  def setSwitchState(self, switchName, state):
    if state != 0 and state != 1:
      return False
    if switchName not in self.env.list_switches():
      switch = self.discoverSwitch(switchName)
    else:
      switch = self.env.get_switch(switchName)
    if switch is None:
      return False
    switch.basicevent.SetBinaryState(BinaryState = state)
    return True

  def turnoffSwitch(self, switchName):
    return self.setSwitchState(switchName, 0)

  def turnonSwitch(self, switchName):
    return self.setSwitchState(switchName, 1)

  def isSwitchOn(self, name):
    state = self.getSwitchState(name)
    if state is None:
      return None
    return True if state == 1 else False

  def getSwitchState(self, switchName):
    if switchName not in self.env.list_switches():
      switch = self.discoverSwitch(switchName)
    else:
      switch = self.env.get_switch(switchName)
    if switch is None:
      return None
    state = switch.get_state(force_update = True)
    return state

  

def on_switch(switch):
  print ("Switch found!", switch.name)
def on_motion(motion):
  print ("Motion found!", motion.name)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-set", action = "store_true")
  parser.add_argument("-isSub", action = "store_true")
  parser.add_argument("-port", type = int, default = 10085)
  options = parser.parse_args()
  bind = "0.0.0.0:{}".format(options.port)
  switchName = "WeMo Switch"
  wemoController = WemoController(bind = bind)
  switch = wemoController.discoverSwitch(switchName)
  if switch is None:
    print("error to locate the switch")
    sys.exit(1)
  wemoController.setSwitchState(switchName, 1)
  time.sleep(5)
  print(wemoController.getSwitchState(switchName))
  wemoController.setSwitchState(switchName, 0)
