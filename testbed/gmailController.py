#!/usr/bin/python

import os, sys
from apiclient import errors
from email.mime.text import MIMEText
import base64
import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

#all avaialble auto scopes: https://developers.google.com/gmail/api/auth/scopes
SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
]
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python'
class GmailController(object):
    serviceName = "gmail"
    serviceVersion = "v1"
    def __init__(self, credentialName):
        self.flags = None
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        self.credentialPath = os.path.join(credential_dir, "{}.json".format(credentialName))
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

    @staticmethod
    def create_message_with_attachment(sender, to, subject, message_text, file):
        import mimetypes
        from email import encoders
        from email.message import Message
        from email.mime.audio import MIMEAudio
        from email.mime.base import MIMEBase
        from email.mime.image import MIMEImage
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        """Create a message for an email.
        
        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file: The path to the file to be attached.
        
        Returns:
        An object containing a base64url encoded email object.
        """
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        msg = MIMEText(message_text)
        message.attach(msg)
        
        content_type, encoding = mimetypes.guess_type(file)
        
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(file, 'r')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(file, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
        
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")}

    @staticmethod
    def create_message(sender, to, subject, message_text):
        """Create a message for an email.

        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

        Returns:
        An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")}

    #response structure: https://developers.google.com/gmail/api/v1/reference/users/messages#resource
    def sendMessage(self, message, user_id = "me"): 
        """Send an email message.

        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.

        Returns:
          Sent Message.
        """
        try:
            message = (self.service.users().messages().send(userId=user_id, body=message).execute())
            return message
        except errors.HttpError as error:
            print('An error occurred:', error)
            return None

    #response structure: https://developers.google.com/gmail/api/v1/reference/users/messages#resource
    def listMessagesMatchingQuery(self, user_id = "me", query='', messageLimit = 10):
        """List all Messages of the user's mailbox matching the query.

        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          query: String used to filter messages returned.
          Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

        Returns:
          List of Messages that match the criteria of the query. Note that the
          returned list contains Message IDs, you must use get with the
          appropriate ID to get the details of a Message.
        """
        try:
            response = self.service.users().messages().list(userId=user_id,q=query, maxResults = messageLimit).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                if len(messages) >= messageLimit:
                    return messages
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId=user_id, q=query,
                                                   pageToken=page_token).execute()
                messages.extend(response['messages'])

            return messages
        except errors.HttpError as error:
            print('An error occurred: ', error)


    def getMailDetail(self, mail_id,  user_id = "me", type = "full"):
        response = self.service.users().messages().get(userId = user_id, id = mail_id).execute()
        return response
    def listMessagesWithLabels(self, user_id = "me", label_ids=[], messageLimit = 10):
        """List all Messages of the user's mailbox with label_ids applied.

          Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          label_ids: Only return Messages with these labelIds applied.

          Returns:
          List of Messages that have all required Labels applied. Note that the
          returned list contains Message IDs, you must use get with the
          appropriate id to get the details of a Message.
        """
        try:
            response = self.service.users().messages().list(userId=user_id, labelIds=label_ids, maxResults = messageLimit).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId=user_id,
                                                           labelIds=label_ids,
                                                           pageToken=page_token).execute()
                messages.extend(response['messages'])

            return messages
        except errors.HttpError as error:
              print ('An error occurred: ', error)

if __name__ == "__main__":
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None
    xianghangMailController = GmailController("xianghangmi")
    muxingMailController = GmailController("senmuxing")
    from datetime import datetime
    import time
    number = 5
    for i in range(number):
        nowDate = datetime.now()
        nowStr = nowDate.strftime("%Y-%m-%d %H-%M-%S")
        message2Send = GmailController.create_message(to = "senmuxing@gmail.com", sender = "xianghangmi@gmail.com", subject = "testMessage_{}".format(nowStr), message_text = "welcome to automatic email sending {}".format(i))
        preMsgList = muxingMailController.listMessagesMatchingQuery()
        sendResult = xianghangMailController.sendMessage(message2Send)
        sentTime = datetime.now()
        while True:
            latestMsgList = muxingMailController.listMessagesMatchingQuery()
            latestMsgId = latestMsgList[0]["id"]
            preMsgId = preMsgList[0]["id"]
            if latestMsgId == preMsgId:
                time.sleep(0.1)
                continue
            else:
                break
        receiveTime = datetime.now()
        timeCostDelta = receiveTime - sentTime
        timeCost = timeCostDelta.seconds + timeCostDelta.microseconds / float(1000000)
        print("time cost between sending and recieve is {} seconds".format(timeCost))

