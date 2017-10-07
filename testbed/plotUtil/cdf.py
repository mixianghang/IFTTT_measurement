import matplotlib
matplotlib.use('Agg')
import  matplotlib.pyplot as plt
import logging
import sys, os
labelSize = 20
legendSize = 20
titleSize = 36
def drawCdf(xList, yList, resultFile, legends = None, xLabel = None, yLabel = None, title = None, colorList = None, opacity = 0.6, xRange = None, yRange = None):
  logger = logging.getLogger(__name__)
  figure = plt.figure(1)
  #plot lines
  lineObjList = []
  for xSubList, ySubList in zip(xList, yList):
    lineObj = plt.plot(xSubList, ySubList)
    lineObj[0].set_alpha(opacity)
    lineObjList.append(lineObj[0])
  if colorList is not None:
    for lineObj, color in zip(lineObjList, colorList):
      lineObj.set_color(color)
  logger.info("%d lines drawn", len(lineObjList))
  #set up min/max of axixes
  #if xRange is not None:
  #  plt.xlim(xRange)
  #if yRange is not None:
  #  plt.ylim(yRange)
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
  figure.savefig(resultFile, format = "pdf")
  plt.clf()

def drawCdfForFeatureEvaluation(positiveCdfFile, negativeCdfFile, resultPlotFile, xRange = None, yRange = None):
  positiveX = []
  positiveY = []
  negativeX = []
  negativeY = []
  xLabel = "Feature Value"
  yLabel = "Probability"
  legends = ["Positive", "Negative"]
  colorList = ["r", "b"]
  with open(positiveCdfFile, "r") as fd:
    for line in fd:
      attrs = line.strip().split(",")
      xValue = float(attrs[0])
      yValue = float(attrs[1])
      positiveX.append(xValue)
      positiveY.append(yValue)

  with open(negativeCdfFile, "r") as fd:
    for line in fd:
      attrs = line.strip().split(",")
      xValue = float(attrs[0])
      yValue = float(attrs[1])
      negativeX.append(xValue)
      negativeY.append(yValue)
  drawCdf(xList = [positiveX, negativeX], yList = [positiveY, negativeY], resultFile = resultPlotFile, xLabel = xLabel, yLabel = yLabel, legends = legends, colorList = colorList, xRange = xRange, yRange = yRange)

def drawCdfForFirstStep(sourceDir, resultDir):
  if not os.path.exists(resultDir):
    os.makedirs(resultDir)
  resultBaseName = ["averageSim", "maxSim", "minSim", "infrequency", "averageInfreq", "infreqGap" ,"sentSim", "oldSentSim"]
  valueMinList = [0, 0, 0, 0, 0, -1, 0, 0]
  valueMaxList = [1, 1, 1, 9, 9, 1,  1, 1]
  for featureIndex, featureName in enumerate(resultBaseName):
    currValueMin = valueMinList[featureIndex]
    currValueMax = valueMaxList[featureIndex]
    xRange = (currValueMin, currValueMax)
    resultPositiveFile = os.path.join(sourceDir, "{}_Positive_FirstStep.txt".format(featureName))
    resultNegativeFile = os.path.join(sourceDir, "{}_Negative_FirstStep.txt".format(featureName))
    resultCdfFile = os.path.join(resultDir, "{}_FirstStep.pdf".format(featureName))
    drawCdfForFeatureEvaluation(resultPositiveFile, resultNegativeFile, resultCdfFile, xRange = xRange)

def drawCdfForSecondStep(sourceDir, resultDir):
  if not os.path.exists(resultDir):
    os.makedirs(resultDir)
  #resultBaseName = ["similarityOfDomainList", "similarityOfDomainPathList", "similarityOfDomainCombinedList", "resultNumDiff", "resultNumLog", "domainDiversityDist", "domainDiversityDiff", "domainPopularity", "domainPopularityDiff", "averageTitleRbo", "maxTitleRbo"]
  #valueMinList = [0, 0, 0, -1, 0, 0, -1, 0, -1, 0, 0]
  #valueMaxList = [1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1]
  resultBaseName = ["similarityOfDomainList", "similarityOfDomainPathList", "similarityOfDomainCombinedList", "domainDiversitySimi", "domainPopularitySim", "resultNumDiff", "resultNumLog", "titleAverageSim", "titleMaxSim","titleMinSim"]
  valueMinList = [0, 0, 0, 0, 0, -1, 0, 0, 0, 0]
  valueMaxList = [1, 1, 1, 1, 1, 1,  1, 1, 1, 1]
  for featureIndex, featureName in enumerate(resultBaseName):
    currValueMin = valueMinList[featureIndex]
    currValueMax = valueMaxList[featureIndex]
    xRange = (currValueMin, currValueMax)
    resultPositiveFile = os.path.join(sourceDir, "{}_Positive_FirstStep.txt".format(featureName))
    resultNegativeFile = os.path.join(sourceDir, "{}_Negative_FirstStep.txt".format(featureName))
    resultCdfFile = os.path.join(resultDir, "{}_FirstStep.pdf".format(featureName))
    drawCdfForFeatureEvaluation(resultPositiveFile, resultNegativeFile, resultCdfFile, xRange = xRange)
funcDict = {
    "single" :  drawCdfForFeatureEvaluation,
    "multi-1" :  drawCdfForFirstStep,
    "multi-2" :  drawCdfForSecondStep,
    }
if __name__ == "__main__":
  #parser = argparse.ArgumentParser("parser")
  #parser.add_argument(
  funcName = sys.argv[1]
  if funcName == "single":
    positiveCdfFile = sys.argv[2]
    negativeCdfFile = sys.argv[3]
    resultPlotFile  = sys.argv[4]
    drawCdfForFeatureEvaluation(positiveCdfFile, negativeCdfFile, resultPlotFile)
  elif funcName == "multi-1":
    #source dir , resultDir
    drawCdfForFirstStep(sys.argv[2], sys.argv[3])
  elif funcName == "multi-2":
    #source dir , resultDir
    drawCdfForSecondStep(sys.argv[2], sys.argv[3])
  else:
    print("available functions", funcDict.keys())
