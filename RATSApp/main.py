#!/usr/bin/env python
# -*- coding: utf-8 -*-

#builtin
from __future__ import absolute_import
import pickle
from functools import partial
from copy import copy
import csv
from io import open
import os, time

#kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.widget import Widget

#google drive
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

#stats
import analysis as anal
import game_hierarchy as hierarch

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

class PlayerButton(Button):
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.callback = None

    def __str__(self):
        return u'PB<' + self.text + u'>'

    __repr__ = __str__

class Separator(Widget):
    pass


#rs # i'm reorganising the main.py file to more accurately match the flow through live stat taking


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

    def goto_confirm_input(self):
        sApp = App.get_running_app()

        #this is where we need to check if there is a saved game and ask if they want to continue taking stats on that
        # check for all pickle files in the folder
        # if there are any, offer file browser like config with confirm+cancel buttons
        # cancel dismisses popup
        # confirm loads game, goes to confirm input screen


        sApp.root.switch_to(ConfirmInputScreen())
        return True

    def goto_read_stats(self):
        sApp = App.get_running_app()
        sApp.root.switch_to(ChooseStatsScreen())
        return True

    def goto_switch_config(self):
        sApp = App.get_running_app()
        sApp.root.switch_to(ConfigScreen())
        return True


class ConfirmInputScreen(Screen):
    def __init__(self, **kwargs):
        super(ConfirmInputScreen, self).__init__(**kwargs)
        sApp = App.get_running_app()

        configpath = os.path.join(sApp.user_data_dir,'AUCDivisionII.cfg')
        sApp.tournament_data = self.import_config(configpath)
        # doing this instead of instantiating a tournament object rn

        if sApp.tournament_data:
            content = ''
            for item in sApp.tournament_data:
                # lol this produces such gross output
                content = content +str(item)
                content = content + '\n'
            self.ids.content_disp.text = content
        else:
            self.ids.content_disp.text = 'unable to load tournament configuration :('

    def conf_input(self, *args):
        sApp = App.get_running_app()
        sApp.root.switch_to(TeamSelectScreen())
        return True

    def import_config(self, path):
        if path is not None:
            sApp = App.get_running_app()

            file = open(os.path.join(sApp.user_data_dir, path), u'rb')
            for line in file.readlines():
                key, value = line.split(u':')
                value = value.strip()
                if key == u'tournament_name':
                    tournament_name = [key,value]
                elif key == u'time_cap':
                    time_cap = [key,value]
                elif key == u'point_cap':
                    point_cap = [key,value]
                elif key == u'timeouts':
                    timeouts = [key,value]
                elif key == u'divisions':
                    divisions = value.split(u'|')
                    tournament_divisions = ['tournament_divisions',divisions]
                else:
                    pass
                    #print(key,value)
            file.close()

            # tournament = hierarch.Tournament(tournament=tournament_name,
            #                                  point_cap=point_cap,
            #                                  time_cap=time_cap)

            tournament_data = [tournament_name,point_cap,time_cap,timeouts,
                               tournament_divisions,['tournament_year',2017]]

            return tournament_data
        else:
            return None

    def go_back(self, *args):
        sApp = App.get_running_app()
        sApp.root.switch_to(MenuScreen())
        return True

class TeamSelectScreen(Screen):
    def __init__(self, **kwargs):
        super(TeamSelectScreen, self).__init__(**kwargs)
        sApp = App.get_running_app()

        teamlistpath = os.path.join(sApp.user_data_dir, 'teamlists'.strip())
        self.ids.BigBox.add_widget(Label(text='Select Team A (this is arbitrary)'))
        self.filechA = FileChooserListView(path=teamlistpath, size_hint_y=5)
        self.ids.BigBox.add_widget(self.filechA)

        self.ids.BigBox.add_widget(Separator())

        self.ids.BigBox.add_widget(Label(text='Select Team B (this is arbitrary)'))
        self.filechB = FileChooserListView(path=teamlistpath, size_hint_y=5)
        self.ids.BigBox.add_widget(self.filechB)

        self.ids.BigBox.add_widget(Separator())

        specialBox = BoxLayout(orientation='horizontal')
        self.ids.BigBox.add_widget(specialBox)

        confBut = Button(text='Confirm Teams')
        confBut.bind(on_release=self.conf_selec)
        specialBox.add_widget(confBut)

        menuBut = Button(text='Back')
        menuBut.bind(on_release=self.go_back)
        specialBox.add_widget(menuBut)

    def conf_selec(self, *args):
        sApp = App.get_running_app()

        # this feels clunky, i'm splitting and joining all over the shop
        # TODO: split out file access functions and make them good

        path, teamAfn = os.path.split(self.filechA.selection[0])
        path, teamBfn = os.path.split(self.filechB.selection[0])

        filenames = [teamAfn,teamBfn]
        for filename in filenames:
            full_path = os.path.join(sApp.user_data_dir, 'teamlists', filename)
            file = open(full_path, u'rb')

            players = []
            for line in file.readlines():
                key, value = line.split(u':')
                if key == u'name':
                    team_name = value
                elif key == u'players':
                    team = value.split(u',')
                    for player in team:
                        player = player.strip() # trailing newline on last player
                        player_obj = hierarch.Player(player_name=player,
                                                     player_number=420)
                        players.append(player_obj)

            team = hierarch.Team(team_name=team_name,
                                 team_players=players,
                                 team_division='womens is better')

            file.close()
            sApp.unordered_teams.append(team)

        sApp.root.switch_to(SelectOffenceScreen())
        return True

    def go_back(self, *args):
        sApp = App.get_running_app()
        sApp.root.switch_to(MenuScreen())
        return True


class SelectOffenceScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectOffenceScreen, self).__init__(**kwargs)

        sApp = App.get_running_app()
        for team in sApp.unordered_teams:
            teambutton = Button(text=team.team_name)
            storecallback = partial(self.store_offence, teambutton)
            teambutton.bind(on_release=storecallback)
            self.ids.SOBox.add_widget(teambutton)

    def store_offence(self, teambutton, *args):
        sApp = App.get_running_app()
        offence_name = teambutton.text
        if sApp.unordered_teams[0].team_name == offence_name:
            teams = sApp.unordered_teams
        elif sApp.unordered_teams[1].team_name == offence_name:
            teams = sApp.unordered_teams
            teams.reverse()
        else:
            print('invalid team selected for offence') # literally no idea

        # keywords here looks like [[key,value],[key,value]] etc
        #TODO: check that this kwarg passing shit actually works
        keywords = sApp.tournament_data
        keywords.append(['game_teams', teams])
        keywords.append(['game_stage','default_stage'])
        keywords = dict(sApp.tournament_data)
        sApp.game = hierarch.Game(**keywords)

        sApp.root.switch_to(SelectPlayersScreen())
        return True


class SelectPlayersScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectPlayersScreen, self).__init__(**kwargs)
        sApp = App.get_running_app()
        if len(sApp.game.points) == 0: # if this is the first point
            self.offence = 0
            self.score = [0,0]
        else:
            self.offence = 1 - sApp.game.points[-1].offence # opposite offence to end of last point
            self.score = sApp.game.points[-1].point_score # should be incremented when the goal is scored, hence correct here
        self.temp_oline = []
        self.temp_dline = []

        for player in sApp.game.game_teams[self.offence].team_players:
            pb = ToggleButton(text=player.player_name)
            pb.bind(on_release=partial(self.swap_state, pb, player))
            self.ids.LeftBox.add_widget(pb)

        for player in sApp.game.game_teams[1 - self.offence].team_players:
            pb = ToggleButton(text=player.player_name)
            pb.bind(on_release=partial(self.swap_state, pb, player))
            self.ids.RightBox.add_widget(pb)

    def swap_state(self,pb,player,*args):
        #this is the NEW state - normal button pressed will trigger the if 'down' branch of this
        # offence here is just for checking which team the call is coming from and hence which list to edit
        sApp = App.get_running_app()
        if pb.state == 'normal':
            if player in sApp.game.game_teams[1 - self.offence].team_players:
                self.temp_dline.remove(player)
            else:
                self.temp_oline.remove(player)
        elif pb.state == 'down':
            if player in sApp.game.game_teams[1 - self.offence].team_players:
                self.temp_dline.append(player)
            else:
                self.temp_oline.append(player)
        else:
            print('something is broken in the state switching of player selection')
        self.ids.subtitle.text = 'Offence: '+str(len(self.temp_oline))+' | Defence: '+str(len(self.temp_dline))
        return True


    def store_players(self):
        sApp = App.get_running_app()
        if len(self.temp_dline) == 7 and len(self.temp_oline) == 7:
            #order has already been checked when we look for offence in the __init__ of this screen
            #TODO: confirm this
            lines = [self.temp_oline,self.temp_dline]
            sApp.current_point = hierarch.Point(point_teams=sApp.game.game_teams,
                                                point_lines=lines,
                                                point_score=self.score)
            sApp.root.switch_to(PullingScreen())
        else:
            pass
        return True


