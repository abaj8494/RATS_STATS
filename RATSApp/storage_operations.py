# storage_operations.py
# this is where we will put all the functions that interact with local storage and gdrive

# builtins
import pickle, os

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
    """
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/drive-python-quickstart.json
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Drive API Python Quickstart'

    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    # pass None if you want to search the working directory
    # otherwise pass a path (user_data_dir is for Android)
    if not user_data_dir:
        user_data_dir = os.path.expanduser('~\AppData\Roaming\stats')
    credential_dir = os.path.join(user_data_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')
    print(credential_path)

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


# lets me turn indexes (ie column number) to the A1 notation sheets requires
def column_number_to_string(n):
    div = n
    string = ""
    while div > 0:
        module = (div-1) % 26
        string = chr(65+module)+string
        div = int((div-module)/26)
    return string

def import_config(path):
    """
    Reads in a tournament config file to yield tournament-specific data
    Data to be used for making Game objects

    Currently called from main.py
    """
    if path is not None:
        file = open(path, u'rb')
        for line in file.readlines():
            key, value = line.split(u':')
            value = value.strip()
            if key == u'tournament':
                tournament = [key, value]
            elif key == u'time_cap':
                time_cap = [key, value]
            elif key == u'point_cap':
                point_cap = [key, value]
            elif key == u'timeouts':
                timeouts = [key, value]
            # elif key == u'divisions':
            #    divisions = value.split(u'|')
            #    tournament_divisions = ['tournament_divisions',divisions]
            else:
                pass
                # print(key,value)
        file.close()

        # tournament = hierarch.Tournament(tournament=tournament,
        #                                  point_cap=point_cap,
        #                                  time_cap=time_cap)

        tournament_data = [tournament, point_cap, time_cap, timeouts, ['year', 2017]]

        return tournament_data
    else:
        return None

def store_game_pickle(game,path):
    """
    Stores a game object to a pickle file
    """
    pickle.dump(game, open(path, 'wb'))
    #print('#saving_game# ' + path)


def retrieve_game_pickle(path):
    """
    returns a game object from saved pickle file
    """
    game = pickle.load(open(path, 'rb'))
    return game


def update_player_sheet(sheet_name, values):
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

    spreadsheet_id = '1LQNUJbbG8fEO_eVkEOx03ibbLQ3GOq3bDkrnVCjvcfU'

    # row is the list index + 2 (column headers)
    # we know the column number sequence
    # Name, Points Player, Touches, Goals, Assists, Blocks

    column_range_start = 2
    column_range_end = len(values) + 2

    row_range_start = column_number_to_string(1)
    row_range_end = column_number_to_string(len(values[0]))  # assume all rows same length as first row

    A1_range = row_range_start+str(column_range_start)+':'+row_range_end+str(column_range_end)
    range_name = sheet_name+'!'+str(A1_range)
    # range_name = 'Australia!A1:F1'
    print(range_name)

    body = values

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()
    # valueInputOption choices are "RAW" and "USER ENTERED"
    # if you put USER ENTERED it will format etc as though you type it like a pleb

    if not values:
        print('No data found.')
    else:
        for row in values:
            print(row)

    pass


def read_tournament_config(path):
    pass
    # return tournament_data


def read_teamlist(path):
    # soon to be replaced with scrape
    pass
    # return teamlist   