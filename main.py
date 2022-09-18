import os
import numpy as np
import json
import re
import name_scraper
from improvement_data_scraper import grab_player_stats
import nonlinear_regression


def func(x, a, b, c):
    return np.e**(a*x+b)+c


def main(running_dir, num_pages):
    improvement_data_dir = os.path.join(running_dir, 'improvement_data')
    playerlist_filename = os.path.join(running_dir, 'playerlist.txt')
    if not os.path.exists(playerlist_filename):
        playerlist = name_scraper.write_playernames(
            num_pages, playerlist_filename)

    else:
        with open(playerlist_filename, "r") as f:
            playerlist = f.read().splitlines()
    print("Players Names Found")

    for i, player in enumerate(playerlist):
        if (not player) or os.path.exists(os.path.join(improvement_data_dir, f'jstris_data-{player}.tsv')):
            continue
        grab_player_stats(player)

    print("Improvement Data Found")

    regression_data = {}
    for improvement_data_path in os.listdir(improvement_data_dir):
        improvement_data_abspath = os.path.join(
            improvement_data_dir, improvement_data_path)
        player_data = nonlinear_regression.load_data(improvement_data_abspath)
        xData, yData = player_data["dayssincestart"], player_data["time"]

        # bad naming i know i know
        params = nonlinear_regression.non_linear_regression(
            func, xData, yData
        )

        metrics = nonlinear_regression.calculate_metrics(
            func, xData, yData, params
        )

        # nonlinear_regression.plot_regression(
        #     func, xData, yData, params
        # )

        regression_data[re.search(r'jstris_data-(.*?).tsv', improvement_data_path).group(1)] = {
            "params": params.tolist(),
            "metrics": metrics,
            "data_length": len(xData),
        }
        print(f"{params=}, {metrics=}")

    with open("regression_data.json", "w") as outfile:
        json.dump(regression_data, outfile)


if __name__ == "__main__":
    running_dir = os.path.dirname(os.path.realpath(__file__))
    main(running_dir, 1)
