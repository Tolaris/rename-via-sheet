#!/usr/bin/env python3

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Rename files given a matrix in Google Sheets."""

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import argparse
import pickle
import os
import os.path
import sys
import tempfile

### defaults
header = ["Source", "Destination"]
# Update this to your Google Sheet, or pass in "-s". This one is mine.
sheetsSpreadsheetId = "1yUS9-u19giB78IlwPXMhHqHzoiusAYcMyZ-8JgJDt2A"
sheetsRangeName = "Sheet1!A2:B"
# keep credentials in "$script_dir/credentials"
credentialsFileName = os.path.join(os.path.dirname(sys.argv[0]), "credentials.json")
credentialsTokenFileName = os.path.join(os.path.dirname(sys.argv[0]), "credentials_token.pickle")
args = None

def getSheetsService():
  """Returns a Google Sheets service, refreshing credentials if required."""
  # Taken directly from:
  # https://developers.google.com/sheets/api/quickstart/python
  scopes = ['https://www.googleapis.com/auth/spreadsheets']
  creds = None
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(args.credentials_token):
    with open(args.credentials_token, 'rb') as token:
      creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(args.credentials, scopes)
        creds = flow.run_local_server()
      # Save the credentials for the next run
      with open(args.credentials_token, 'wb') as token:
          pickle.dump(creds, token)
  return build('sheets', 'v4', credentials=creds)


def getRenameList(spreadsheetId=sheetsSpreadsheetId,rangeName=sheetsRangeName):
  """Read the Google Sheet and return a matrix {source,destination} filenames.

  Ignores the first row, columns C and beyond, and any row with empty content for source or destination."""
  # Call the Sheets API
  service = getSheetsService()
  request = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,range=rangeName)
  response = request.execute()
  values = response.get('values', [])

  # return only rows with 2 values (where both source and destination are populated)
  return [ x for x in values if len(x) == 2 ]


def renameFiles(filenames):
  """Given a set of filenames as [source,destination] pairs, rename all files."""
  # Avoids namespace collisions in source,destination sets by using intermediate
  # temp files. Will overwrite any other destination files that may exist.
  #
  # pseudocode:
  #   for each pair, generate a unique tempfile
  #   for each pair, rename source to temp
  #   for each pair, rename temp to destination
  size = len(filenames)
  source = size*[None]
  destination = size*[None]
  temp = size*[None]
  if args.dry_run:
    for src,dest in filenames:
      print('Dry run, not renaming "{}" to "{}"'.format(src, dest))
  else:
    for i in range(size):
      source[i] = filenames[i][0]
      destination[i] = filenames[i][1]
      temp[i] = tempfile.NamedTemporaryFile(delete=False,dir=os.getcwd()).name
      print('Renaming "{}" to "{}"'.format(source[i], destination[i]))
    for i in range(size):
      os.replace(src=source[i],dst=temp[i])
    for i in range(size):
      os.replace(src=temp[i],dst=destination[i])


if __name__ == '__main__':
  # argparse
  parser = argparse.ArgumentParser(description=__doc__)

  parser.add_argument("-s", "--sheet", help="Google Sheet ID to read (default {})".format(sheetsSpreadsheetId), default=sheetsSpreadsheetId)
  parser.add_argument("-r", "--range", help="range to read (default {})".format(sheetsRangeName), default=sheetsRangeName)
  parser.add_argument("-c", "--credentials", help="path to credentials file (default {})".format(credentialsFileName), default=credentialsFileName)
  parser.add_argument("-t", "--credentials_token", help="path to credentials token (default {})".format(credentialsTokenFileName), default=credentialsTokenFileName)
  parser.add_argument("-n", "--dry-run", action="store_true", help="dry run, don't write changes")
  args = parser.parse_args()

  renameFiles(getRenameList())
