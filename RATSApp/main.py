#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard library
from __future__ import absolute_import
import pickle
from functools import partial
import copy
import csv
from io import open
import os, time

# kivy
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

#stats
import analysis as anal
import raw_game_hierarchy as hierarch

#the app needs to run on android better hence:
import storage_operations as stops



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
        sApp.root.switch_to(ConfirmInputScreen())
        return True

    def goto_continue_stats(self):
        sApp = App.get_running_app()
        sApp.root.switch_to(ChooseStatsScreen())
        return True


    # deactivate this so you can't accidentally fuck it all up

    def goto_read_stats(self):
        #sApp = App.get_running_app()
        #sApp.root.switch_to(ExportScreen())
        return True


class ConfirmInputScreen(Screen):
    def __init__(self, **kwargs):
        super(ConfirmInputScreen, self).__init__(**kwargs)
        sApp = App.get_running_app()

        configpath = os.path.join(sApp.user_data_dir,'AUSvJPNTestMatches.cfg')
        sApp.tournament_data = stops.import_config(configpath)

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
        # TODO: move this to stops
        # the stick in the mud here is the Player instantiation

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
                    team_name = value.strip()
                elif key == u'players':
                    team = value.split(u',')
                    for player in team:
                        try:
                            number, gender, name = player.split(u'|')
                        except:
                            name = player
                            number = 0
                            gender = 'u'

                        player_obj = hierarch.Player(player_name=name.strip(),
                                                     player_number=number,
                                                     player_gender=gender)
                        players.append(player_obj)


            team = hierarch.Team(team_name=team_name,
                                 team_players=players)  # division='very mixed')

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


        keywords = sApp.tournament_data
        keywords.append(['teams', teams])
        # keywords.append(['game_stage','default_stage'])
        keywords = dict(sApp.tournament_data)
        sApp.game = hierarch.Game(**keywords)

        sApp.root.switch_to(SelectPlayersScreen())
        return True


class SelectPlayersScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectPlayersScreen, self).__init__(**kwargs)
        sApp = App.get_running_app()
        if len(sApp.game.points) == 0: # if this is the first point
            #print('# this is the first point')
            self.offence = 0
            self.score = [0,0]
        elif sApp.current_point == 'HALF_REACHED': # if this is the first point after half
            self.offence = 1
            self.score = sApp.game.points[-1].score
            sApp.current_point = None
        else:
            self.offence = 1 - sApp.game.points[-1].current_sequence().offence # opposite offence to end of last point
            #print('new offence: '+str(self.offence))
            self.score = sApp.game.points[-1].score
        self.temp_oline = []
        self.temp_dline = []
        self.defence_timeouts_flagged = []
        self.offence_timeouts_flagged = []

        self.offenceTObutton = Button(text='Take Timeout - '+str(sApp.game.timeout_status[self.offence])+' taken so far')
        self.offenceTObutton.bind(on_release=partial(self.start_point_timeout,self.offence))
        self.ids.LeftBox.add_widget(self.offenceTObutton)

        teamLabel = Label(text=sApp.game.teams[self.offence].team_name)
        self.ids.LeftBox.add_widget(teamLabel)
        for player in sApp.game.teams[self.offence].team_players:
            pb = ToggleButton(text=player.display_name)
            pb.bind(on_release=partial(self.swap_state, pb, player))
            self.ids.LeftBox.add_widget(pb)

        self.defenceTObutton = Button(text='Take Timeout - ' + str(sApp.game.timeout_status[1-self.offence]) + ' taken so far')
        self.defenceTObutton.bind(on_release=partial(self.start_point_timeout,1-self.offence))
        self.ids.RightBox.add_widget(self.defenceTObutton)

        teamLabel = Label(text=sApp.game.teams[1 - self.offence].team_name)
        self.ids.RightBox.add_widget(teamLabel)
        for player in sApp.game.teams[1 - self.offence].team_players:
            pb = ToggleButton(text=player.display_name)
            pb.bind(on_release=partial(self.swap_state, pb, player))
            self.ids.RightBox.add_widget(pb)

    def start_point_timeout(self,offence_source,*args):
        sApp = App.get_running_app()
        if offence_source == self.offence: # offence called the TO
            sApp.game.timeout_status[self.offence] = sApp.game.timeout_status[self.offence] + 1
            self.offenceTObutton.text = 'Take Timeout - '+str(sApp.game.timeout_status[self.offence])+' taken so far'
            # create the event and timestamp it here, append to this list and chuck it on the sequence later
            fakePlayer = hierarch.Player(player_name=sApp.game.teams[self.offence].team_name,
                                         player_number=-1,
                                         player_gender='T')
            self.offence_timeouts_flagged.append(hierarch.Event(event_player=fakePlayer,
                                                                event_action='timeout',
                                                                ts_start=time.time(),
                                                                ts_end=time.time()+75))

        elif offence_source == 1-self.offence: # defence gets to call them here too
            sApp.game.timeout_status[1-self.offence] = sApp.game.timeout_status[1-self.offence] + 1
            self.defenceTObutton.text = 'Take Timeout - '+str(sApp.game.timeout_status[1-self.offence])+' taken so far'
            fakePlayer = hierarch.Player(player_name=sApp.game.teams[1-self.offence].team_name,
                                         player_number=-1,
                                         player_gender='T')
            self.defence_timeouts_flagged.append(hierarch.Event(event_player=fakePlayer,
                                                                event_action='timeout',
                                                                ts_start=time.time(),
                                                                ts_end=time.time()+75))

        return True

    def swap_state(self,pb,player,*args):
        # this is the NEW state - normal button pressed will trigger the if 'down' branch of this
        # offence here is just for checking which team the call is coming from and hence which list to edit
        sApp = App.get_running_app()
        if pb.state == 'normal':
            if player in sApp.game.teams[1 - self.offence].team_players:
                self.temp_dline.remove(player)
            else:
                self.temp_oline.remove(player)
        elif pb.state == 'down':
            if player in sApp.game.teams[1 - self.offence].team_players:
                self.temp_dline.append(player)
            else:
                self.temp_oline.append(player)
        else:
            print('something is broken in the state switching of player selection')
        self.ids.subtitle.text = 'Offence: '+str(len(self.temp_oline))+' | Defence: '+str(len(self.temp_dline))
        return True

    def store_players(self):
        sApp = App.get_running_app()
        # gender ratio?
        # beach ultimate?
        if len(self.temp_dline) == 7 and len(self.temp_oline) == 7:
            # if self.offence = 0, starting offence is on offence now
            # if self.offence = 1, the other team is on offence
            # thus the lines should match this - even
            # TODO: test this thoroughly

            if self.offence == 0:
                lines = [self.temp_oline,self.temp_dline] # this is it here
            elif self.offence == 1:
                lines = [self.temp_dline,self.temp_oline]

            # self.offence still matches the correct team in self.game.teams
            # and it reflects the reality of this point - the parameters have changed since the goal

            if len(sApp.game.points) != 0:
                self.score = sApp.game.points[-1].score
            else:
                self.score = [0,0]
            #print("making Point, off: "+str(self.offence))
            sApp.current_point = hierarch.Point(score=self.score,
                                                starting_offence=self.offence)

            sApp.current_point.create_sequence(lines=lines,
                                               offence=self.offence)

            for event in self.offence_timeouts_flagged:
                sApp.current_point.current_sequence().events.append(event)
            for event in self.defence_timeouts_flagged:
                sApp.current_point.current_sequence().events.append(event)

            sApp.root.switch_to(PullingScreen())
        else:
            pass
        return True


class PullingScreen(Screen):
    def __init__(self, **kwargs):
        super(PullingScreen, self).__init__(**kwargs)
        sApp = App.get_running_app()
        self.puller = 'puller_not_set'
        # print("starting pulling, off: "+str(sApp.current_point.current_sequence().offence))
        for player in sApp.current_point.current_sequence().lines[1 - sApp.current_point.current_sequence().offence]:
            pb = ToggleButton(text=player.display_name, group=u'players')
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
                                 pull_reception=outcome)
            if outcome == u'dropped-pull':

                sApp.current_point.current_sequence().offence = 1 - sApp.current_point.current_sequence().offence
                print('dropped pull, new offence:'+str(sApp.current_point.current_sequence().offence))

            sApp.root.switch_to(SelectActionScreen())

        return True

