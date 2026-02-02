import api
import data_visualization as dv
import os

menu = """
=======================================
        Basketball Stats Menu
=======================================
  [1] Single Player Stats
  [2] Compare Multiple Players (up to 3)
  [q] Quit
=======================================
"""

mode1_menu = """
==========================================
        Single Player Options
==========================================
  [1] Single Season Stats (Bar)
  [2] Career Stat Trend (Line, Multi Stat)
      (ppg / rpg / apg / spg / bpg)
  [b] Back
==========================================
"""

mode2_menu = """
=======================================
        Compare Players
=======================================
  [1] Single-Season Comparison (Bar)
  [2] Career Comparison (Line, One Stat)
  [b] Back
=======================================
"""

def print_seasons(seasons: list):
    '''
    Prints out seasons
    '''
    print("\n====== Available Seasons ======")
    command_index = 0
    n = len(seasons)
    if n <= 8:
        for s in seasons:
            print(f'[{command_index}]: {s}')
            command_index += 1
    else:
        half = (n + 1) // 2
        for i in range(half):
            left_index = i
            right_index = i + half

            left = f'[{left_index}]: {seasons[left_index]}'
            if right_index < n:
                right = f'[{right_index}]: {seasons[right_index]}'
            else:
                right = ''

            print(f"{left:<16} {right}")
    print()

def choose_season(career_seasons: list) -> int:
    """
    Returns a valid season index chosen by the user.
    """
    print_seasons(career_seasons)
    while True:
        season_input = input(
            "Choose a season by typing its corresponding number ([s]: to see seasons again): "
        ).strip()

        if season_input.lower() == "s":
            print_seasons(career_seasons)
            continue

        if not season_input.isdigit():
            print("\nERROR: Please enter a valid number.\n")
            continue

        idx = int(season_input)
        if idx < 0 or idx >= len(career_seasons):
            print("\nERROR: Invalid season! Try again.\n")
            continue

        return idx

def get_player_season_stats(label: str):
    """
    Prompts for player name until valid, then allows season selection.
    Returns dict: {name, league, player_id, season_label, stats}
    """

    while True:
        name_input = input(
            f"Please enter the name of {label} player (exact spelling/caps, or 'q' to cancel): "
        ).strip()

        if name_input.lower() == "q":
            return None  # caller decides what to do

        league, player_id = api.find_player(name_input)
        if not player_id:
            print("ERROR: Invalid name. Please try again.\n")
            continue

        career_df, career_seasons = api.get_player_career_seasons(player_id, league)

        season_idx = choose_season(career_seasons)
        stats = api.get_player_season_stats(career_df, season_idx)

        return {
            "name": name_input,
            "league": league,
            "player_id": player_id,
            "season_label": career_seasons[season_idx],
            "stats": stats,
        }

def run():
    while True:
        print(menu)
        mode = input("Select an option: ").strip().lower()

        if mode == "q":
            return False  # stop main loop

        if mode not in ("1", "2"):
            print("\nERROR: Choose 1 or 2.\n")
            continue

        made_graph = False  # <- track whether we actually generated a graph this cycle

        if mode == "1":
            while True:
                print(mode1_menu)
                sub = input("Select an option: ").strip().lower()

                if sub == "b":
                    break  # back to mode selection

                if sub == "1":
                    p = get_player_season_stats("the")
                    if p is None:
                        continue
                    filename = dv.make_stats_bar_graph([p])
                    print(f'\nSuccess! Graph created for {p["name"]} during the {p["season_label"]} season\nSaved to: {filename}\n')
                    made_graph = True
                    break  # <- go to "again" prompt

                if sub == "2":
                    p = api.get_player_career("the")
                    if p is None:
                        continue

                    stat_input = input("Enter stats separated by commas (ppg,rpg,apg,spg,bpg): ").strip().lower()
                    stat_codes = [s.strip() for s in stat_input.split(",") if s.strip()]

                    filename = dv.make_single_player_multi_stat_career_graph(p["name"], p["career_df"], stat_codes)
                    print("Saved to:", filename)

                    made_graph = True
                    break  # <- go to "again" prompt

                print("\nERROR: Choose 1, 2, or b.\n")

            if not made_graph:
                # user hit 'b' (back). restart outer loop to choose mode again
                continue

        else:  # mode == "2"
            while True:
                print(mode2_menu)
                sub = input("Select an option: ").strip().lower()

                if sub == "b":
                    break

                if sub not in ("1", "2"):
                    print("\nERROR: Choose 1, 2, or b.\n")
                    continue

                while True:
                    count_input = input("How many players to compare? (2-3): ").strip()
                    if count_input.isdigit() and 2 <= int(count_input) <= 3:
                        num_players = int(count_input)
                        break
                    print("\nERROR: Enter a number from 2 to 3.\n")

                # ===============================
                # BAR GRAPH (single season)
                # ===============================
                if sub == "1":
                    players_list = []
                    for i in range(num_players):
                        p = get_player_season_stats(f"Player {i+1}")
                        if p is None:
                            players_list = []
                            break
                        players_list.append(p)

                    if len(players_list) != num_players:
                        continue

                    filename = dv.make_stats_bar_graph(players_list)

                    names = " vs ".join(
                        [f'{p["name"]} ({p["season_label"]})' for p in players_list]
                    )
                    print(
                        f"\nSuccess! Bar comparison created: {names}"
                        f"\nSaved to: {filename}\n"
                    )
                    break  # go to "Make another graph?"

                # ===============================
                # LINE GRAPH (career, one stat)
                # ===============================
                if sub == "2":
                    players_list = []
                    for i in range(num_players):
                        p = api.get_player_career(f"Player {i+1}")
                        if p is None:
                            players_list = []
                            break
                        players_list.append(p)

                    if len(players_list) != num_players:
                        continue

                    stat_code = input(
                        "Which stat to compare? (ppg/rpg/apg/spg/bpg): "
                    ).strip().lower()

                    if stat_code not in ("ppg", "rpg", "apg", "spg", "bpg"):
                        print("\nERROR: Choose one of ppg/rpg/apg/spg/bpg.\n")
                        continue

                    filename = dv.make_multi_player_single_stat_career_graph(
                        players_list, stat_code
                    )

                    names = " vs ".join([p["name"] for p in players_list])
                    print(
                        f"\nSuccess! Career line comparison created: {names} ({stat_code.upper()})"
                        f"\nSaved to: {filename}\n"
                    )
                    break
        
        again = input("Make another graph? (y/n): ").strip().lower()
        if again != "y":
            return False  # stop main loop

def main():
    while True:
        keep_going = run()
        if not keep_going:
            break


if __name__ == "__main__":
    main()
