#!/usr/bin/env python
# -*- coding: utf-8 -*-

# team_scrape.py

# standard library
from __future__ import print_function
import os
import sys
import codecs
import urllib2

# third party
from bs4 import BeautifulSoup

# local project
import game_hierarchy


def make_soup(hyperlink):
    """Takes a hyperlink and returns a BeautifulSoup object."""

    request = urllib2.Request(hyperlink)
    response = urllib2.urlopen(request)
    return BeautifulSoup(response.read().decode("utf-8", "ignore"), "html.parser")


def find_divisions(soup):
    """Returns a list of teams and their hyperlinks for each non-Guts divisions at the tournament."""

    divisions = soup.find("div", class_="content").find_all("table")

    return [
        # divisions
        [
            division.th.string,  # division name
            # teams
            [
                [
                    [link.string, link.get("href")]
                    for link in table_row.find_all("a")
                ]
                # table rows loop
                for table_row in division.find_all("tr")
            ][1:],  # slice out division name
        ]
        # divisions loop
        for division in divisions if division.th.string != u"Guts"
    ]


def create_team(team_links, division):
    """Takes a list of team links and creates a Team object."""

    # print(division, ", ".join("{} {}".format(link[0], link[1]) for link in team_links))

    team_group = team_links[1][0]
    name_team = team_links[0][0]
    players_team = team_links[2][1]
    team_games = team_links[4][1]
    print(team_games)

    team_object = game_hierarchy.Team()

    print(team_object.games)

    return team_object


def main():
    soup = make_soup("http://scores.wugc2016.com/?view=teams&season=WUGC16&list=allteams")
    # print(soup.prettify())

    # division_tables = find_divisions(soup)
    #
    # # print(len(division_tables))
    #
    # for division in division_tables:
    #     # print(division)
    #
    #     for team_links in division[1]:
    #
    #         team_object = create_team(team_links, division[0])

    test_team = game_hierarchy.Team(
        group_name="RATS",
        team_name="STATS",
        team_players=["Rob", "Andy"],
        team_division="Very Mixed",
    )

if __name__ == u"__main__":
    sys.exit(main())
