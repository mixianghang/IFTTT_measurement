#!/usr/bin/python

import os, sys
import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
SCOPES = [
        #"https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
        #"https://www.googleapis.com/auth/spreadsheets.readonly",
]
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python'
class GoogleSheetController(object):
    serviceName = "sheets"
    serviceVersion = "v4"
    def __init__(self):
        self.flags = None
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        self.credentialPath = os.path.join(credential_dir, "googleDriveController.json")
        self.credentials = self.initCredentials()
        print('Storing credentials to ' + self.credentialPath)
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build(self.serviceName, self.serviceVersion, http = self.http)
        self.testSpreadsheetId = "1sXOSfQAyBOpI4oMPuY3jFdzeQ3vo2D5gnNGKz7-MU-g"
        self.testSheetTitle = "sheet1"

    def initCredentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        store = Storage(self.credentialPath)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
        return credentials

    def getSpreadSheet(self, spreadsheetId):
      return self.service.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
    def createFile(self, name, initSheetName):
        body = {
                "properties" : {
                    "title" : name,
                    },
                "sheets" : [
                        {
                            "properties" : {
                                "title" : initSheetName,
                             }
                        }
                    ],
                }
        response = self.service.spreadsheets().create(body = body).execute()
        return response

    def listFileRevisions(self, fileId):
        revisionOp = self.service.revisions()
        revisionList = revisionOp.list(fileId = fileId).execute()
        return revisionList
    def appendFile(self, spreadsheetId, range, valueList):
        body  = {
                "values" : valueList,
                }
        response = self.service.spreadsheets().values().append(spreadsheetId = spreadsheetId, range = range, body = body, insertDataOption = "INSERT_ROWS", valueInputOption = "RAW").execute()
        return response
    def clearFileContent(self, spreadsheetId, range):
        response = self.service.spreadsheets().values().clear(spreadsheetId = spreadsheetId, range = range).execute()
    def getFileContent(self, spreadsheetId, range):
        response = self.service.spreadsheets().values().get(spreadsheetId = spreadsheetId, range = range).execute()
        return response
    def getRowList(self, spreadsheetId, range):
        try:
            response = self.service.spreadsheets().values().get(spreadsheetId = spreadsheetId, range = range).execute()

            if "values" in response:
                return response["values"]
            return []
        except Exception as e:
            return None
    def fileExists(self, filePath):
        pass
    def rmFile(self, filePath):
        pass
    def mvFile(self, srcPath, dstPath): # include files and directories
        pass
    def ls(self, parentId = None):
        pageToken = None
        overallFileList = []
        if parentId is None:
            q = "mimeType='application/vnd.google-apps.folder'"
        else:
            q = "mimeType='application/vnd.google-apps.folder' and '{}' in parents".format(parentId)
        while True:
            fileList = self.service.files().list(q = q, orderBy = "createdTime",  spaces = "drive", fields='nextPageToken, files(id, name)', pageToken=pageToken).execute()
            overallFileList.extend(fileList.get("files", []))
            pageToken = fileList.get("nextPageToken", None)
            if pageToken is None:
                break
        return overallFileList

    def getFileInfo(self, filePath):
        pass
    def setFileInfo(self, filePath, fileInfo):
        pass

if __name__ == "__main__":
  spreadsheetId = "1_Tns6MvOXRh9VZxtVw0gXoiwL3PZ3_gDVWQVLl4FtjU"
  sheetController = GoogleSheetController()
  spreadsheet = sheetController.getSpreadSheet(spreadsheetId)
  print("got spreadsheet: ",  sheetController.getSpreadSheet(spreadsheetId))
  print("title of first sheet is ", spreadsheet["sheets"][0]["properties"]["title"])
  valueList = sheetController.getRowList(spreadsheetId, range = "Sheet1")
  print(valueList)
  sys.exit(1)
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
