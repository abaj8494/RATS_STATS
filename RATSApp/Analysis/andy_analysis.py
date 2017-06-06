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

def main():
    """
    WRITE A DOCSTRING
    :return: 
    """

    andy_game = load_game("{}.p")  # TODO: find a non-corrupt object to open

    print andy_game


if __name__ == '__main__':
    sys.exit(main())
