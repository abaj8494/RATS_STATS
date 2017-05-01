#!/usr/bin/env python
# -*- coding: utf-8 -*-


# TODO: these should just extend the raw classes but I'm not sure how to do it.

class Root(object):
    """Wrapper class for debugging."""

    def __init__(self, **kwargs):
        """
        Returns an AssertionError if any extraneous variables exist upon an __init__() call.
        """

        print("Root.__init__() called.")

        assert not kwargs


class Team(Root):
    """Team data for a Game of Ultimate."""

    def __init__(self, **kwargs):
        """Does not currently do anything."""

        pass


class Player(Root):
    """Player data for a Game of Ultimate."""

    def __init__(self, **kwargs):
        """Takes team_players, as mandatory arguments"""

        # raw_attributes
        self.team_players = kwargs.pop("team_players")

        # analysed_attributes
        self.connections = {self.player: {
            "pulls": 0,  # in the air in the field
            "bricks": 0,  # out-of-bounds
            "pushes": 0,  # caught pulls
            "pick ups": 0,  # after a turnover
            "blocks": 0,  # touches resulting in a turnover
            "intercepts": 0,  # catch blocks
        }}

        super(Player, self).__init__(**kwargs)
