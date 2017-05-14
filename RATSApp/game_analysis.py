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

        self.name = kwargs.pop("name")  # string
        self.coaches = kwargs.pop("coaches")  # list of Coach objects
        self.players = kwargs.pop("players")  # list of Player objects
        self.opponent = kwargs.pop("opponent")  # string

        # Points
        self.points_played = 0  # count
        self.offensive_points = 0  # count
        self.defensive_points = 0  # count
        # TODO: offensive_points + defensive_points == points_played

        # Possessions
        self.offensive_possessions = 0  # count
        self.defensive_possessions = 0  # count

        # Touches
        self.discs = 0
        self.completions = 0
        self.incompletions = 0
        # TODO: completions + incompletions == discs
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

        # TODO:



def load_game():
    """Open a Game pickle file"""

    pass


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

    pass


if __name__ == '__main__':
    sys.exit(main())
