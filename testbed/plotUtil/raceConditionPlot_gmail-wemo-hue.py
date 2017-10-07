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
  parser = argparse.ArgumentParser("raceCondition plot")
  parser.add_argument("sourceFile", type = str)
  parser.add_argument("resultFile", type = str)
  options = parser.parse_args()
  sourceFile = options.sourceFile
  resultFile = options.resultFile
  availableLegends = ["Hue Light", "Wemo Switch"]
  availableColorList = ["b", "r", "g", "c", "m"]
  xList = []
  y1List = []
  y2List = []
  with open(sourceFile, "r") as fd:
    index = 0
    for line in fd:
      if line.startswith("triggerNum"):
        continue
      index += 1
      xList.append(index)
      attrs = line.strip().split(",")
      yValue1 = float(attrs[1])
      yValue2 = float(attrs[2])
      y1List.append(yValue1)
      y2List.append(yValue2)
  legends = availableLegends
  xLabel = "Test No"
  yLabel = "Delta"
  drawLine([xList, xList], [y1List, y2List], resultFile = resultFile, legends = legends, xLabel = xLabel, yLabel = yLabel, colorList = availableColorList[:2])
