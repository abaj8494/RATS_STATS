# !/usr/bin/env python
# -*- coding: utf-8 -*-

# open a game file
# read through points
# read through sequences
# read through possessions
# read through discs

# spit out numbers for both teams and each player in each team.
# TAG'd
# MON'd


# imports
# standard library
import sys
import pickle
import raw_game_hierarchy as hierarch


class Root():
    """Wrapper class for debugging."""

    def __init__(self, **kwargs):
        """Raises an assertion error if any unexpected kwargs exist on initialisation."""

        print("Root.__init__() called.")
        assert not kwargs

#
# class Team(Root):
#     """storage unit for Team level statistics for a Game object."""
#
#     def __init__(self, **kwargs):
#         """Takes name, players, opponent, as mandatory arguments."""
#
#         # Game
#
#         self.team_name = kwargs.pop("name")  # string
#         self.coaches = kwargs.pop("coaches")  # list of Coach objects
#
#         self.name = kwargs.pop("name")  # string
#         # self.coaches = kwargs.pop("coaches")  # list of Coach objects
#         self.players = kwargs.pop("players")  # list of Player objects
#         self.opponent = kwargs.pop("opponent")  # string - matches team.name
#         # self.tournament = kwargs.pop("tournament")
#         # self.year = kwargs.pop("year")
#         # self.surface = kwargs.pop("surface")
#         # self.gender = kwargs.pop("gender")
#         # self.time_cap = kwargs.pop("time_cap")
#         # self.point_cap = kwargs.pop("point_cap")
#         # self.wind = kwargs.pop("wind")  # relative to the first offensive point
#         # self.temperature = kwargs.pop("temperature")
#         # self.rain = kwargs.pop("rain")  # TODO: start of game only
#         # self.draw = kwargs.pop("draw")  # TODO: this is a list of stages
#         # self.stage = kwargs.pop("stage") # TODO: this is the stage
#         # self.officiating = kwargs.pop("officiating")
#         # self.spirit_grades = kwargs.pop("spirit_grades")
#
#         # TODO: these need to be datetime objects
#         # self.start = kwargs.pop("start")
#         # self.pause = kwargs.pop("pause")
#         # self.finish = kwargs.pop("finish")
#
#         # mid-Game analyses
#         # if self.pause is not None:
#         #     self.duration = self.start - self.pause
#         # else:
#         #     self.duration = self.start - self.finish
#
#         # Points
#         self.points_played = 0  # count
#         self.offensive_points = 0  # count
#         self.offensive_structures = []  # TODO: list of initial play calls, done after the Game
#         self.defensive_points = 0  # count
#         self.defensive_structure = []  # TODO: list of defensive calls, done after the Game
#         # TODO: offensive_points + defensive_points == points_played
#
#         # Possessions
#         self.offensive_possessions = 0  # count
#         self.defensive_possessions = 0  # count
#
#         # Touches
#         self.discs = 0
#         self.completions = 0
#         self.turnovers = 0
#         # TODO: completions + turnovers == discs
#         self.completion_rate = 0.00
#
#         # retention == passes completed per pass attempted  # TODO: individual player stats, different for shot takers
#         # efficiency == goals scored per possession  # TODO: where is the win line? above what percentage?
#         # conversions == goals scored per point played  # TODO: what lines are most efficient at conversions
#
#         self.offensive_holds = []  # count
#         self.offensive_breaks = []  # count
#         self.offensive_retention = 0.00  # percentage
#         self.offensive_efficiency = 0.00
#
#         self.defensive_holds = []  # count
#         self.defensive_breaks = []  # count
#         self.offensive_conversions = 0.00  # percentage
#         self.defensive_efficiency = 0.00
#
#         # Goals
#         self.goals = []  # list of players
#
#         # Assists
#         self.assists = []  # list of players
#
#         # Defences
#         self.defences = []  # list of players
#
#         super.__init__(self, **kwargs)
#
# class Player(Root):
#     def __init__(self, **kwargs):
#         # descriptors
#         self.name = kwargs.pop("name")
#         self.number = kwargs.pop("number")
#         self.gender = kwargs.pop("gender")
#
#         # stats
#         self.goals = 0
#         self.assists = 0
#         self.blocks = 0
#
#         self.points_played = 0
#         self.touches = 0
#         self.completions = 0
#         self.turnovers = 0
#         self.completion_rate = 0.00

def run_player_analysis(player,game):

    stats_player = Player(name=player.name,
                          number=player.number,
                          gender=player.gender)

    for point in game.points:
        for sequence in point.sequences:
            if player not in sequence.lines[0] and player not in sequence.lines[1]: # will this object comparsion work ?
                continue # they're not on this sequence, go to the next one

            stats_player.points_played+=1
            for i in range(0,len(sequence.events)):
                event = sequence.events[i]
                if event.player == player:
                    # single-check events
                    stats_player.touches+=1
                    if event.action == 'goal':
                        stats_player.goals+=1
                    if i < len(sequence.events)-1: # dont go past the end - better safe than sorry
                        # print(str(i)+'#'+str(len(sequence.events)))
                        if sequence.events[i+1].action == 'goal':
                            stats_player.assists+=1
                    if event.action == 'block':
                        stats_player.blocks+=1
                    if event.action in hierarch.Event.turnover_actions:
                        stats_player.incompletions+=1

            # calculated stats - these numbers to be run after reading over the whole game (for a player)
            if stats_player.touches != 0:
                stats_player.completion_rate = stats_player.incompletions / stats_player.touches
            else:
                stats_player.completion_rate = 1.00

    return stats_player


def load_game(file_path):
    """Open a Game pickle file"""

    game = pickle.load(open(file_path, 'rb'))
    return game


def point_progressions():
    """Points in the Game."""

    pass


def sequence_progressions():
    """Sequences in a Point"""

    pass


def possession_progression():
    """TeamPossessions in a Sequence."""

    pass


def discs_progression():
    """PlayerDiscs in a TeamPossession"""


def main():
    """"""

    turnover_actions = [
        u'double-touch',
        u'down',
        u'hand-over',
        u'out-of-bounds',
        u'drop',
        u'foot-block',
        u'hand-block',
        u'stall-out',
        u'block',
        u'intercept',
    ]

    analysed_game = load_game('Test Match Series2017_Melbourne Juggernaut_Brunch Smashed_final.p')

    print(type(analysed_game))
    print(analysed_game.points)

    possessions = [[]]

    for point in analysed_game.points:
        # print(point)
        print("\n")

        for sequence in point.sequences:
            print("starting offence: {}".format(sequence.offence))

            print("sequence length: {}".format(len(sequence.events)))
            for event in sequence.events:
                print(event)

                if event.action != u"goal":

                    if event.action not in turnover_actions:
                        possessions[0].append(event)

    # for team in game_to_analyse.teams:
    #
    #     for player in team.players:
    #         this_player = run_player_analysis(player,game_to_analyse)
    #         print('Name: ' + str(this_player.name))
    #         print('Touches: ' + str(this_player.touches))
    #         print('Goals: ' + str(this_player.goals))
    #         print('Assists: ' + str(this_player.assists))
    #         print('Blocks: ' + str(this_player.blocks))
    #         print('Points Played: ' + str(this_player.points_played))
    #         print('__________________________________________')



if __name__ == '__main__':
    sys.exit(main())
