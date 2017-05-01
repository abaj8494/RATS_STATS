# !/usr/bin/env python
# -*- coding: utf-8 -*-

# open a game file
# read through points
# read through sequences
# spit out numbers for both teams and each player in each team.


# imports
# standard library
import sys
import pickle


# local project
import game_hierarchy as gh


def main():
    """"""

    # open pickle file

    for point in gh.Game.points:
        for sequence in point.sequences:  # not sure about this, Point is a separate object
            for event in sequence:
                pass  # analyse the sequence

    return None


if __name__ == '__main__':
    sys.exit(main())
