# !/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
import sys
import pickle

# local project


# Possessions
# Possessions are a level below Sequence.

def load_game(file_path):
    """
    WRITE A DOCSTRING
    :param raw_game: 
    :return: 
    """

    analysed_game = pickle.load(open(file_path, 'rb'))

    return analysed_game


def point_analysis(analysed_game):
    """
    WRITE A DOCSTRING
    :param analysed_game: 
    :return: 
    """

    analysed_points = [point for point in analysed_game.points]

    game_points = len(analysed_points)

    for point in analysed_points:
        print(point.starting_offence)


def main():
    """
    WRITE A DOCSTRING
    :return: 
    """

    andy_game = load_game("Test Match Series_Game22017_Australia_Japan_final.p")

    # print(andy_game)
    # print(type(andy_game))

    point_analysis(andy_game)

if __name__ == '__main__':
    sys.exit(main())
