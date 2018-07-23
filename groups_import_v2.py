#! /usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import httplib2
import os

import sys
from sys import argv
from io import BytesIO
from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import googleapiclient.http

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser])
    flags.add_argument('-f', action="store", dest="to_upload")
    flags.add_argument('-d', action="store", dest="drive_folder")
    flags = flags.parse_args()
    to_upload = flags.to_upload
    drive_folder = flags.drive_folder
except ImportError:
    flags = None

SCOPES = ['https://www.googleapis.com/auth/apps.groups.migration']
CLIENT_SECRET_FILE = '/PATH/TO/CLIENT_SECRET_FILE'
APPLICATION_NAME = 'Groups Migrator'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'groups-migrator.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('groupsmigration', 'v1', http=http)
    base_path = '/PATH/TO/EML_FILES/'
    for filename in os.listdir(base_path):
        with open(base_path + filename, 'rb') as to_insert:
            to_insert = to_insert.read()
            b = BytesIO()
            b.write(to_insert)
            to_upload = googleapiclient.http.MediaIoBaseUpload(b, mimetype='message/rfc822')
            try:
                request = service.archive().insert(groupId='group@domain.com',media_body=to_upload).execute()
                print(request['responseCode'])
            except Exception as e:
                print(e) 
    
if __name__ == '__main__':
    main()
