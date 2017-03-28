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
import structures as struct
import analysis as anal
from structures import Game, Point

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
        for point in sApp.game.points_list:
            if point == None:
                print("Detected a NoneType obj in game.points_list, discarding")
                sApp.game.points_list.remove(point)

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

            for point in sApp.game.points_list:
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
        if sApp.game:
            self.ids.content_disp.text = str(sApp.game.tournament) + str(sApp.game.time_cap) + str(sApp.game.points_cap) + str(
                sApp.game.team_names) + '\n' + str(sApp.game.team_players[0]) + '\n' + str(sApp.game.team_players[1])
            # self.ids.BigBox.add_widget(Label(text=content, size_hint=[1.5, 4]))
        else:
            self.ids.content_disp.text = 'no game object found - go to switch config'

    def conf_input(self, *args):
        sApp = App.get_running_app()
        sApp.root.switch_to(SelectOffenceScreen())
        return True

    def go_back(self, *args):
        sApp = App.get_running_app()
        sApp.root.switch_to(MenuScreen())
        return True

    def on_enter(self):
        pass


class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)

        sApp = App.get_running_app()
        sApp.game = sApp.import_config(sApp.teamfilenames)
        if sApp.game:
            content = str(sApp.game.tournament) + str(sApp.game.time_cap) + str(sApp.game.points_cap) + str(
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


class SwitchScreen(Screen):
    def __init__(self, **kwargs):
        super(SwitchScreen, self).__init__(**kwargs)
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
        confBut = Button(text='confirm selections')
        confBut.bind(on_release=self.conf_selec)
        specialBox.add_widget(confBut)
        menuBut = Button(text='Back')
        menuBut.bind(on_release=self.go_back)
        specialBox.add_widget(menuBut)

    def conf_selec(self, *args):
        path, teamAfn = os.path.split(self.filechA.selection[0])
        path, teamBfn = os.path.split(self.filechB.selection[0])
        sApp = App.get_running_app()
        sApp.teamfilenames = [teamAfn, teamBfn]
        #print(sApp.teamfilenames)
        sApp.root.switch_to(ConfigScreen())
        return True

    def go_back(self, *args):
        sApp = App.get_running_app()
        sApp.root.switch_to(MenuScreen())
        return True


class SelectOffenceScreen(Screen):
    # TODO: want this to get saved as a property of game

    def __init__(self, **kwargs):
        super(SelectOffenceScreen, self).__init__(**kwargs)

        sApp = App.get_running_app()
        for team in sApp.game.team_names:
            teambutton = Button(text=team)
            storecallback = partial(self.store_offence, sApp.game.team_names.index(team))
            teambutton.bind(on_release=storecallback)
            self.ids.SOBox.add_widget(teambutton)

    def on_enter(self, *args):
        sApp = App.get_running_app()

        sApp.current_point = Point([sApp.temp_oline, sApp.temp_dline], sApp.temp_offence)

        sApp.temp_offence = None
        sApp.temp_dline = []
        sApp.temp_oline = []

    def store_offence(self, offence, *args):
        sApp = App.get_running_app()
        sApp.current_point.offence = offence
        sApp.game.starting_offence = offence  # Andy, hoping this will save me time in anlysis.
        sApp.root.switch_to(SelectPlayersScreen())
        return True

class SelectPlayersScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectPlayersScreen, self).__init__(**kwargs)

        self.temp_oline = []
        self.temp_dline = []
        sApp = App.get_running_app()

        for player in sApp.game.teams[sApp.current_point.offence]:
            pb = ToggleButton(text=player)
            pb.bind(on_release=partial(self.swap_state, pb, sApp.current_point.offence))
            self.ids.LeftBox.add_widget(pb)

        for player in sApp.game.teams[1 - sApp.current_point.offence]:
            pb = ToggleButton(text=player)
            pb.bind(on_release=partial(self.swap_state, pb, 1 - sApp.current_point.offence))
            self.ids.RightBox.add_widget(pb)

    def swap_state(self,pb,offence,*args):
        #this is the NEW state - normal button pressed will trigger the if 'down' branch of this
        # offence here is just for checking which team the call is coming from and hence which list to edit
        if pb.state == 'normal':
            if offence:
                self.temp_dline.remove(pb.text)
            else:
                self.temp_oline.remove(pb.text)
        elif pb.state == 'down':
            if offence:
                self.temp_dline.append(pb.text)
            else:
                self.temp_oline.append(pb.text)
        else:
            print('something is broken in the state switching of player selection')
        self.ids.subtitle.text = 'Offence: '+str(len(self.temp_oline))+' | Defence: '+str(len(self.temp_dline))
        return True


    def store_players(self):
        sApp = App.get_running_app()
        if len(self.temp_dline) == 7 and len(self.temp_oline) == 7:
            sApp.current_point.lines[sApp.current_point.offence] = self.temp_oline
            sApp.current_point.lines[1 - sApp.current_point.offence] = self.temp_dline
            sApp.root.switch_to(PullingScreen())
        else:
            pass
        return True


