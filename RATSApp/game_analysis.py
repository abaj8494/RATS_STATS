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

        self.name = kwargs.pop("name")
        self.players = kwargs.pop("players")
        self.opponent = kwargs.pop("opponent")

        # Points
        self.points_played = 0
        self.offensive_points = 0
        self.defensive_points = 05
        # TODO: offensive_points + defensive_points == points_played

        # Touches
        self.discs = 0
        self.completions = 0
        self.incompletions = 0
        # TODO: completions + incompletions == discs
        self.completion_rate = 0.00

        # Goals
        self.goals = []
        self.assists = []
        self.defensive_breaks = []
        self.holds = []
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
