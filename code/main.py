import api
import data_visualization as dv
import os


def print_seasons(seasons: list):
    '''
    Prints out seasons
    '''
    print("\n------ Available Seasons ------")
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
        stats = api.get_stats_from_season(career_df, season_idx)

        return {
            "name": name_input,
            "league": league,
            "player_id": player_id,
            "season_label": career_seasons[season_idx],
            "stats": stats,
        }

def run():
    while True:
        mode = input("Mode: [1] Single player graph, [2] Compare two players: ").strip()

        if mode == "1":
            p = get_player_season_stats("the")
            if p is None:
                # invalid name -> go back to choosing mode again (or you could retry name inside that function)
                print("\nTry again.\n")
                continue

            dv.make_graph(p["name"], p["stats"], p["season_label"])
            print(f'\nSuccess! Graph created for {p["name"]} during the {p["season_label"]} season.\n')
            return False  # or return True depending on how your main loop is set up

        elif mode == "2":
            p1 = get_player_season_stats("Player 1")
            if p1 is None:
                print("\nTry again.\n")
                continue

            p2 = get_player_season_stats("Player 2")
            if p2 is None:
                print("\nTry again.\n")
                continue

            dv.make_comparison_graph(
                p1_name=p1["name"],
                p1_stats=p1["stats"],
                p1_season=p1["season_label"],
                p2_name=p2["name"],
                p2_stats=p2["stats"],
                p2_season=p2["season_label"],
            )

            print(
                f'\nSuccess! Comparison graph created: {p1["name"]} ({p1["season_label"]}) vs '
                f'{p2["name"]} ({p2["season_label"]}).\n'
            )
            return False  # or return True depending on your main loop

        else:
            print("\nERROR: Choose 1 or 2.\n")
            # stays in the while loop and asks again


def main():
    # For personal testing
    os.system('ipconfig /flushdns > nul 2>&1')

    print('\nWelcome! This program will create a bar graph using the statistics'
          ' of an NBA or WNBA player. \n')

    while True:
        run()  # always attempt one graph (single or compare)

        again = input("Make another graph? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
