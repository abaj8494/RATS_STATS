#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes an Ultimate Central Tournament url and extracts team lists for each division.
"""

# imports
# standard library
from __future__ import print_function
import os
import sys
import codecs
import urllib2

# third party
from bs4 import BeautifulSoup

# TODO: Division names are saved as user inputs because there is no Goddess. Need to build a regex to handle that.


def get_divisions(soup):
    """Returns a list of all tournament divisions."""

    # print(soup)

    division_menu = soup.find("select", id="division").find_all("option")  # find the division select menu
    all_divisions = [option.string for option in division_menu if option.string != u"All Divisions"]

    print(all_divisions)

    return all_divisions


def load_division(tournament_url, division):
    """Reloads the tournament page with the teams in the division and returns the page soup."""

    division_url = tournament_url + "/teams/division/" + division  # division hyperlink
    
    request = urllib2.Request(division_url)
    response = urllib2.urlopen(request)

    division_soup = BeautifulSoup(response.read().decode("utf-8", "ignore"), "html.parser")

    print(division_soup)

    return division_soup


def get_division_teams(division_soup):
    """Returns a dictionary with the keys as team names and the values as sets of players."""

    # TODO: include team numbers with names

    division_teams = {
        team.find("h3").string.title(): set(player.string.title() for player in team.find("ul").find_all("a"))
        for team in division_soup.find_all("div", class_="span4 media-item-wrapper spacer1 ")
    }

    print(division_teams)

    return division_teams


def write_team_text_file(tournament_abbreviation, team_entry):
    """Takes a tuple of a team and its players and writes it to a text file for the app.."""

    # TODO: save these to Google Drive in app.
    # TODO: we're importing text files but we could just be piping it to the program

    text_string = "team:{}".format(team_entry[0]) + "\nplayers:" + ", ".join(team_entry[1]) + "\n"

    print(text_string)

    file_path = os.path.join(
        os.getcwd(),  # working directory
        tournament_abbreviation,  # tournament directory
        "{}-{}.txt".format(tournament_abbreviation, team_entry[0].replace(" ", ""))  # team file
    )
    print(file_path)

    with codecs.open(file_path, mode="w+", encoding="utf-8") as text_file:
        text_file.write(text_string)

    return text_string


def main():
    """Takes an tournament link and returns a list of teams and their players in each division."""

    tournament_url = unicode(raw_input("Enter Tournament hyperlink: "))
    tournament_abbreviation = tournament_url.split("/")[-1]

    print("Tournament: {}".format(tournament_abbreviation))

    # create tournament directory
    if not os.path.exists(os.path.join(os.getcwd(), tournament_abbreviation)):
        os.makedirs(os.path.join(os.getcwd(), tournament_abbreviation))

    # open the web page
    request = urllib2.Request(tournament_url + "/teams")
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response.read().decode("utf-8", "ignore"), "html.parser")

    divisions = get_divisions(soup)

    for division in divisions:

        print("Division: {}".format(division))

        division_soup = load_division(tournament_url, division)
        division_teams = get_division_teams(division_soup)

        for team_entry in division_teams.iteritems():
            write_team_text_file(tournament_abbreviation, team_entry)

    print("Team lists saved!")


if __name__ == '__main__':
    sys.exit(main())
