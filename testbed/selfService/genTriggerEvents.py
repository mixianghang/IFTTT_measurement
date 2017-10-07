#!/usr/bin/env python3
import requests
import json
import logging
import argparse
import time
import sys

#sync device events to the server side
def sendEvent2Server(payload):
    logger = logging.getLogger(__name__)
    requestUrl = "http://129.79.242.194:8081/ifttt/v1/updateState.php"
    headers = {
            "Self-Channel-Key" : "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd",
            }
    response = requests.post(requestUrl, headers = headers, json=payload)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return False
    else:
        return True

#sync device events to the server side
def sendEvent2Server2(deviceId, deviceState):
    logger = logging.getLogger(__name__)
    currTimeStr = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
            "userId" : 1,
            "deviceId" : deviceId,
            "deviceState" : deviceState,
            "eventTime" : currTimeStr,
            }
    #payload = json.dumps(payload)
    requestUrl = "http://129.79.242.194:8081/ifttt/v1/updateState.php"
    headers = {
            "Self-Channel-Key" : "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd",
            }
    response = requests.post(requestUrl, headers = headers, json=payload)
    print(response.text)
    if response.status_code != 200:
        logger.debug("request error with status %d and msg %s", response.status_code, response.text)
        return False
    else:
        return True

deviceIdList = [1,2,3]
def genEvents(argv):
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser("gen events")
    parser.add_argument("-in", "--interval",  type = int, default = 60) # time interval between events in seconds
    parser.add_argument("-nr", "--numberOfRounds", type = int, default = 100) # time interval between events in seconds
    options = parser.parse_args(argv)
    round = 0
    for round in range(options.numberOfRounds):
        logger.info("round %d", round)
        currTimeStr = time.strftime("%Y-%m-%d %H:%M:%S")
        for deviceId in deviceIdList:
            payload = {
                    "userId" : 1,
                    "deviceId" : deviceId,
                    "deviceState" : 1,
                    "eventTime" : currTimeStr,
                    }
            sendEvent2Server(payload)
        time.sleep(options.interval)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    genEvents(sys.argv[1:])


