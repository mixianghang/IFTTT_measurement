if __name__ == "__main__":
  gController = GoogleSheetController()
  from datetime import datetime
  number = 5
  for i in range(number):
    nowDate = datetime.now()
    nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
    values = [
          ["new song listened", nowStr],
        ]
    responseAppend = sheetController.appendFile(spreadsheetId, range = "Sheet1", valueList = values)
    print("append time: ", nowStr)
    print("response of appending: ", responseAppend)
    responseGet = sheetController.getFileContent(spreadsheetId, range = "Sheet1")
    nowDate = datetime.now()
    nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
    print("get time: ", nowStr)
    print("response of getting: ", responseGet)
