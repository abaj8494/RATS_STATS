# storage_operations.py
# this is where we will put all the functions that interact with local storage and gdrive

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
    full_source = os.path.join(source_path,filename)
    full_dest = os.path.join(destination_path,filename)
    shutil.copyfile(full_source,full_dest)
    return True


def read_tournament_config(path):
    pass
    # return tournament_data


def read_teamlist(path):
    # soon to be replaced with scrape
    pass
    # return teamlist
