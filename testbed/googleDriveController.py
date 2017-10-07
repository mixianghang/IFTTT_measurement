#!/usr/bin/python

import os, sys
import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
flags = None
SCOPES = [
  "https://www.googleapis.com/auth/drive",
  #"https://www.googleapis.com/auth/drive.scripts",
  #'https://www.googleapis.com/auth/drive.metadata.readonly',
  #"https://www.googleapis.com/auth/drive.file",
  #"https://www.googleapis.com/auth/drive.metadata",
]
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python'
class GoogleDriveController(object):
    serviceName = "drive"
    serviceVersion = "v3"
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

    def uploadFile(self, srcPath, name, dstParentList = []):
        file_metadata = { 'name' : name, "parents" : dstParentList }
        #media = MediaFileUpload(srcPath,mimetype='image/jpeg')
        file = self.service.files().create(body=file_metadata,
                                            media_body=srcPath
                                            #fields='id'
                                            ).execute()
        print(type(file))
        print(file)
        print('File ID: %s' % file.get('id'))

    def createFile(self, name,  parentId = "root", fileType = "doc"):
        mimeTypeDict = {
            "doc" : "application/vnd.google-apps.document",
            "sheet" : "application/vnd.google-apps.spreadsheet",
        }
        mimeType = mimeTypeDict.get(fileType, None) 
        body = {
                "name" : name,
                "mimeType" : mimeType,
                "parents" : [parentId],
                }
        response = self.service.files().create(body = body, fields = "id, name").execute()
        return response

    def listFileRevisions(self, fileId):
        revisionOp = self.service.revisions()
        revisionList = revisionOp.list(fileId = fileId).execute()
        return revisionList
    def appendFile(self, filePath, content):
        pass
    def fileExists(self, filePath):
        pass
    def rmFile(self, filePath):
        pass
    def mvFile(self, srcPath, dstPath): # include files and directories
        pass

    def ls(self, parentId = None, isFolder = True):
        pageToken = None
        overallFileList = []
        if isFolder:
            if parentId is None:
                q = "mimeType='application/vnd.google-apps.folder'"
            else:
                q = "mimeType='application/vnd.google-apps.folder' and '{}' in parents".format(parentId)
        else:
            if parentId is None:
                q = "mimeType != 'application/vnd.google-apps.folder'"
            else:
                q = "mimeType != 'application/vnd.google-apps.folder' and '{}' in parents".format(parentId)
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
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

    parentId = "0B2Edbo2pC3d4MzEzSzRBN1BnSVU"
    driveController = GoogleDriveController()
    preFileList = driveController.ls(parentId = parentId, isFolder = False)
    print(preFileList)
    import time
    import datetime
    startTime = datetime.datetime.now()
    while True:
        currentFileList = driveController.ls(parentId = parentId, isFolder = False)
        print(currentFileList)
        if len(currentFileList) != len(preFileList):
            print("got new files", currentFileList)
            break
        else:
            time.sleep(2)
