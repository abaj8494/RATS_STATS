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


# TODO: insert this class for a Worlds campaign.
# class Group(Root):
#     """Superclass for a group of teams; e.g. Bench Ultimate (Club) or Team Australia (International)."""
#
#     group_types = [
#         u"Club",
#         u"International",
#     ]
#
#     def __init__(self, **kwargs):
#         """Takes group, group_type as mandatory arguments."""
#
#         print("Group.__init__({}) called.".format(kwargs))
#
#         self.group = kwargs.pop("group")
#         self.group_type = kwargs.pop("group_type")
#         self.group_teams = []  # list of pointers to Team Objects
#
#         super(Group, self).__init__(**kwargs)


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



class TestMatchPlayer(Root): #working title
    def __init__(self,**kwargs):

        # tbh because these are all likely to be zero'd on instatiation
        # can probably just loop over the teamlist once and deepcopy() the results

        self.thrown_connections = {
            # a key for every other player on their team
            # a value that is how many times this player threw to them
        }

        self.received_connections = {
            # a key for every other player on their team
            # a value that is how many times this playere received from them
        }

        self.thrown_assists = {
            # as above, but assists only
        }

        self.received_goals = {
            # as above, but goals only
        }

        super(TestMatchPlayer, self).__init__(**kwargs)


    def connection_strength(self,other_player):
        return self.thrown_connections[other_player] + self.received_connections[other_player]

    def connection_quality(self,other_player):
        return self.thrown_assists[other_player] + self.received_goals[other_player]