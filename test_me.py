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

    ::Note seaborn will crash and to fix, you must make these changes to:
site_packages > seaborn > rcmod.py

1. Add the following import statement:
import cycler

2. Change line 492 to this instead:
matplotlib.rcParams['axes.prop_cycle'] = cycler.cycler(color=colors)


"""
try:
    from pip._internal import main as install
except ModuleNotFoundError:
    from pip import main as install

import requests
import argparse
import re
import numpy as np

try:
    import matplotlib as mpl
    from matplotlib import colors
    from matplotlib import colorbar
    from matplotlib import pyplot as plt
    from matplotlib.patches import Circle, Rectangle, Arc
except ImportError:
    install(['install', 'matplotlib'])

try:
    import pandas
except ImportError:
    install(['install', 'pandas'])

try:
    import nba_api
except ImportError:
    install(['install', 'nba_api'])

try:
    import nbashots
except ImportError:
    install(['install', 'nbashots'])

from nba_api.stats.static import players as player_ref
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import commonplayerinfo


cdict = {
    'blue': [(0.0, 0.6313725709915161, 0.6313725709915161), (0.25, 0.4470588266849518, 0.4470588266849518), (0.5, 0.29019609093666077, 0.29019609093666077), (0.75, 0.11372549086809158, 0.11372549086809158), (1.0, 0.05098039284348488, 0.05098039284348488)],
    'green': [(0.0, 0.7333333492279053, 0.7333333492279053), (0.25, 0.572549045085907, 0.572549045085907), (0.5, 0.4156862795352936, 0.4156862795352936), (0.75, 0.0941176488995552, 0.0941176488995552), (1.0, 0.0, 0.0)],
    'red': [(0.0, 0.9882352948188782, 0.9882352948188782), (0.25, 0.9882352948188782, 0.9882352948188782), (0.5, 0.9843137264251709, 0.9843137264251709), (0.75, 0.7960784435272217, 0.7960784435272217), (1.0, 0.40392157435417175, 0.40392157435417175)]
}

mymap = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)


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

        # Set player specific information
        self.player_id = None
        self.team_id = None

        # Set DataFrame
        self.shot_df = None
        self.shooting_percentage = None
        self.hb_shot = None

        self.player_id = self.get_player_id(self.player_lastname, self.player_firstname)
        if self.player_id:
            self.team_id = self.get_team_id(self.player_id)
            self.shot_df = self.get_player_shot_info(self.player_id, self.team_id, self.num_games)
            self.shooting_percentage, self.hb_shot = self.get_player_shooting_pcts(self.shot_df)


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

        :returns DataFrame
        :rtype pandas.DataFrame
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
            shots = current_shot_chart_info.shot_chart_detail.data['data']
            headers = current_shot_chart_info.shot_chart_detail.data['headers']
            shot_df = pandas.DataFrame(shots, columns=headers)
            return shot_df

    def get_player_shooting_pcts(self, shot_df, gridnum=30):
        """Calculate shooting percentages for a player.

        :param DataFrame shot_df:
            pandas.DataFrame object containing shot and header information.
        :param int gridnum:
            Default grid size.

        :returns shooting_percentage, shot_made
        :rtype array
        """
        x = shot_df.LOC_X[shot_df['LOC_X'] < 425.1]
        y = shot_df.LOC_Y[shot_df['LOC_Y'] < 425.1]

        x_made = shot_df.LOC_X[(shot_df['SHOT_MADE_FLAG'] == 1) & (shot_df['LOC_X'] < 425.1)]
        y_made = shot_df.LOC_Y[(shot_df['SHOT_MADE_FLAG'] == 1) & (shot_df['LOC_Y'] < 425.1)]

        # Compute number of shots taken from each hexbin location
        hb_shot = plt.hexbin(x, y, gridsize=gridnum, extent=(-250, 250, 425, -50))
        plt.close()

        # Compute number of shots taken from each hexbin location
        hb_made = plt.hexbin(x_made, y_made, gridsize=gridnum, extent=(-250, 250, 425, -50))
        plt.close()

        # Compute shooting percentage, effectively calculating FGA / FGM
        shooting_pct_locations = hb_made.get_array() / hb_shot.get_array()
        print(shooting_pct_locations)

        # If a player takes 0 shots, make sure both FGA and FGM are set to 0 to null the data point
        shooting_pct_locations[np.isnan(shooting_pct_locations)] = 0
        print(shooting_pct_locations)
        return (shooting_pct_locations, hb_shot)


class ShotChart(object):

    def __init__(self, player_info):
        """Create and maintain matplotlib shot chart information.

        :param object player_info:
            Player information object.

        """
        super(ShotChart, self)

        self.player_info = player_info
        self.create_shot_chart_plot(
            self.player_info.shooting_percentage,
            self.player_info.hb_shot)

    @staticmethod
    def draw_court(ax=None, color="black", lw=2, outer_lines=False):
        """Create the court based on dimensions and places shapes accordingly.

        ::Note this method will draw a basketball court with respect to the x and y
        locations of the shot itself. The NBA API endpoint returns x and y coordinates
        with respect to under the basketball hoop as (0, 0). Therefore, these dimensions
        are calculated to be accurate only with respect to the NBA API endpoint.

        This was taken directly from nba_chart repo, which is a public repository.
        """
        if ax is None:
            ax = plt.gca()
        hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)
        backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)
        outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
        inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)
        top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)
        bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='dashed')
        restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)
        corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
        corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
        three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)
        center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
        center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)
        court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                          bottom_free_throw, restricted, corner_three_a,
                          corner_three_b, three_arc, center_outer_arc,
                          center_inner_arc]
        if outer_lines:
            outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False)
            court_elements.append(outer_lines)

        for element in court_elements:
            ax.add_patch(element)

        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        return ax

    def create_shot_chart_plot(self, shooting_pct, shot_num, plot_size=(12, 8), gridnum=30):
        """Show plot that has X and Y coordinate values for court."""

        # Draw figure and court
        fig = plt.figure(figsize=plot_size)

        # Where the plot places within the figure
        ax = plt.axes([0.1, 0.1, 0.8, 0.8])
        self.draw_court(outer_lines=False)

        plt.title("Shot chart for{} {} for the last {} games".format(
            self.player_info.player_firstname,
            self.player_info.player_lastname,
            self.player_info.num_games
        ))

        # Set court limits
        plt.xlim(-250, 250)
        plt.ylim(400, -25)

        for i, shots in enumerate(shooting_pct):
            restricted = Circle(shot_num.get_offsets()[i], radius=shot_num.get_array()[i],
                                color=mymap(shots), alpha=0.8, fill=True)
            if restricted.radius > 240 / gridnum: restricted.radius = 240 / gridnum
            ax.add_patch(restricted)

        # Draw color bar to indicate percentage as heatmap
        ax2 = fig.add_axes([0.92, 0.1, 0.02, 0.8])
        cb = mpl.colorbar.ColorbarBase(ax2, cmap=mymap, orientation='vertical')
        cb.set_label('Shooting %')
        cb.set_ticks([0.0, 0.25, 0.5, 0.75, 1.0])
        cb.set_ticklabels(['0%', '25%', '50%', '75%', '100%'])

        plt.show()
        return ax


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

    if num_games == 0:
        num_games = 82

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
