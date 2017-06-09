# raw_game_hierarchy.py
# made from game_hierarchy.py @ 28/4/17 - thank you andy

# separation of concerns - this is minimally complex
# it will hold all the data taken from the game in the simplest structure
# such that it can be read into game_analysis.py to give useful numbers

# Timestamp and Root are never going to be instantiated on their own, only for superclassing
# Team, Player, Point, Event objects will be instantiated multiple times
# Game will only be created once per game taken


class Root(object):
    """
    Wrapper class for debugging.
    """

    def __init__(self, **kwargs):
        """
        Returns an AssertionError if any extraneous variables exist upon an __init__() call.
        """

        if kwargs:
            print("Root.__init__() called.")
            print(kwargs)

        assert not kwargs


# class TimeStart(Root):
#     """
#     Start time for game events.
#     """
#
#     def __init__(self, **kwargs):
#         """
#         Takes ts_start as a mandatory argument.
#         """
#
#         self.ts_start = kwargs.pop("ts_start")
#
#         super(TimeStart, self).__init__(**kwargs)
#
#
# class TimeEnd(Root):
#     """
#     End time for game events.
#     """
#
#     def __init__(self, **kwargs):
#         """
#         Takes ts_end as a mandatory argument.
#         """
#
#         self.ts_end = kwargs.pop("ts_end")
#
#         if self.ts_start:
#             self.ts_duration = self.ts_end - self.ts_end


class TimeStamp(Root):
    """
    TimeStamp is a datetime object referring to the timing of an event. It should do more than it currently does
    """

    def __init__(self, **kwargs):
        """
        Takes ts_start as a mandatory argument and should probably take other things. See other options above.
        """

        self.ts_start = kwargs.pop("ts_start")

        if "ts_end" in kwargs:
            self.ts_end = kwargs.pop("ts_end")

            if self.ts_end and self.ts_start:  # default value is None
                # this is janky af - fix it when we have time
                # print('WARNING - None passed to TimeStamp')
                # TODO: fix the program so this doesn't get here

                self.ts_duration = self.ts_end - self.ts_start

        super(TimeStamp, self).__init__(**kwargs)


class Team(Root):
    """
    Data object for a Team in a Game.
    """

    def __init__(self, **kwargs):
        """
        Takes team_name, team_players, team_coaches as mandatory arguments.
        """

        # print("Team.__init() called.")

        self.team_name = kwargs.pop("team_name")
        self.team_players = kwargs.pop("team_players")

        # TODO: Andy - added coaches as an empty property for analysis but it should just be in the .cfg file.
        # Rob - optional means the analysis won't fail - but also neither will the import
        if "team_coaches" in kwargs:
            self.team_coaches = kwargs.pop("team_coaches")
        else:
            self.team_coaches = []

        super(Team, self).__init__(**kwargs)

    def __str__(self):
        return self.team_name


class Player(Root):
    """Data object for a Player on a Team in a Game."""

    def __init__(self, **kwargs):
        """
        Takes player_name, player_number, player_gender, as mandatory arguments. 
        """
        # print("Player.__init__() called.")

        self.player_name = kwargs.pop("player_name")
        self.player_number = kwargs.pop("player_number")
        self.player_gender = kwargs.pop("player_gender")

        self.display_name = str(self.player_name)+' | '+str(self.player_number)+' | '+str(self.player_gender)

        super(Player, self).__init__(**kwargs)

    # def __eq__(self, other):
    #     return self.player_name == other.player_name
    #
    # def __ne__(self, other):
    #     return self.player_name != other.player_name

    def __str__(self):
        return self.player_name + "#" + str(self.player_number)

    __repr__ = __str__



class Game(Root):
    """
    Data object for a Game of Ultimate.
    """

    # TODO: Game should have a timestamp.

    def __init__(self, **kwargs):
        """
        Takes teams, tournament, year, point_cap, time_cap, timeouts as mandatory inputs.
        """

        # print("Game.__init__() called.")

        self.teams = kwargs.pop("teams")  # two item list: 0 = offence, 1 = defence
        self.tournament = kwargs.pop("tournament")
        self.year = kwargs.pop("year")
        self.point_cap = kwargs.pop("point_cap")
        self.time_cap = kwargs.pop("time_cap")
        self.timeouts = kwargs.pop("timeouts")

        # same index / offence system - to track through stat taking
        self.points = []
        self.timeout_status = [0,0]

        # self.stage = kwargs.pop("stage")  # choose from stages
        # self.wind = kwargs.pop("wind")  # relative to first possession, choose from winds
        # self.temperature = kwargs.pop("temperature")  # choose an integer value in degrees Celsius

        # TODO: build this to track how many nerds are ruined
        # self.flips = kwargs.pop("flips")

        super(Game, self).__init__(**kwargs)


    def get_filename(self, special=None):
        """
        :param special: 
        :return: 
        """
        # TODO: Rob why do you hate docstrings and readability whitespace.

        string = "{}{}_{}_{}".format(
            self.tournament,
            self.year,
            self.teams[0].team_name,  # offence
            self.teams[1].team_name,  # defence
        )

        if special is not None:
            string = string + str(special)

        string = string + '.p'

        return string

    __str__ = get_filename


