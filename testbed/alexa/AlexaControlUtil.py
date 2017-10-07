import os, sys, requests, json, time, subprocess

class AlexaController(object):
  '''
  1.pyaudio provides low level apis to play and record audio, we may leverage it to provide more functions
  2. sox can be used to record and play audio on mac
  '''
  def __init__(self): 
    self.name = "alexaController"
    self.dir = os.path.dirname(os.path.abspath(__file__))
    self.defaultTurnOnHueLightCommand = self.dir + "/turnonHueLight.wav"
    self.defaultTurnOffHueLightCommand = self.dir + "/turnoffHueLight.wav"
    self.defaultTurnOnWemoSwitchCommand = self.dir + "/wemoTurnon.wav"
    self.defaultTurnOffWemoSwitchCommand = self.dir + "/wemoTurnoff.wav"
  def playCommand(self, audioFile):
    if sys.platform == "linux2":
      commandList = ["xdg-open", audioFile]
    elif sys.platform == "darwin":
      commandList = ["afplay", audioFile]
    subprocess.run(args = commandList)
  def recordCommand(self, resultFile):
    pass
  def turnonHueLight(self, audioFile = None):
    if audioFile is None:
      audioFile = self.defaultTurnOnHueLightCommand
    self.playCommand(audioFile)

  def saySomething(self, audioFile):
    self.playCommand(audioFile)

  def turnoffHueLight(self, audioFile = None):
    if audioFile is None:
      audioFile = self.defaultTurnOffHueLightCommand
    self.playCommand(audioFile)

  def turnoffWemoSwitch(self, audioFile = None):
    if audioFile is None:
      audioFile = self.defaultTurnOffWemoSwitchCommand
    self.playCommand(audioFile)

  def turnonWemoSwitch(self, audioFile = None):
    if audioFile is None:
      audioFile = self.defaultTurnOnWemoSwitchCommand
    self.playCommand(audioFile)


if __name__ == "__main__":
  controller = AlexaController()
  #controller.playCommand("playMusic.wav")
  controller.turnonHueLight()
