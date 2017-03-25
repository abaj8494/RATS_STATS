#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GameHierarchy.py

# defines structures for a live recording, with gaps for any analysis we want to run later
# class attribute lists have single item indentation to make it easier to change the display order
# App button options should call class attributes (rather than the floating lists we had before)
# I need to tweak the data storage for some actions/events/calls at runtime

# TODO: I feel like we could have a separate abstract class for timestamps (start, finish, duration, pause).
# TODO: between point time outs???


class Tournament(object):
    """Superclass for Game, provides scoring and field information."""

    # class attributes
    surfaces = [
        u"grass",
        u"beach",
        u"indoor",
    ]
    # field_size = if grass, elif beach, elif indoor, else raise ValueError; conditional on surface
    levels = [
        u"club",
        u"international",
    ]
    # formats = [u"round-robin", u"Swiss-elimination", "etc."]

    def __init__(self, **kwargs):

        self.tournament = kwargs.get("tournament")
        self.year = kwargs.get("year")  # TODO: turn this into a regex
        # self.location = kwargs.get("location")
        # self.surface = kwargs.get("surface")
        self.point_cap = kwargs.get("point_cap")
        self.time_cap = kwargs.get("time_cap")
        # self.tournament_start = None
        # self.tournament_finish = None
        # self.tournament_duration = self.tournament_finish - self.tournament_start
        # self.duration = None
        # self.level = None

    def __str__(self):
        return self.tournament

# TODO: define an abstract field class for heat maps; [x, y, z] with [0, 0, 0] as back left cone of defending end zone.

# TODO: define TimeStamp class or look at ways to do it better


class Game(Tournament):
    """"""

    def __init__(self, **kwargs):

        super(Game, self).__init__(**kwargs)

        self.score = [[0, 0]]  # double nesting, want to just append the score here after each point
        self.points = []
        self.teams = kwargs.get("teams")  # two item list of pointers to team objects, 0 = offence, 1 = defence
        self.stage = "stage"
        self.game = "{}-{}:{}-{}".format(self.tournament, self.stage, self.teams[0].team, self.teams[1].team)
        self.game_start = None
        self.game_finish = None
        self.game_pause = None
        # self.wind = kwargs.get("wind")

    def __str__(self):
        return self.game


class Point(Game):
    """"""

    # class attributes
    point_outcomes = [
        u"break",
        u"hold"
    ]
    # TODO: want to consider upwind/downwind at some point here too

    def __init__(self, **kwargs):
        """Double nesting is to handle injuries."""

        super(Point, self).__init__(**kwargs)

        self.teams = kwargs.get("teams")  # two item list of pointers to team objects, 0 = offence, 1 = defence
        self.lines = [kwargs.get("lines")]  # two item list of pointers to 7 players, 0 = offence, 1 = defence
        self.score = [kwargs.get("score"), None]  # TODO: inherit from Game.score, increment upon completion
        self.number = self.score[0][0] + self.score[0][1] + 1  # theres a better way
        self.starting_difference = self.score[0][0] - self.score[0][1]  # might want max() - min(), not sure
        # current setup means that the difference is how the offence was positioned when it started the point:
        # positive numbers mean they were winning, 0 means tied, negative means losing

        self.pull = None
        self.sequence = [[]]  # double nesting is to allow for injuries
        self.turnovers = [[0, 0]]  # two-item list [starting offence, starting defence]
        self.possessions = [[0, 0]]  # two-item list [starting offence, starting defence]
        self.outcome = None  # from point_outcomes


class Pull(Point):
    """"""

    # class attributes
    pull_locations = [
        u"in",
        u"out-of-bounds"
    ]  # clunky name because I want to keep u"location" for heat maps and duplications seems like something to avoid
    in_receptions = [
        u"caught",
        u"landed",
        u"untouched",
        u"touched",
        u"dropped-pull"
    ]
    ob_receptions = [
        u"brick",
        u"sideline"
    ]
    # type = [
    #     u"IO",
    #     u"flat",
    #     u"OI"
    # ]

    def __init__(self, **kwargs):

        super(Pull, self).__init__(**kwargs)

        self.puller = kwargs.get("puller")
        self.location = kwargs.get("location")
        self.reception = kwargs.get("reception")
        # self.type = kwargs.get("type")


class Event(Point):
    """"""

    # class attributes
    possessions = [
        u"offensive",
        u"defensive",
    ]
    types = [
        u"throw",
        u"reception",
    ]
    outcomes = [
        u"completion",
        u"turnover",
    ]

    sorted_actions = [
        # offensive
        [
            # throws
            [
                # completions
                u"pass",
                u"assist",
            ],
            [
                # turnovers
                u"double-touch",
                u"down",
                u"hand-over",
                u"out-of-bounds",
            ],
            # receptions
            [
                # completions
                u"catch",
                u"goal",
            ],
            [
                # turnovers
                u"drop"
            ],
        ],
        # defensive
        [
            # throws
            [
                # completions
                u"marked-pass",
                u"tipped-pass",
            ],
            [
                # turnovers
                u"foot-block",
                u"hand-block",
                u"stall-out",
            ],
            # receptions
            [
                # completions
                u"marked-catch",
                u""
            ],
            [
                # turnovers
                u"Callahan",
                u"block",
                u"intercept",
            ],
        ],
    ]

    def __init__(self, **kwargs):

        super(Event, self).__init__(**kwargs)

        self.player = kwargs.get("player")  # pointer to player object
        self.action = None
        # not sure about below names but type is restricted
        self.action_possession = None
        self.action_type = None
        self.action_outcome = None
        # self.location = None
        self.time = None


class Call(Point):
    """"""

    # class attributes
    calls = [
        u"offside",
        u"time-out",
        u"pick",
        u"foul",
        u"strip",
        u"marking-infraction",
        u"travel",
        u"delay-of-game",
        u"equipment",
        u"delay-of-game",
        u"injury"
    ]
    call_outcomes = [
        u"contested",
        u"uncontested",
        u"retracted"
    ]

    def __init__(self, **kwargs):

        super(Call, self).__init__(**kwargs)

        self.caller = kwargs.get("caller")  # pointer to Player object
        self.call = None
        self.opponent = None  # pointer to Player object
        # TODO: game adviser/observer should probably go here
        self.call_outcome = None

