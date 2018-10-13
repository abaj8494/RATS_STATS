# internet_operations.py
# separating out gdrive so we can compile on android without it if necessary

# builtins
import os

# google drive
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# the google drive script needs this
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


def get_credentials(user_data_dir):
    """
    Allows the program to connect to google drive
    0 - takes in path to credentials, or none
    1 - checks if credentials exist, gets new ones if not
    2 - stores and returns credentials
    """
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/drive-python-quickstart.json
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'RATS_Output'

    # pass user_data_dir=None if you want to search the working directory
    # otherwise pass a path (typically the storage area the App has access to)
    if not user_data_dir:
        user_data_dir = os.path.expanduser('~\AppData\Roaming\stats')
    credential_dir = os.path.join(user_data_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets-python-RATS.json')
    # print(credential_path)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials




def column_number_to_string(n):
    """
    takes in a column number, returns the A1 notation of that column for google sheets
    thanks internet
    """
    div = n
    string = ""
    while div > 0:
        module = (div-1) % 26
        string = chr(65+module)+string
        div = int((div-module)/26)
    return string



def update_players_sheet(sheet_name, values, spreadsheet_id):
    """
    Takes in a Game object and updates the corresponding Google Sheet on the RATS account

    # TODO: Longer term storage.
    How do we go about creating new sheets?
    At the present it just edits this one - we'll have to back it up manually ?
    Backup scripts on google drive?

    """
    credentials = get_credentials(None)
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    # spreadsheet_id = '1LQNUJbbG8fEO_eVkEOx03ibbLQ3GOq3bDkrnVCjvcfU' # ACT_M / NSW_M

    # row is the list index + 2 (column headers)
    # we know the column number sequence
    # Name, Points Player, Touches, Goals, Assists, Blocks

    column_range_start = 2
    column_range_end = len(values) + 2

    row_range_start = column_number_to_string(1)
    row_range_end = column_number_to_string(len(values[0]))  # assume all rows same length as first row

    A1_range = row_range_start+str(column_range_start)+':'+row_range_end+str(column_range_end)
    range_name = sheet_name+'!'+str(A1_range)

    print(range_name)

    # for row in values:
    #     print(row)

    body = {'values': values}

    # result here is the response from the server
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()
    # valueInputOption choices are "RAW" and "USER ENTERED"
    # if you put USER ENTERED it will format etc as though you type it like a pleb

    if result:
        print(result)
        return True