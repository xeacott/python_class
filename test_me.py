# Project File


"""
This file serves as Dominick Bellofatto and Joe Eacott's CS2005 project.

The purpose of this file is to analyze NBA shot attempt information for a specific player
to create a model of shot makes/attempts. This statistic is called FGA, or field-goal-attempts,
which determines another statistic, which is FGM. These two statistics will give us a percentage
of how a player typically does scoring-wise for a game.

We can use this information to predict when a player may have above average night for shooting,
which people like to refer to as a "hot" game. We'll formally define a "hot" game as shooting
more than 7% above a player's average.

"""
import matplotlib.pyplot as plt
import numpy
import pandas
import requests
import argparse
import re

from nba_api.stats.static import players as player_ref
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import commonplayerinfo
import nbashots as nba_chart


class PlayerInfo(object):

    def __init__(self, player_lastname, player_firstname, num_games):
        """Information about player such as name, id, and shot dataframe info.

        :param basestring player_lastname:
            Last name of an NBA Player provided by user.

        :param basestring player_firstname:
            First name of an NBA Player provided by user.

        :param int time:
            Number of years the account will compound over given as integer.

        :param int compound:
            Enum corresponding to the compound rate.

        """
        super(PlayerInfo, self)

        self.player_lastname = player_lastname
        self.player_firstname = player_firstname
        self.num_games = num_games

        self.player_id = None
        self.team_id = None
        self.x_loc = []
        self.y_loc = []

        self.player_id = self.get_player_id(self.player_lastname, self.player_firstname)
        if self.player_id:
            self.team_id = self.get_team_id(self.player_id)
            self.get_player_shot_info(self.player_id, self.team_id, self.num_games)


    def get_player_id(self, player_lastname, player_firstname):
        """Match user input to legal nba player.

        :param basestring player_lastname:
            Last name of an NBA Player provided by user.

        :param basestring player_firstname:
            First name of an NBA Player provided by user.

        :returns Legal player ID
        :rtype int
        """
        player_dict = player_ref.get_players()
        player_id = None

        for i in range(len(player_dict)):
            if re.search((player_dict[i].get('last_name')).lower(), player_lastname.lower()):
                if re.search((player_dict[i].get('first_name')).lower(), player_firstname.lower()):
                    player_id = player_dict[i].get('id')

        if player_id is None:
            print("Player not found, check your spelling of {} or please choose another player.".format(
                player_lastname + player_firstname
            ))
        return player_id


    def get_team_id(self, player_id):
        """Match player id to team id which is necessary for shot info.

        :param int player_id:
            Player ID that is associated with player user provided.

        :returns team_id
        :rtype int
        """
        try:
            current_team_id = commonplayerinfo.CommonPlayerInfo(
                player_id=player_id
            )
        except requests.exceptions.ConnectionError:
            print("Request failed.")
        else:
            return current_team_id.common_player_info.data['data'][0][16]

    def get_player_shot_info(self, player_id, team_id, num_games):
        """Match player id to shot chart information.

        :param int player_id:
            Player ID that is associated with player user provided.

        :param int team_id:
            Team ID that is associated with the player user provided.

        :param int num_games:
            Indicate length of shot info to acquire.

        :returns object
        :rtype ShotChartDetail
        """
        try:
            current_shot_chart_info = shotchartdetail.ShotChartDetail(
                league_id='00',
                season_type_all_star='Regular Season',
                team_id=team_id,
                player_id=player_id,
                last_n_games=num_games
            )

        except requests.exceptions.ConnectionError:
            print("Request failed.")

        else:
            for i in range(len(current_shot_chart_info.shot_chart_detail.data['data'])):
                self.x_loc.append(current_shot_chart_info.shot_chart_detail.data['data'][i][17])
                self.y_loc.append(current_shot_chart_info.shot_chart_detail.data['data'][i][18])


class ShotChart(object):

    def __init__(self, player_info):
        """Create and maintain matplotlib shot chart information.

        :param object player_info:
            Player information object.

        """
        super(ShotChart, self)

        self.player_info = player_info
        self.x_series = pandas.Series(self.player_info.x_loc)
        self.y_series = pandas.Series(self.player_info.y_loc)

        self.create_shot_chart_plot()

    def create_shot_chart_plot(self):
        """Docstring."""

        nba_chart.shot_chart(self.x_series, self.y_series)
        plt.show()


def main():

    player = input(
        "Please provide an NBA player to analyze in the format of Lastname, Firstname.\n"
        "Here are a few examples to get started:\n"
        "{}\n"
        "{}\n"
        "{}\n"
        "Enter:".format(
            "Rose, Derrick",
            "James, LeBron",
            "Harden, James"
        ))

    num_games = int(input(
        "Enter the amount of games you'd like to view statistics for. This can be in the"
        "format of 10 games, 30 games, or say 0 to indicate a season-length.\n"
        "Enter:"
    ))


    try:
        last_name, first_name = player.split(',')
    except ValueError:
        print("Did not provide correct format for {}.".format(player))
    else:
        player_info = PlayerInfo(last_name, first_name, num_games)
        if player_info.player_id is not None:
            ShotChart(player_info)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='nba-analytics', description='Run NBA Analytics with provided player.')

    args = parser.parse_args()
    main()