class PlayBreakScreen(Screen):
    def __init__(self,**kwargs):
        super(PlayBreakScreen,self).__init__(**kwargs)
        sApp = App.get_running_app()

        self.new_lines = []
        self.player_off_def = None
        self.player_off_off = None
        self.player_on_def = None
        self.player_on_off = None

        # offer choice of timeout or injury (or other/back)
        self.ids.BigBox.add_widget(Label(text='Break in Play:'))

        timeout_readout = 'TOs taken '+sApp.game.teams[0].team_name+': '+str(sApp.game.timeout_status[0])+' | TOs taken '+sApp.game.teams[1].team_name+': '+str(sApp.game.timeout_status[1])
        self.ids.BigBox.add_widget(Label(text=timeout_readout))

        toBut = Button(text='Timeout')
        toBut.bind(on_release=self.do_timeout)
        self.ids.BigBox.add_widget(toBut)

        injBut = Button(text='Injury')
        injBut.bind(on_release=self.do_injury)
        self.ids.BigBox.add_widget(injBut)

        # could probably put the edit button here too
        # edit or undo who knows

        backBut = Button(text='Back to Build Event')
        backBut.bind(on_release=self.go_back)
        self.ids.BigBox.add_widget(backBut)

    def go_back(self,*args):
        sApp = App.get_running_app()
        sApp.root.switch_to(SelectActionScreen())
        return True

    def do_injury(self,*args):
        # 2x popup - who's going off, who's coming on
        sApp = App.get_running_app()
        offcontent = BoxLayout(orientation=u'horizontal')
        offLeftBox = BoxLayout(orientation=u'vertical')
        offRightBox = BoxLayout(orientation=u'vertical')
        offcontent.add_widget(offLeftBox)
        offcontent.add_widget(offRightBox)

        teamLabelO = Label(text=sApp.game.teams[sApp.current_point.current_sequence().offence].team_name)
        offLeftBox.add_widget(teamLabelO)

        noButoff = ToggleButton(text='noone',group='offence')
        nocallback = partial(self.set_injured,'none_offence')
        noButoff.bind(on_release=nocallback)
        offLeftBox.add_widget(noButoff)
        for player in sApp.current_point.current_sequence().lines[sApp.current_point.current_sequence().offence]:
            pb = ToggleButton(text=player.display_name,group='offence')
            pbcallback = partial(self.set_injured, player)
            pb.bind(on_release=pbcallback)
            offLeftBox.add_widget(pb)

        teamLabelD = Label(text=sApp.game.teams[1-sApp.current_point.current_sequence().offence].team_name)
        offRightBox.add_widget(teamLabelD)

        noButdef = ToggleButton(text='noone',group='defence')
        nocallback = partial(self.set_injured, 'none_defence')
        noButdef.bind(on_release=nocallback)
        offRightBox.add_widget(noButdef)
        for player in sApp.current_point.current_sequence().lines[1 - sApp.current_point.current_sequence().offence]:
            pb = ToggleButton(text=player.display_name,group='defence')
            pbcallback = partial(self.set_injured, player)
            pb.bind(on_release=pbcallback)
            offRightBox.add_widget(pb)

        confBut = Button(text='Confirm Sub Off')
        confBut.bind(on_release=self.confirm_off)
        offcontent.add_widget(confBut)

        self.offpopup = Popup(title=u"Who's going off?",
                           content=offcontent,
                           size_hint=[0.7, 0.7])

        self.offpopup.open()
        return True

    def set_injured(self,player,*args):
        sApp = App.get_running_app()

        # it's ok that this checks object instead of the name variable
        # because we haven't copied into self.new_lines yet
        # that happens when we confirm injured
        if player in sApp.current_point.current_sequence().lines[sApp.current_point.current_sequence().offence]:
            self.player_off_off = player
        elif player in sApp.current_point.current_sequence().lines[1-sApp.current_point.current_sequence().offence]:
            self.player_off_def = player
        elif player == 'none_offence':
            self.player_off_off = None
        elif player == 'none_defence':
            self.player_off_def = None

        else:
            print('we fucked it - OFF player not on either team and not expected none_*')
            print(player)

        return True

    def confirm_off(self,*args):

        sApp = App.get_running_app()
        self.new_lines = copy.deepcopy(sApp.current_point.current_sequence().lines)
        self.oncontent = BoxLayout(orientation=u'horizontal')

        if self.player_off_off:
            team_players = sApp.game.teams[sApp.current_point.current_sequence().offence].team_players
            line_players = self.new_lines[sApp.current_point.current_sequence().offence]
            o_sideline_players = [a for a in team_players + line_players if (a.player_name not in [b.player_name for b in team_players]) or (a.player_name not in [c.player_name for c in line_players])]

            onLeftBox = BoxLayout(orientation=u'vertical')
            teamLabelO = Label(text=sApp.game.teams[sApp.current_point.current_sequence().offence].team_name)
            onLeftBox.add_widget(teamLabelO)

            for player in o_sideline_players:
                pb = ToggleButton(text=player.display_name,group='offence')
                pbcallback = partial(self.set_substitute, player)
                pb.bind(on_release=pbcallback)
                onLeftBox.add_widget(pb)
            for player in self.new_lines[sApp.current_point.current_sequence().offence]:
                if player.player_name == self.player_off_off.player_name: # same player not same object
                    self.new_lines[sApp.current_point.current_sequence().offence].remove(player)
            self.oncontent.add_widget(onLeftBox)

        if self.player_off_def:
            team_players = sApp.game.teams[1-sApp.current_point.current_sequence().offence].team_players
            line_players = self.new_lines[1-sApp.current_point.current_sequence().offence]
            d_sideline_players = [a for a in team_players + line_players if (a.player_name not in [b.player_name for b in team_players]) or (a.player_name not in [c.player_name for c in line_players])]

            onRightBox = BoxLayout(orientation=u'vertical')
            teamLabelD = Label(text=sApp.game.teams[1-sApp.current_point.current_sequence().offence].team_name)
            onRightBox.add_widget(teamLabelD)
            for player in d_sideline_players:
                pb = ToggleButton(text=player.display_name,group='defence')
                pbcallback = partial(self.set_substitute, player)
                pb.bind(on_release=pbcallback)
                onRightBox.add_widget(pb)
            for player in self.new_lines[1-sApp.current_point.current_sequence().offence]:
                if player.player_name == self.player_off_def.player_name: # same player not same object
                    self.new_lines[1-sApp.current_point.current_sequence().offence].remove(player)
            self.oncontent.add_widget(onRightBox)

        onBut = Button(text='Confirm Subs')
        onBut.bind(on_release=self.confirm_on)
        self.oncontent.add_widget(onBut)
        self.onpopup = Popup(title=u"Who's coming on?",
                           content=self.oncontent,
                           size_hint=[0.9, 0.9])

        self.offpopup.open()

        self.offpopup.dismiss()
        self.onpopup.open()
        # remove the players going off

        # hit this after selected players to go off
        # define the new popup, close the old, open the new
        # second popup will return you to SelectAction when you're done
        # ideally only offer player selection for the team if noone went off

        return True

    def set_substitute(self,player,*args):
        sApp = App.get_running_app()

        # of course they're not in the current_point lines, they're from the sideline
        if player.player_name in [a.player_name for a in sApp.game.teams[sApp.current_point.current_sequence().offence].team_players]:
            self.player_on_off = player
        elif player.player_name in [a.player_name for a in sApp.game.teams[1-sApp.current_point.current_sequence().offence].team_players]:
            self.player_on_def = player
        # you do have to sub somebody back on
        else:
            print('we fucked it - ON player not on either team')
            print(player)

        return True

    def confirm_on(self,*args):
        sApp = App.get_running_app()
        if self.player_on_off:
            self.new_lines[sApp.current_point.current_sequence().offence].append(self.player_on_off)
        if self.player_on_def:
            self.new_lines[1-sApp.current_point.current_sequence().offence].append(self.player_on_def)

        sApp.current_point.create_sequence(lines=self.new_lines,
                                           offence=sApp.current_point.current_sequence().offence)
        self.onpopup.dismiss()

        sApp.root.switch_to(SelectActionScreen())
        return True

    def do_timeout(self,*args):
        # only offence can call a timeout
        sApp = App.get_running_app()
        to_content = BoxLayout(orientation=u'vertical')
        for player in sApp.current_point.current_sequence().lines[sApp.current_point.current_sequence().offence]:
            pb = Button(text=player.display_name)
            pbcallback = partial(self.choose_to_caller, player)
            pb.bind(on_release=pbcallback)
            to_content.add_widget(pb)

        self.to_popup = Popup(title='Who called the timeout?',
                         content=to_content,
                         size_hint=[0.7,0.7])
        self.to_popup.open()
        return True

    def choose_to_caller(self,player,*args):
        sApp = App.get_running_app()
        sApp.game.timeout_status[sApp.current_point.current_sequence().offence] = sApp.game.timeout_status[sApp.current_point.current_sequence().offence] + 1
        to_obj = hierarch.Event(event_player=player,
                                event_action='timeout',
                                ts_start=time.time(),
                                ts_end=time.time()+75)
        sApp.current_point.current_sequence().events.append(to_obj)
        self.to_popup.dismiss()
        sApp.root.switch_to(SelectActionScreen())
        return True

class SelectActionScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectActionScreen, self).__init__(**kwargs)

        self.popup = None
        self.temp_event = ['player_not_set', None, None, None]  # [player, action, ts_start, ts_end]
        self.pblist = []
        sApp = App.get_running_app()

        # sequence_display = Label(text=str(seq_content),pos_hint={'top':1})
        # not sure pos_hint works very well - possibly bc i never use it and hence am mixing
        # this is the shit to fix with the UI restructure hey
        self.update_sequence()

        for player in sApp.current_point.current_sequence().lines[sApp.current_point.current_sequence().offence]:
            pb = ToggleButton(text=player.display_name, group=u'players')
            pickcallback = partial(self.set_player, player)
            pb.bind(on_release=pickcallback)
            self.pblist.append(pb)
            self.ids.LeftBox.add_widget(pb)

        fakePlayer = hierarch.Player(player_name=sApp.game.teams[sApp.current_point.current_sequence().offence].team_name,
                                     player_number=-1,
                                     player_gender='G')
        pb = ToggleButton(text=fakePlayer.display_name, group=u'players')
        pickcallback = partial(self.set_player,fakePlayer)
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

        playBreakButton = Button(text='Break in play')
        playBreakButton.bind(on_release=self.playbreak_switch)
        self.ids.RightBox.add_widget(playBreakButton)

        undoButton = Button(text='Undo Event')
        # undocallback = partial(self.undo_action)
        undoButton.bind(on_release=self.undo_action)
        self.ids.RightBox.add_widget(undoButton)

    def playbreak_switch(self,*args):
        sApp = App.get_running_app()
        sApp.root.switch_to(PlayBreakScreen())
        return True

    def undo_action(self,*args):

        # works fine for regular actions
        # can't undo goals
        sApp = App.get_running_app()

        if len(sApp.current_point.current_sequence().events) != 0: # misclick protection

            ditched = sApp.current_point.current_sequence().events.pop()
            if ditched.event_action in hierarch.Event.turnover_actions:
                sApp.current_point.current_sequence().offence = 1-sApp.current_point.current_sequence().offence
            print('## undo ## ' + str(ditched))
            sApp.root.switch_to(SelectActionScreen())

        return True

    def set_player(self, player, *args):
        sApp = App.get_running_app()
        self.temp_event[0] = player
        self.temp_event[2] = time.time()
        return True

    def update_sequence(self): # only need *args+return True if calling this from a button press
        # seems to be working well
        sApp = App.get_running_app()
        # this is the only dynamic text on this screen i think
        seq_content = []  # there is already a title on this shit
        for event in sApp.current_point.current_sequence().events[-3:]:  # last three events
            seq_content.append(str(event.event_player.display_name) + ' : ' + str(event.event_action))
        self.ids.SequenceLabel.text = str(seq_content)
        # return True

    def set_action(self, action, *args):
        # store the event
        sApp = App.get_running_app()
        if self.temp_event[0] != 'player_not_set':
            #button does nothing if haven't picked a player
            self.temp_event[1] = action
            self.temp_event[3] = time.time()

            event_obj = hierarch.Event(event_player=self.temp_event[0],
                                       event_action=self.temp_event[1],
                                       ts_start=self.temp_event[2],
                                       ts_end=self.temp_event[3])

            sApp.current_point.current_sequence().events.append(copy.copy(event_obj)) # if you fuck with event_obj from here, doesn't touch sequence

            # having the seq display here means that it updates every time you select action - good
            # needs to update all the time - on entry to the screen as well as any action button
            self.update_sequence()

            stops.store_game_pickle(sApp.game,sApp.save_path(special='_auto'))
            for pb in self.pblist:
                pb.state = u'normal' # reset the player buttons
            self.temp_event = ['player_not_set',None,None,None]

            # offensive turnovers
            if event_obj.event_action in hierarch.Event.turnover_actions and event_obj.event_action not in hierarch.Event.defensive_actions:
                #print("- offensive turnover")
                sApp.current_point.current_sequence().offence = 1 - sApp.current_point.current_sequence().offence
                sApp.root.switch_to(SelectActionScreen())
            # defensive turnovers
            if event_obj.event_action in hierarch.Event.defensive_actions:
                popupContent = BoxLayout(orientation=u'vertical')
                for player in sApp.current_point.current_sequence().lines[1-sApp.current_point.current_sequence().offence]:
                    pb = Button(text=player.display_name)
                    pbcallback = partial(self.save_defensive_action, player , event_obj.event_action)
                    pb.bind(on_release=pbcallback)
                    popupContent.add_widget(pb)

                self.popup = Popup(title=u'who got the block/int',
                                   content=popupContent,
                                   size_hint=[0.7, 0.7])
                self.popup.open()

            if event_obj.event_action == u'goal':
                # change this to the stacked or whatever, even x/y  boxex
                popupContent = BoxLayout(orientation='vertical')
                # print('end point, off: '+str(sApp.current_point.current_sequence().offence))
                sApp.current_point.score[sApp.current_point.current_sequence().offence] += 1

                teamLabel = Label(text = 'teams:['+str(sApp.game.teams[0].team_name)+','+str(sApp.game.teams[1].team_name)+']')
                scoreLabel = Label(text = 'score:'+str(sApp.current_point.score))
                popupContent.add_widget(teamLabel)
                popupContent.add_widget(scoreLabel)

                yes = Button(text=u'yes')
                yes.bind(on_release=self.end_game)
                popupContent.add_widget(yes)

                half = Button(text=u"that's half")
                half.bind(on_release=self.end_half)
                popupContent.add_widget(half)

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
        print('##defensive action - '+str(action))
        blockevent = hierarch.Event(event_player=player,
                                    event_action=action,
                                    ts_start=time.time())
                                    
        sApp.current_point.current_sequence().events.append(blockevent)
        sApp.current_point.current_sequence().offence = 1 - sApp.current_point.current_sequence().offence
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

    def end_half(self, *args):
        if self.popup:
            self.popup.dismiss()
        sApp = App.get_running_app()
        sApp.game.points.append(sApp.current_point)
        sApp.current_point = 'HALF_REACHED'
        # how dodgy is this - its only for literally this one function pass
        # fuck you
        stops.store_game_pickle(sApp.game,sApp.save_path(special='_half'))

        sApp.root.switch_to(SelectPlayersScreen())
        return True

    def end_game(self, *args):
        if self.popup:
            self.popup.dismiss()
        sApp = App.get_running_app()
        sApp.game.points.append(sApp.current_point)
        #sApp.game.time_game_end = time.time()
        stops.store_game_pickle(sApp.game,sApp.save_path(special='_final'))

        sApp.game = None #should we clear this here??
        sApp.unordered_teams = []
        sApp.root.switch_to(MenuScreen())
        return True


