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


class Root():
    """Wrapper class for debugging."""

    def __init__(self, **kwargs):
        """Raises an assertion error if any unexpected kwargs exist on initialisation."""

        print("Root.__init__() called.")
        assert not kwargs


class Team(Root):
    """storage unit for Team level statistics for a Game object."""

    def __init__(self, **kwargs):
        """Takes name, players, opponent, as mandatory arguments."""

        # Game
        self.name = kwargs.pop("name")  # string
        self.coaches = kwargs.pop("coaches")  # list of Coach objects
        self.players = kwargs.pop("players")  # list of Player objects
        self.opponent = kwargs.pop("opponent")  # string
        self.tournament = kwargs.pop("tournament")
        self.year = kwargs.pop("year")
        self.surface = kwargs.pop("surface")
        self.gender = kwargs.pop("gender")
        self.time_cap = kwargs.pop("time_cap")
        self.point_cap = kwargs.pop("point_cap")
        self.wind = kwargs.pop("wind")  # relative to the first offensive point
        self.temperature = kwargs.pop("temperature")
        self.rain = kwargs.pop("rain")  # TODO: start of game only
        self.draw = kwargs.pop("draw")  # TODO: this is a list of stages
        self.stage = kwargs.pop("stage") # TODO: this is the stage
        self.officiating = kwargs.pop("officiating")
        self.spirit_grades = kwargs.pop("spirit_grades")

        # TODO: these need to be datetime objects
        self.start = kwargs.pop("start")
        self.pause = kwargs.pop("pause")
        self.finish = kwargs.pop("finish")

        # mid-Game analyses
        if self.pause is not None:
            self.duration = self.start - self.pause
        else:
            self.duration = self.start - self.finish

        # Points
        self.points_played = 0  # count
        self.offensive_points = 0  # count
        self.offensive_structures = []  # TODO: list of initial play calls, done after the Game
        self.defensive_points = 0  # count
        self.defensive_structure = []  # TODO: list of defensive calls, done after the Game
        # TODO: offensive_points + defensive_points == points_played

        # Possessions
        self.offensive_possessions = 0  # count
        self.defensive_possessions = 0  # count

        # Touches
        self.discs = 0
        self.completions = 0
        self.turnovers = 0
        # TODO: completions + turnovers == discs
        self.completion_rate = 0.00

        # retention == passes completed per pass attempted  # TODO: individual player stats, different for shot takers
        # efficiency == goals scored per possession  # TODO: where is the win line? above what percentage?
        # conversions == goals scored per point played  # TODO: what lines are most efficient at conversions

        self.offensive_holds = []  # count
        self.offensive_breaks = []  # count
        self.offensive_retention = 0.00  # percentage
        self.offensive_efficiency = 0.00

        self.defensive_holds = []  # count
        self.defensive_breaks = []  # count
        self.offensive_conversions = 0.00  # percentage
        self.defensive_efficiency = 0.00

        # Goals
        self.goals = []  # list of players

        # Assists
        self.assists = []  # list of players

        # Defences
        self.defences = []  # list of players

        super.__init__(self, **kwargs)



def load_game(path):
    """Open a Game pickle file"""
    game = pickle.load(open(path, 'rb'))
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
    game_to_analyse = load_game('Test Match Series2017_Australia_Japan_final.p')

    pass


if __name__ == '__main__':
    sys.exit(main())