class PullingScreen(Screen):
    def __init__(self, **kwargs):
        super(PullingScreen, self).__init__(**kwargs)
        sApp = App.get_running_app()
        sApp.current_point.pull[0] = 'puller_not_set'

        for player in sApp.current_point.lines[1 - sApp.current_point.offence]:
            pb = ToggleButton(text=player, group=u'players')
            pickcallback = partial(self.set_puller, pb)
            pb.bind(on_release=pickcallback)
            self.ids.LeftBox.add_widget(pb)

        for action in struct.pull_outcomes:
            outcome = Button(text=action)
            outcomecallback = partial(self.set_pull_outcome, outcome)
            outcome.bind(on_release=outcomecallback)
            self.ids.RightBox.add_widget(outcome)

    def on_enter(self, *args):
        pass

    def set_puller(self, puller, *args):
        sApp = App.get_running_app()
        sApp.current_point.pull[0] = puller.text
        return True

    def set_pull_outcome(self, outcome, *args):
        sApp = App.get_running_app()
        if sApp.current_point.pull[0] != 'puller_not_set':
            #if they haven't selected a puller, button will do nothing
            sApp.current_point.pull[1] = outcome.text
            if sApp.current_point.pull[1] in struct.pull_outcomes_turnovers:
                sApp.current_point.offence = 1 - sApp.current_point.offence
            sApp.current_point.time_start = time.time()
            if sApp.game.score == [0,0]:
                sApp.game.time_game_start = time.time()
            sApp.root.switch_to(SelectActionScreen())

        return True


class SelectActionScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectActionScreen, self).__init__(**kwargs)
        self.popup = None
        self.temp_event = ['player_not_set', None, 0]  # [player, action, timestamp]
        self.pblist = []
        sApp = App.get_running_app()
        for player in sApp.current_point.lines[sApp.current_point.offence]:
            pb = ToggleButton(text=player, group=u'players')
            pickcallback = partial(self.set_player, pb)
            pb.bind(on_release=pickcallback)
            self.pblist.append(pb)
            self.ids.LeftBox.add_widget(pb)

        for action in struct.actions:
            select = Button(text=action)
            selectcallback = partial(self.set_action, select)
            select.bind(on_release=selectcallback)
            self.ids.RightBox.add_widget(select)

        # save button
        goBut = Button(text=u'save')
        goButcallback = partial(sApp.save_game) # call some save shit here
        goBut.bind(on_release=goButcallback)
        self.ids.SpecialBox.add_widget(goBut)

        # block button
        blockBut = Button(text=u'block')
        blockButcallback = partial(self.set_action, blockBut)
        blockBut.bind(on_release=blockButcallback)
        self.ids.SpecialBox.add_widget(blockBut)

    def on_enter(self, *args):
        pass

    def set_player(self, player, *args):
        self.temp_event[0] = player.text
        return True

    def set_action(self, action, *args):
        # store the event
        sApp = App.get_running_app()
        if self.temp_event[0] != 'player_not_set':
            #button does nothing if haven't picked a player
            self.temp_event[1] = action.text
            self.temp_event[2] = time.time() - sApp.current_point.time_start
            #timestamps are time since start of the point
            sApp.current_point.sequence.append(copy(self.temp_event))
            sApp.save_game()
            for pb in self.pblist:
                pb.state = u'normal'

            if self.temp_event[1] in struct.turnovers:
                sApp.current_point.offence = 1 - sApp.current_point.offence
                sApp.root.switch_to(SelectActionScreen())

            if self.temp_event[1] == u'block':
                popupContent = BoxLayout(orientation=u'vertical')
                #blockLabel = Label(text='who got the block')
                #popupContent.add_widget(blockLabel)
                for player in sApp.current_point.lines[1-sApp.current_point.offence]:
                    pb = Button(text=player)
                    pbcallback = partial(self.save_block,pb)
                    pb.bind(on_release=pbcallback)
                    popupContent.add_widget(pb)

                self.popup = Popup(title=u'who got the block',
                                   content=popupContent,
                                   size_hint=[0.7, 0.7])
                self.popup.open()

            if self.temp_event[1] == u'goal':
                # change this to the stacked or whatever, even x/y  boxex
                popupContent = BoxLayout()
                sApp.current_point.time_end = time.time()
                sApp.game.score[sApp.current_point.offence] += 1
                scoreLabel = Label(text='the score is '+str(sApp.game.score))
                popupContent.add_widget(scoreLabel)

                yes = Button(text=u'yes')
                yes.bind(on_release=self.end_game)
                popupContent.add_widget(yes)

                no = Button(text=u'no')
                no.bind(on_release=self.end_point)
                popupContent.add_widget(no)

                #paws = Button(text=u'pause please')
                #paws.bind(on_release=self.pause_game)
                #popupContent.add_widget(paws)

                # review stats button should be here
                review = Button(text=u'review stats')
                review.bind(on_release=self.review_stats)
                popupContent.add_widget(review)

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

    def save_block(self, player, *args):
        sApp = App.get_running_app()
        blockevent = [player.text,'block',(time.time()-sApp.current_point.time_start)]
        sApp.current_point.sequence.append(blockevent)

        sApp.current_point.offence = 1-sApp.current_point.offence
        if self.popup:
            self.popup.dismiss()
        #print('$$$ switching screen')
        sApp.root.switch_to(SelectActionScreen())
        #does not appear to work rn
        return True

    #moved save_game to be a function of the App class - so can access it anywhere


    # def pause_game(self, *args):
        # save the time as some paused time so can return with working timer
        # save the game object as it exists
        # sApp = App.get_running_app()


    def end_point(self, *args):
        if self.popup:
            self.popup.dismiss()
        sApp = App.get_running_app()
        sApp.game.points_list.append(sApp.current_point)
        sApp.current_point = None

        sApp.root.switch_to(SelectOffenceScreen())
        return True

    def end_game(self, *args):
        if self.popup:
            self.popup.dismiss()
        sApp = App.get_running_app()
        sApp.game.points_list.append(sApp.current_point)
        sApp.game.time_game_end = time.time()
        #this path
        savename = sApp.game.tournament.strip() + '_' + sApp.game.team_names[0].strip() + "v" + sApp.game.team_names[1].strip() + ".p"
        path = os.path.join(sApp.user_data_dir, savename)
        print('#end_game#' + path)
        pickle.dump(sApp.game, open(path, 'wb'))

        sApp.game = None #should we clear this here??
        sApp.root.switch_to(MenuScreen())
        return True


