#!/usr/bin/env python
# -*- coding: utf-8 -*-

# analysis.py


# standard library
import sys
import time
import csv
import pickle

# third party
import numpy
import scipy.stats as ss

# local project
import structures
import game_structure


def basic_info(game):
    info = []
    info.append(game.tournament)
    info.append(game.names)
    #info.append(game.time_game_end - game.time_game_start)
    # time_game_end is not stored unless you fully complete the game
    # and read_stats will crash bc it calls this (only load good games lol)
    info.append(game.score)
    # [tournamnet, names, duration, score]
    return info


def offensive_turns(game):
    oturns = 0
    for point in game.points_list:
        if point.sequence[0][0] in point.lines[0]:
            startingo = 0
        else:
            startingo = 1

        for i in range(0,len(point.sequence)-1):
            if point.sequence[i][0] in point.lines[startingo] and point.sequence[i][1] in structures.turnovers:
                oturns+=1 # if our player turns i t

            elif point.sequence[i][0] in point.lines[startingo] and point.sequence[i+1][0] in point.lines[1-startingo]:
                oturns+=1

    return oturns


def playerstat_for_everyone(game,function):
    # this function lets you run the single player stat functions over all the players

    result = []

    for team in game.teams:
        team_result = []
        for player in team:
            team_result.append([player,function(game,player)])
        result.append(team_result)

    return result


def event_count(game,player,event_to_find):
    event_count = 0
    for point in game.points_list:
        #print(point)
        for event in point.sequence:
            if event[0] == player and event[1] == event_to_find:
                event_count+=1
    return event_count


def assists(game, player):
    ass_count = 0
    for point in game.points_list:
        #for event in point.sequence:
        for i in range (0,len(point.sequence)-1):
            if point.sequence[i][0] == player and point.sequence[i+1][1] == 'goal':
                ass_count+=1
    return ass_count


def touches(game,player):
    #includes turnovers atm
    player_touches = 0
    for point in game.points_list:
        for event in point.sequence:
            if event[0] == player:
                player_touches+=1
    return player_touches


def turnovers(game, player):
    player_turnovers = 0
    for point in game.points_list:
        # for event in point.sequence:
        for i in range(0, len(point.sequence) - 1):
            if point.sequence[i][0] == player and point.sequence[i][1] in structures.turnovers:
                player_turnovers += 1
            elif point.sequence[i][0] == player and point.sequence[i + 1][1] == 'block':
                player_turnovers += 1
            else:
                pass

    return player_turnovers


def split_possessions(game):

    # only need this for the first point
    starting_offence = game.starting_offence  # take this out you don't need it you're better than this

    # take the sequence and reverse it
    for point in game.points_list:

        point.reverse()  # last action should now be goal

        # this is a check on data saving properly, it should always be true
        if point[0][1] is not u'goal':
            raise ValueError
        else:
            continue

        # Callahan check
        # TODO: leaving this for now, need to build team/group classes
            # NOTE TO SELF: you're trying to extend classes but you don't know why

    for event in sequence:
        pass

        # if event is goal:
        #     append start:sequence to possessions
        # elif event in turnover:
        #     append start:sequence to possessions
        # else: pass

    return possessions


def write_csv_files(game):
    """Creates csv files for each team's player stats and the team level game statistics"""

    results = playerstat_for_everyone(game, touches)

    for a in range(0, len(results)):  # loop over each team

        team_filename = "{} - {}.csv".format(game.teams[a], game.tournament)

        with open(team_filename, "w", newline="") as csv_file:  # create team csv file

            team_writer = csv.writer(csv_file)
            team_writer.writerow([game.teams[a]])  # team name
            team_writer.writerow(['Player', 'Touches', 'Completion Percentage', 'Goals', 'Assists', 'Blocks', 'Points'])

            for player_data in game.teams[a]:

                player_touches = 0
                player_goals = event_count(game, player_data[0], 'goal')
                player_assists = assists(game, player_data[0])
                player_blocks = event_count(game, player_data[0], 'block')
                player_points = 0

                for point in game.points_list:
                    for line in point.lines:
                        if player_data[0] in line:
                            player_points += 1

                if player_data[1]:
                    player_completion = (player_data[1] - turnovers(game, player_data[0])) / player_data[1]
                else:
                    player_completion = 1

                player_data.append(player_completion)  # player_completion percentage
                player_data.append(event_count(game, player_data[0], 'goal'))  # goals
                player_data.append(assists(game, player_data[0]))  # assists
                player_data.append(event_count(game, player_data[0], 'block'))  # blocks
                player_data.append(player_points)  # points played

                team_writer.writerow([player_data[0], player_touches, player_completion, player_goals,
                                     player_assists, player_blocks, player_points])

            csv_file.close()


def open_raw_game(raw_game):
    """Open pickle file and return the raw game object."""

    return pickle.load(open(raw_game, "rb"))

    # open the game file


def main():
    """Testing for Andy to explore data."""

    # temp_game = open_raw_game(raw_game)
    # print(temp_game)

    swab_invitational = game_structure.Tournament(
        tournament="SWAB Invitational",
        point_cap=7,
        time_cap=60,
        surface="Beach",
        ages=("Rookies","Trippers"),
        genders=("Mixed", "Very Mixed")
    )
    print(swab_invitational)

    print(swab_invitational.divisions)

    # shrooms = structures.Team(team="Shrooms", age="")


if __name__ == u"__main__":
    sys.exit(main())