# these are important but not part of the live stat taking - consider breaking up screen definitions

# this is where you can select a game file and continue on from the end
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
        sApp.game = stops.retrieve_game_pickle(self.path)
        #
        # for some reason in the SMO ellipsis v rogue game there was a None object saved in the pointslist, crashing it
        # this is clearly a workaround - why the None ??
        # ^ when is current_point == None (sometimes)
        # ^ how would it get stored during those times - on_pause probably
        #
        # - works still -
        #
        for point in sApp.game.points:
            if point == None:
                print("Detected a NoneType obj in game.points, discarding")
                sApp.game.points.remove(point)

        sApp.root.switch_to(SelectPlayersScreen())

# strictly experimental - don't go here

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
            # anal.gdrive_text(stops.get_credentials())
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


class ExportScreen(Screen):
    def __init__(self, **kwargs):
        super(ExportScreen, self).__init__(**kwargs)

        # here i want to come in and have you choose which game to export
        # then export the basic stats to a csv file
        # then upload that to our gdrive
        #

        sApp = App.get_running_app()
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
        return stops.import_config(filenames)

    def on_enter(self):
        pass


class RatsScreenManager(ScreenManager):
    def go_back(self):
        # GO BACK TO THE PREVIOUS SCREEN
        # this functionality will probably require redoing switch_to
        # or some shit who knows
        #
        pass


class StatsApp(App):
    def __init__(self):
        super(StatsApp, self).__init__()

        self.tournament_data = None
        self.current_point = None
        self.current_seq = None
        self.game = None
        # game files aren't currently linked to tournament objects

        self.unordered_teams = [] # read in teams, check whos on offence next screen

    def build(self):
        sApp = App.get_running_app()
        return Builder.load_file(u'stats.kv')

    def save_path(self,special=None):
        # popup confirmation is for nerds
        sApp = App.get_running_app()
        savename = sApp.game.get_filename(special=special)
        path = os.path.join(sApp.user_data_dir, savename)

        if special != '_auto':
            print('## saving special ##'+str(path))

        return path

    def on_pause(self):
        sApp = App.get_running_app()
        stops.store_game_pickle(sApp.game,sApp.save_path())
        return True

    def on_resume(self):
        return True


if __name__ == u'__main__':
    a = StatsApp()
    a.run()
