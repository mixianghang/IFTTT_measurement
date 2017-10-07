import logging
import sys, os
import re
import argparse
labelSize = 20
legendSize = 20
titleSize = 36

def drawLine(xList, yList, resultFile, legends = None, xLabel = None, yLabel = None, title = None, colorList = None, opacity = 0.6, xRange = None, yRange = None, marker = "o"):

  import matplotlib
  #matplotlib.use('Agg')
  import  matplotlib.pyplot as plt
  logger = logging.getLogger(__name__)
  #figure = plt.figure(1)
  figure, axis = plt.subplots()
  #axis.spines['right'].set_visible(False)
  #axis.spines['top'].set_visible(False)
  axis.tick_params(labeltop='off', labelright='off')
  #plot lines
  lineObjList = []
  for xSubList, ySubList in zip(xList, yList):
    lineObj = plt.plot(xSubList, ySubList)
    lineObj[0].set_alpha(opacity)
    lineObj[0].set_marker(marker)
    lineObjList.append(lineObj[0])
  if colorList is not None:
    for lineObj, color in zip(lineObjList, colorList):
      lineObj.set_color(color)
  logger.info("%d lines drawn", len(lineObjList))
  #set up min/max of axixes
  if xRange is not None:
    plt.xlim(xRange)
  if yRange is not None:
    plt.ylim(yRange)
  #set up labels of x and yaxis
  if xLabel is not None:
    plt.xlabel(xLabel, fontsize = labelSize)
  if yLabel is not None:
    plt.ylabel(yLabel, fontsize = labelSize)
  #set up title
  if title is not None:
    plt.title(title, fontsize = titleSize)
  #set up legends
  if legends is not None:
    plt.legend(lineObjList, legends, fontsize = legendSize)
  #save to file
  figure.savefig(resultFile + ".pdf", format = "pdf")
  figure.savefig(resultFile + ".png", format = "png")
  plt.clf()

if __name__ == "__main__":
  parser = argparse.ArgumentParser("reliability plot")
  parser.add_argument("lightSourceFile", type = str)
  parser.add_argument("switchSourceFile", type = str)
  parser.add_argument("resultDir", type = str)
  parser.add_argument("-startDate", type = int, default = 20170514)
  parser.add_argument("-endDate", type = int, default = 20170517)
  options = parser.parse_args()
  lightSourceFile = options.lightSourceFile
  switchSourceFile = options.switchSourceFile
  resultDir = options.resultDir
  startDate = options.startDate
  endDate = options.endDate
  if not os.path.exists(resultDir):
    os.makedirs(resultDir)
  lightResultFile = os.path.join(resultDir, "light_{}_{}.txt".format(startDate, endDate))
  switchResultFile = os.path.join(resultDir, "switch_{}_{}.txt".format(startDate, endDate))
  plotResultFile = os.path.join(resultDir, "switch_light_{}_{}_plot.txt".format(startDate, endDate))
  lineRe = re.compile("./ifttt_access_(\d+)_(\d+)\.log:(\d+)", re.I)
  lightResultList = []
  switchResultList = []
  with open(lightSourceFile, "r") as fd:
    for line in fd:
      matchObj =  lineRe.match(line.strip())
      if matchObj is None:
        print("error when paring line: ", line.strip())
        sys.exit(1)
      currDate = int(matchObj.group(1))
      if currDate < startDate or currDate > endDate:
        continue
      currHour = int(matchObj.group(2))
      pollNum  = int(matchObj.group(3))
      lightResultList.append((currDate, currHour, pollNum))
  with open(switchSourceFile, "r") as fd:
    for line in fd:
      matchObj =  lineRe.match(line.strip())
      if matchObj is None:
        print("error when paring line: ", line.strip())
        sys.exit(1)
      currDate = int(matchObj.group(1))
      if currDate < startDate or currDate > endDate:
        continue
      currHour = int(matchObj.group(2))
      pollNum  = int(matchObj.group(3))
      switchResultList.append((currDate, currHour, pollNum))
  lightYList = [ item[2] for item in lightResultList ]
  switchYList = [ item[2] for item in switchResultList ]
  with open(lightResultFile, "w") as fd:
    for item in lightResultList:
      fd.write("{}{},{}\n".format(item[0], item[1], item[2]))
  with open(switchResultFile, "w") as fd:
    for item in switchResultList:
      fd.write("{}{},{}\n".format(item[0], item[1], item[2]))
  xTriggerList = [ index for index in range(len(lightResultList))]
  availableLegends = ["Switch Turned on", "Light Turned on"]
  availableColorList = ["b", "r", "g", "c", "m"]
  legends = availableLegends
  legends = None
  xLabel = "Time Delta By Hour"
  yLabel = "Poll Frequence"
  drawLine([xTriggerList, xTriggerList], [lightYList, switchYList], resultFile = plotResultFile, legends = legends, xLabel = xLabel, yLabel = yLabel, colorList = availableColorList[:2])
