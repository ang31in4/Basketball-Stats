import plotly.express as px
import pandas as pd
pd.options.plotting.backend = "plotly"

STAT_KEYS = ["PTS", "REB", "AST", "STL", "BLK"]

STAT_LABELS = {
    "PTS": "Points",
    "REB": "Rebounds",
    "AST": "Assists",
    "STL": "Steals",
    "BLK": "Blocks",
}

def sanitize_filename(text: str) -> str:
    """
    Remove possible invalid characters from player name.
    """
    return (
        text.replace(" ", "_")
            .replace("/", "-")
            .replace("\\", "-")
            .lower()
    )

def make_graph(player_name: str, player_stats: pd.Series, season_id: str):
    """
    Creates a bar chart for a single player.
    """

    header = f'{player_name} - Averages per Game ({season_id})'

    data = [
        {
            "Statistic": STAT_LABELS[stat],
            "Value": player_stats[stat],
            "Player": player_name
        }
        for stat in STAT_KEYS
    ]

    fig = px.bar(
        data,
        x="Statistic",
        y="Value",
        color="Player",
        text_auto=True
    )

    fig.update_layout(
        title=header,
        title_x=0.5,
        yaxis_title="Per Game",
        xaxis_title=""
    )

    fig.update_traces(textfont_size=16, textposition="outside")

    filename = sanitize_filename(f"{player_name}_{season_id}_stats.html")
    fig.write_html(filename)


def make_comparison_graph( p1_name: str, p1_stats: pd.Series, p1_season: str, p2_name: str, p2_stats: pd.Series, p2_season: str):
    """
    Creates a grouped bar chart comparing two players.
    """

    header = (
        f'{p1_name} ({p1_season}) vs '
        f'{p2_name} ({p2_season}) - Averages per Game'
    )

    data = []

    for stat in STAT_KEYS:
        data.append({
            "Statistic": STAT_LABELS[stat],
            "Value": p1_stats[stat],
            "Player": p1_name
        })
        data.append({
            "Statistic": STAT_LABELS[stat],
            "Value": p2_stats[stat],
            "Player": p2_name
        })

    fig = px.bar(
        data,
        x="Statistic",
        y="Value",
        color="Player",
        barmode="group",
        text_auto=True
    )

    fig.update_layout(
        title=header,
        title_x=0.5,
        yaxis_title="Per Game",
        xaxis_title=""
    )

    fig.update_traces(textfont_size=16, textposition="outside")

    filename = sanitize_filename(f"{p1_name}_{p1_season}_vs_{p2_name}_{p2_season}.html")
    fig.write_html(filename)