class RandyScreenManager(ScreenManager):
    def go_back(self):
        # GO BACK TO THE PREVIOUS SCREEN
        # will have to track screens or something bc screenmanager doesn't do that
        pass

    #timer might also sit here?


class StatsApp(App):
    def __init__(self):
        super(StatsApp, self).__init__()

        #i guess here we need to check for and possibly also import


        self.current_point = None
        self.game = None
        self.teamfilenames = None
        # these are used to carry information before we have it all
        # when we have all the info we dump it into a Point as current_point
        self.temp_offence = None
        self.temp_oline = []
        self.temp_dline = []

    def build(self):
        sApp = App.get_running_app()
        return Builder.load_file(u'stats.kv')

    def save_game(self, *args):
        # popup confirmation is for nerds
        sApp = App.get_running_app()
        savename = sApp.game.tournament.strip() + u'_' + sApp.game.team_names[0].strip() + "v" + sApp.game.team_names[1].strip() + ".p"
        path = os.path.join(sApp.user_data_dir, savename)
        print('#save_game#' + path)
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
        # this won't work because it's saving properly now
        # load most recent game ???
        # sort files by date modified - pick most recent and load that
        # start timestamping saves !! - this is for choosing which game to load
        # YYMMDD at the start of a filename will alphabetically sort by game date < good


        sApp = App.get_running_app()
        tempsave = os.path.join(sApp.user_data_dir, 'tempsave.p')
        sApp.game = pickle.load(open(tempsave, 'rb'))
        os.remove(tempsave)
        pass
        # def on_start(self):
        #     pass
        # def on_stop(self):
        #     pass

    def import_config(self, filenames):
        if filenames is not None:
            teamnames = []
            teams = []

            sApp = App.get_running_app()
            for filename in filenames:
                full_path = os.path.join(sApp.user_data_dir, 'teamlists', filename)
                file = open(full_path, u'rb')
                # print('file opened #RANDY')

                for line in file.readlines():
                    key, value = line.split(u':')
                    if key == u'name':
                        teamnames.append(value)
                    elif key == u'players':
                        team = value.split(u',')
                        for player in team:
                            player = player.strip()
                        # trailing newline on last player
                        teams.append(team)
                file.close()

            file = open(os.path.join(sApp.user_data_dir, struct.cfg_filename), u'rb')
            for line in file.readlines():
                key, value = line.split(u':')
                if key == u'time_cap':
                    time_cap = value
                elif key == u'tournament_name':
                    tournament_name = value
                elif key == u'points_cap':
                    points_cap = value
                else:
                    pass
                    #print(key,value)
            file.close()

            game = Game(tournament_name, time_cap, points_cap, teams, teamnames)
            return game

        else:
            return None


if __name__ == u'__main__':
    a = StatsApp()
    a.run()