class Point(Root):
    """
    Point is a length of sequences between goals.
    """

    # TODO: Andy - this should also have a TimeStamp
    # TODO: want to consider upwind/downwind at some point here too, for now it's just set at the start of game.

    def __init__(self, **kwargs):
        """
        Should take starting offence as a mandatory argument but idk what this junk does.
        """

        # TODO: Andy - this needs fixing.

        # print("Point.__init__() called.")

        self.sequences = []  # list of sequence objects
        self.sequence_index = None  # which sequence we are currently taking stats on

        # starting offence is always 0 - this number will track it during stat taking
        # need to be able to tell it who's on offence to carry results from previous points
        # sequences will have offence to track in there
        if "starting_offence" in kwargs:
            self.starting_offence = kwargs.pop("starting_offence")
        else:
            self.starting_offence = 0

        # starting offence is score[0]
        # you can pass the score in when starting the next point if you want
        if "score" in kwargs:
            self.score = kwargs.pop("score")
        else:
            self.score = [0,0]
        # TODO: ANDY - for the 2nd Test, this is overwritten by the final score

        super(Point, self).__init__(**kwargs)

    def current_sequence(self):

        return self.sequences[self.sequence_index]

    def create_sequence(self, lines, offence):

        self.sequences.append(Sequence(lines=lines,
                                       offence=offence))

        if self.sequence_index is None:
            self.sequence_index = 0
        else:
            self.sequence_index += 1


class Sequence(Root):
    """
    Sequence is a level below Point, and includes all actions with the same group of players.
    It changes after a Goal or Injury call.
    """
    def __init__(self, **kwargs):

        # list of events - ends on timeout, injury or goal (goal ends the point also)
        self.offence = kwargs.pop('offence')
        self.lines = kwargs.pop('lines')  # two item list, each item a list of 7 players

        self.events = []

        super(Sequence,self).__init__(**kwargs)


# class TeamPossession(Root, ):
#     """
#     TeamPossession level statistics for a sequence of Disc Events
#     """
#
#     def __init__(self, **kwargs):


class Pull(Root):
    """
    Data object for the pull.
    """

    # TODO: Andy - this should have a TimeStamp

    all_pulls = [
        # in
        u"caught",
        u"landed",
        # out-of-bounds
        u"brick",  #  stop the clap
        # in # separated for display purposes
        u"sideline",
        u"touched",
        u"untouched",
        u"dropped-pull",
        # call
        # u"offside",
    ]

    ob_pulls = [
        u"brick",
        u"sideline",
    ]

    in_pulls = [
        u"caught",
        u"landed",
        u"touched",
        u"untouched",
        u"dropped-pull",
    ]

    re_pulls = [
        u"offside",
    ]

    def __init__(self, **kwargs):
        """
        Takes puller, pull_reception as mandatory arguments.
        """

        # print("Pull.__init__() called.")

        self.puller = kwargs.pop("puller")
        self.pull_reception = kwargs.pop("pull_reception")  # from all_pull

        super(Pull, self).__init__(**kwargs)

    def __str__(self):
        return self.puller +' : ' + self.pull_reception


class Event(TimeStamp):
    """
    Event is any action which affects the status of the disc.
    """
    # class attributes

    all_actions = [
        # offensive
        # throws
        # completions
        u"pass",
        u"assist",
        # turnovers
        u"double-touch",
        u"down",
        u"hand-over",
        u"out-of-bounds",
        # receptions
        # completions
        u"catch",
        u"goal",
        # turnovers
        u"drop"
        # defensive
        # throws
        # completions
        u"marked-pass",
        u"tipped-pass",
        # turnovers
        u"foot-block",
        u"hand-block",
        u"stall-out",
        # receptions
        # completions
        u"marked-catch",
        # turnovers
        u"Callahan",
        u"block",
        u"intercept",
    ]

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

    # these categories are for visual display purposes
    primary_actions = [
        u'pass',
        u'down',
        u'drop',
        u'out-of-bounds',
        u'goal',
    ]

    secondary_actions = [
        u'stall-out',
        u'double-touch',
        u'hand-over',
    ]

    defensive_actions = [
        u'block',
        u'intercept',
        # u'Callahan',
    ]

    call_actions = [
        u'timeout',
        u'injury'
    ]

    def __init__(self, **kwargs):
        """Takes """
        # print("Event.__init__() called.")

        self.event_player = kwargs.pop("event_player")  # will be a Player object
        self.event_action = kwargs.pop("event_action")

        # TODO: Andy - should be a way to input this roughly while watching the footage back so I uncommented it
        self.location = None

        super(Event, self).__init__(**kwargs)

    def __str__(self):
        return str(self.event_player) + " : " + self.event_action

    __repr__ = __str__