class PullingScreen(Screen):
    def __init__(self, **kwargs):
        super(PullingScreen, self).__init__(**kwargs)
        sApp = App.get_running_app()
        self.puller = 'puller_not_set'

        for player in sApp.current_point.current_lines()[1 - sApp.current_point.offence]:
            pb = ToggleButton(text=player.player_name, group=u'players')
            pickcallback = partial(self.set_puller, pb, player)
            pb.bind(on_release=pickcallback)
            self.ids.LeftBox.add_widget(pb)

        for action in hierarch.Pull.all_pulls:
            outcome = Button(text=action)
            outcomecallback = partial(self.set_pull_outcome, outcome)
            outcome.bind(on_release=outcomecallback)
            self.ids.RightBox.add_widget(outcome)

    def on_enter(self, *args):
        pass

    def set_puller(self, puller, player, *args):
        sApp = App.get_running_app()
        self.puller = player
        return True

    def set_pull_outcome(self, outcome, *args):
        sApp = App.get_running_app()
        if self.puller != 'puller_not_set':

            pull = hierarch.Pull(puller=self.puller,
                                 pull_action=outcome)
            if outcome == u'dropped-pull':
                sApp.current_point.offence = 1 - sApp.current_point.offence

            sApp.current_point.ts_start = time.time()
            #if sApp.current_point.score == [0,0]:
            #    sApp.game.ts_start = time.time()
            # TODO: game start time?
            sApp.root.switch_to(SelectActionScreen())

        return True


class SelectActionScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectActionScreen, self).__init__(**kwargs)

        self.popup = None
        self.temp_event = [hierarch.Player, None, None, None]  # [player, action, player_ts, action_ts]
        self.pblist = []
        sApp = App.get_running_app()

        for player in sApp.current_point.current_lines()[sApp.current_point.offence]:
            pb = ToggleButton(text=player.player_name, group=u'players')
            pickcallback = partial(self.set_player, player)
            pb.bind(on_release=pickcallback)
            self.pblist.append(pb)
            self.ids.LeftBox.add_widget(pb)

        for action in hierarch.Event.primary_actions:
            select = Button(text=action)
            selectcallback = partial(self.set_action, action)
            select.bind(on_release=selectcallback)
            self.ids.RightBox.add_widget(select)

        secondaryBox = BoxLayout(orientation='horizontal',
                                 padding=[0,10])
        for action in hierarch.Event.secondary_actions:
            select = Button(text=action)
            selectcallback = partial(self.set_action, action)
            select.bind(on_release=selectcallback)
            secondaryBox.add_widget(select)
        self.ids.RightBox.add_widget(secondaryBox)

        for action in hierarch.Event.defensive_actions:
            select = Button(text=action)
            selectcallback = partial(self.set_action, action)
            select.bind(on_release=selectcallback)
            self.ids.RightBox.add_widget(select)


    def set_player(self, player, *args):
        sApp = App.get_running_app()
        self.temp_event[0] = player
        self.temp_event[2] = time.time() - sApp.current_point.ts_start
        return True

    def set_action(self, action, *args):
        # store the event
        sApp = App.get_running_app()
        if self.temp_event[0] != 'player_not_set':
            #button does nothing if haven't picked a player
            self.temp_event[1] = action
            self.temp_event[3] = time.time() - sApp.current_point.ts_start
            #timestamps are time since start of the point

            event_obj = hierarch.Event(event_player=self.temp_event[0],
                                       event_action=self.temp_event[1],
                                       ts_start=self.temp_event[2],
                                       ts_end=self.temp_event[3])

            sApp.current_point.sequence.append(copy(event_obj))
            sApp.save_game()
            for pb in self.pblist:
                pb.state = u'normal' # reset the player buttons
            # offensive turnovers
            if event_obj.action_outcome == u'turnover' and event_obj.event_action not in hierarch.Event.defensive_actions:
                sApp.current_point.offence = 1 - sApp.current_point.offence
                sApp.root.switch_to(SelectActionScreen())
            # defensive turnovers
            if event_obj.event_action in hierarch.Event.defensive_actions:
                popupContent = BoxLayout(orientation=u'vertical')
                for player in sApp.current_point.current_lines()[1-sApp.current_point.offence]:
                    pb = Button(text=player.player_name)
                    pbcallback = partial(self.save_defensive_action, player , event_obj.event_action)
                    pb.bind(on_release=pbcallback)
                    popupContent.add_widget(pb)

                self.popup = Popup(title=u'who got the block/int',
                                   content=popupContent,
                                   size_hint=[0.7, 0.7])
                self.popup.open()

            if event_obj.event_action == u'goal':
                # change this to the stacked or whatever, even x/y  boxex
                popupContent = BoxLayout()
                sApp.current_point.time_end = time.time()
                sApp.current_point.point_score[sApp.current_point.offence] += 1
                sApp.game.game_score.append(sApp.current_point.point_score)
                scoreLabel = Label(text='the score is '+str(sApp.current_point.point_score))
                popupContent.add_widget(scoreLabel)

                yes = Button(text=u'yes')
                yes.bind(on_release=self.end_game)
                popupContent.add_widget(yes)

                no = Button(text=u'no')
                no.bind(on_release=self.end_point)
                popupContent.add_widget(no)

                # paws = Button(text=u'pause please')
                # paws.bind(on_release=self.pause_game)
                # popupContent.add_widget(paws)

                # review = Button(text=u'review stats')
                # review.bind(on_release=self.review_stats)
                # popupContent.add_widget(review)

                self.popup = Popup(title=u'was that goal the game winner?',
                                   content=popupContent,
                                   size_hint=[0.7, 0.7])
                self.popup.open()

            return True

    def review_stats(self,*args):
        # MORE POPUPS
        # can i nest them like this? hope so
        sApp = App.get_running_app()
        statscontent = BoxLayout()
        statscontent.add_widget(Label(text=u'offensive turns'))
        statscontent.add_widget(Label(text=str(anal.offensive_turns(sApp.game))))
        #here we add the actual stats to review

        returnbut = Button(text=u'Return')

        self.stats_popup = Popup(title=u'stats @ rn',
                                 content=statscontent,
                                 size_hint=[0.7,0.7])
        returnbut.bind(on_release=self.stats_popup.dismiss)
        statscontent.add_widget(returnbut)

        self.stats_popup.open()
        return True

    def save_defensive_action(self, player, action, *args):
        sApp = App.get_running_app()
        blockevent = hierarch.Event(event_player=player,
                                    event_action=action,
                                    ts_start=time.time()-sApp.current_point.ts_start,
                                    ts_end=time.time()-sApp.current_point.ts_start)
                                    # blocks are instantaneous lol
        sApp.current_point.sequence.append(blockevent)
        sApp.current_point.offence = 1 - sApp.current_point.offence
        if self.popup:
            self.popup.dismiss()
        sApp.root.switch_to(SelectActionScreen())
        return True

    # def pause_game(self, *args):
        # save the time as some paused time so can return with working timer
        # save the game object as it exists
        # sApp = App.get_running_app()


    def end_point(self, *args):
        if self.popup:
            self.popup.dismiss()
        sApp = App.get_running_app()
        sApp.game.points.append(sApp.current_point)
        sApp.current_point = None
        sApp.root.switch_to(SelectPlayersScreen())
        return True

    def end_game(self, *args):
        if self.popup:
            self.popup.dismiss()
        sApp = App.get_running_app()
        sApp.game.points.append(sApp.current_point)
        #sApp.game.time_game_end = time.time()
        savename = sApp.game.tournament_name.strip() + '_' + sApp.game.game_teams[0].team_name.strip() + "v" + sApp.game.game_teams[1].team_name.strip() + ".p"
        path = os.path.join(sApp.user_data_dir, savename)
        print('#end_game# ' + path)
        pickle.dump(sApp.game, open(path, 'wb'))

        sApp.game = None #should we clear this here??
        sApp.unordered_teams = []
        sApp.root.switch_to(MenuScreen())
        return True


# these are important but not part of the live stat taking - consider breaking up screen definitions


