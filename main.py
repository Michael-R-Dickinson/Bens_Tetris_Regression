import os
import numpy as np
import json
import re
import name_scraper
from improvement_data_scraper import grab_player_stats
import nonlinear_regression
import warnings
from tqdm import tqdm


def func(x, a, b, c):
    return np.e**(a*x+b)+c


def main(running_dir, num_pages):
    improvement_data_dir = os.path.join(running_dir, 'improvement_data')
    playerlist_filename = os.path.join(running_dir, 'playerlist.txt')
    if not os.path.exists(playerlist_filename):
        playerlist = name_scraper.write_playernames(
            num_pages, playerlist_filename)

    else:
        with open(playerlist_filename, "r", encoding='utf-8') as f:
            playerlist = f.read().splitlines()
    print("Players Names Found")

    for player in tqdm(playerlist, desc="Scraping Improvement Data"):
        if (not player) or os.path.exists(os.path.join(improvement_data_dir, f'jstris_data-{player}.tsv')):
            continue
        try:
            grab_player_stats(player)

        except Exception as e:
            print(f"error {e} with {player}")

    print("Improvement Data Found")

    regression_data = {}
    if os.path.exists(os.path.join(running_dir, 'regression_data.json')):
        with open(os.path.join(running_dir, 'regression_data.json'), 'r') as f:
            precomputed_players = list(json.load(f).keys())

    for improvement_data_path in tqdm(os.listdir(improvement_data_dir), desc="Running Regressions"):
        playername = re.search(
            r'jstris_data-(.*?).tsv', improvement_data_path).group(1)
        if playername in precomputed_players:
            continue

        improvement_data_abspath = os.path.join(
            improvement_data_dir, improvement_data_path)
        player_data = nonlinear_regression.load_data(improvement_data_abspath)
        xData, yData = player_data["dayssincestart"], player_data["time"]

        with warnings.catch_warnings(record=True) as w:
            try:
                # bad naming i know i know
                params = nonlinear_regression.non_linear_regression(
                    func, xData, yData
                )

            except RuntimeError as e:
                print(f"error {e} with {playername}")
                continue

            metrics = nonlinear_regression.calculate_metrics(
                func, xData, yData, params
            )

            # nonlinear_regression.plot_regression(
            #     func, xData, yData, params
            # )

            regression_data[playername] = {
                "params": params.tolist(),
                "metrics": metrics,
                "timeplayed": int(max(player_data['dayssincestart'])),
                "gamesplayed": int(player_data['replay'].count()),
                "errors": [str(warning.message) for warning in w],
            }

    with open("regression_data.json", "w") as outfile:
        json.dump(regression_data, outfile)


if __name__ == "__main__":
    running_dir = os.path.dirname(os.path.realpath(__file__))
    main(running_dir, 40)
