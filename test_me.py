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
import numpy as np
import argparse
import re

from nba_api.stats.static import players as player_ref
import nbashots as nba_chart

#
# x_values = np.linspace(-np.pi, np.pi, 1000)
#
#
# # Equation 1
# equation1 = (np.multiply(
#     np.power(np.e, -x_values),
#     np.sin(np.multiply(x_values, 10)))
# )
#
#
# plt.plot(x_values, equation1, 'r')
#
# plt.xticks(ticks=[-np.pi, -np.pi/2, 0, np.pi/2, np.pi],
#            labels=['-pi', '-pi/2', '0', 'pi/2', 'pi'])
# plt.show()

class PlayerInfo(object):

    def __init__(self, player_lastname, player_firstname):
        """Class to calculate account amount.

        :param float amount_original:
            Amount of money in a bank account initially.

        :param float interest_rate:
            Rate of interest for the account specified in a decimal.

        :param int time:
            Number of years the account will compound over given as integer.

        :param int compound:
            Enum corresponding to the compound rate.

        """
        super(PlayerInfo, self)

        self.player_id = None

        player_id = self.player_reg_expression(player_lastname, player_firstname)
        test_value = self.get_player_id(player_id)

        if test_value:
            self.player_id = test_value

    def player_reg_expression(self, player_lastname, player_firstname):
        """Match user input to legal nba player.

        :param basestring player_lastname:
            Last name of an NBA Player provided by user.

        :param basestring player_firstname:
            First name of an NBA Player provided by user.

        :returns Legal player ID
        :rtype int
        """
        player_dict = player_ref.get_players()

        for i in range(len(player_dict)):
            if re.search((player_dict[i]['last_name']).lower(), player_lastname.lower()):
                if re.search((player_dict[i]['first_name']).lower(), player_firstname.lower()):
                     return player_dict[i]['id']

    def get_player_id(self, player_id):
        """Docstring"""
        test_value = player_id
        return test_value



def main():

    player = input(
        "Please provide an NBA player to analyze in the format of Lastname, Firstname:")

    try:
        last_name, first_name = player.split(',')
    except ValueError:
        print("Did not provide correct format check your comma.")
    else:
        PlayerInfo(last_name, first_name)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='nba-analytics', description='Run NBA Analytics with provided player.')

    args = parser.parse_args()
    main()