class ChooseStatsScreen(Screen):
    def __init__(self,**kwargs):
        super(ChooseStatsScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        sApp = App.get_running_app()
        # loadpath = os.path.join(sApp.user_data_dir)
        # self.ids.BigBox.add_widget(Label(text='Select Team A (this is arbitrary)'))
        loadpath = sApp.user_data_dir
        self.filechA = FileChooserListView(path=loadpath, size_hint_y=5)
        # path, game = os.path.split(filechA.selection[0])
        self.ids.BigBox.add_widget(self.filechA)
        conf = Button(text=u'confirm')
        conf.bind(on_release=self.pick_game)
        self.ids.BigBox.add_widget(conf)

    def pick_game(self,*args):
        sApp = App.get_running_app()
        #print(self.filechA.selection)
        self.path = self.filechA.selection[0]
        sApp.game = pickle.load(open(self.path, 'rb'))
        #
        # for some reason in the SMO ellipsis v rogue game there was a None object saved in the pointslist, crashing it
        # this is clearly a workaround - why the None ??
        # - works still -
        #
        for point in sApp.game.points:
            if point == None:
                print("Detected a NoneType obj in game.points, discarding")
                sApp.game.points.remove(point)

        sApp.root.switch_to(ReadScreen())


class ReadScreen(Screen):
    def __init__(self, **kwargs):
        super(ReadScreen, self).__init__(**kwargs)
        self.ids.BigBox.add_widget(Label(text='stats go here',
                                         size_hint=[1,0.05]))

    def on_pre_enter(self):
        sApp = App.get_running_app()
        if sApp.game:
            self.ids.BigBox.add_widget(Label(text=str(anal.basic_info(sApp.game)), size_hint=[1,0.01]))

            for point in sApp.game.points:
                print(point)

            # TODO: turn this on later
            # anal.write_csv_files(sApp.game)
            # anal.gdrive_text(sApp.get_credentials())
        else:  # shouldn't happen
            self.ids.BigBox.add_widget(Label(text=u'Could not find a Game object'))

    def on_enter(self):
        self.ids.BigBox.add_widget(Button(text='Back',
                                          size_hint=[0.1,0.1],
                                          on_release=self.go_back))

    def go_back(self, *args):
        sApp = App.get_running_app()
        sApp.root.switch_to(MenuScreen())
        return True


class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)

        sApp = App.get_running_app()
        sApp.game = sApp.import_config(sApp.teamfilenames)
        if sApp.game:
            content = str(sApp.game.tournament) + str(sApp.game.time_cap) + str(sApp.game.point_cap) + str(
                sApp.game.team_names) + '\n' + str(sApp.game.team_players)
        else:
            content = 'no game found - go to switch config'
        self.ids.content_disp.text = content

        optionsBox = BoxLayout(orientation='horizontal')

        self.ids.BigBox.add_widget(optionsBox)

        confBut = Button(text='switch',
                         size_hint=[1,0.2])
        confBut.bind(on_release=self.switch_config)
        optionsBox.add_widget(confBut)

        backBut = Button(text='main menu',
                         size_hint=[1,0.2])
        backBut.bind(on_release=self.go_back)
        optionsBox.add_widget(backBut)

    def switch_config(self, *args):
        sApp = App.get_running_app()
        sApp.root.switch_to(SwitchScreen())
        return True

    def go_back(self, *args):
        sApp = App.get_running_app()
        sApp.root.switch_to(MenuScreen())
        return True

    def do_import(self,filenames):
        sApp = App.get_running_app()
        return sApp.import_config(filenames)

    def on_enter(self):
        pass




class RatsScreenManager(ScreenManager):
    def go_back(self):
        # GO BACK TO THE PREVIOUS SCREEN
        # this functionality will probably require redoing switch_to
        # or some shit who knows
        #
        pass

    #timer might also sit here?


class StatsApp(App):
    def __init__(self):
        super(StatsApp, self).__init__()

        self.tournament_data = None
        self.current_point = None
        self.game = None
        # game files aren't currently linked to tournament objects

        self.unordered_teams = [] # read in teams, check whos on offence next screen

    def build(self):
        sApp = App.get_running_app()
        return Builder.load_file(u'stats.kv')

    def save_game(self, *args):
        # popup confirmation is for nerds
        sApp = App.get_running_app()
        savename = sApp.game.tournament_name.strip() + u'_' + sApp.game.game_teams[0].team_name.strip() +\
                   "v" + sApp.game.game_teams[1].team_name.strip() + ".p"
        path = os.path.join(sApp.user_data_dir, savename)
        print('#save_game# ' + path)
        pickle.dump(sApp.game, open(path, 'wb'))
        return True

    def on_pause(self):
        self.save_game()
        return True

    def get_credentials(self):
        sApp = App.get_running_app()

        # If modifying these scopes, delete your previously saved credentials
        # at ~/.credentials/drive-python-quickstart.json
        SCOPES = 'https://www.googleapis.com/auth/drive'
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'Drive API Python Quickstart'

        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(sApp.user_data_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'drive-python-quickstart.json')
        print(credential_path)

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def on_resume(self):
        pass


if __name__ == u'__main__':
    a = StatsApp()
    a.run()
