# storage_operations.py
# this is where we will put all the functions that interact with local storage

# builtins
import pickle, os, shutil


def import_config(path):
    """
    Reads in a tournament config file to yield tournament-specific data
    Data to be used for making Game objects

    Currently called from main.py
    """
    # if we pass in None path or the file does not exist, return None
    if path is not None and os.path.exists(path):
        file = open(path,u'rb')
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


def load_teamlist(path):
    """
    :param path: path to a teamlist.txt file
    :return:
     (team_name, staff, players)
     where players = [[name,number,gender],[name,number,gender],...]
    """
    file = open(path, u'rb')

    players = []
    staff = []

    for line in file.readlines():
        key, value = line.split(u':')
        if key == u'name':
            team_name = value.strip()
        if key == u'staff':
            staff = value.split(u',')
        if key == u'players':
            team = value.split(u',')
            for player in team:
                try:
                    number, gender, name = player.split(u'|')
                except:
                    # catch corrupted players - seeing this is an error
                    name = player
                    number = 0
                    gender = 'u'


                player_list = [name.strip(), number, gender]
                players.append(player_list)

        else:
            # this is firing yet importing fine
            # the if/else switch is the issue i think?
            print('### missed import key: ' + str(key) +' with value: '+str(value))

    # order the players list by number before returning it
    players = sorted(players, key=lambda x: int(x[1]))

    return (team_name, staff, players)


def store_game_pickle(game,path):
    """
    Stores a game object to a pickle file
    """
    pickle.dump(game, open(path, 'wb'))
    # print('#saving_game# ' + path)


def retrieve_game_pickle(path):
    """
    returns a game object from saved pickle file
    """
    game = pickle.load(open(path, 'rb'))
    return game


def pipe_pickle_to_output(filename, source_path, destination_path):
    """
    this was specifically for moving files around for upload at the test matches
    keeping for potential use later and/or nostalgia
    """
    full_source = os.path.join(source_path,filename)
    full_dest = os.path.join(destination_path,filename)
    shutil.copyfile(full_source,full_dest)
    return True


def read_tournament_config(path):
    pass
    # still currently being done in main.py
    # return tournament_data

