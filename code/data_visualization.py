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

CAREER_STAT_MAP = {
    "ppg": ("PTS", "Points Per Game"),
    "rpg": ("REB", "Rebounds Per Game"),
    "apg": ("AST", "Assists Per Game"),
    "spg": ("STL", "Steals Per Game"),
    "bpg": ("BLK", "Blocks Per Game"),
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


def make_stats_bar_graph(players_list: list[dict]):
    """
    Creates a bar chart for 1+ players.
    """

    if not players_list:
        raise ValueError("players_list cannot be empty.")

    # Build long-format data
    data = []
    for p in players_list:
        series = p["stats"]
        # For single player, you can keep it clean; for multi, include season in label
        if len(players_list) == 1:
            player_label = p["name"]
        else:
            player_label = f'{p["name"]} ({p["season_label"]})'

        for stat in STAT_KEYS:
            data.append({
                "Statistic": STAT_LABELS[stat],
                "Value": series[stat],
                "Player": player_label,
            })

    # Title + barmode
    if len(players_list) == 1:
        p = players_list[0]
        title = f'{p["name"]} - Averages per Game ({p["season_label"]})'
        barmode = None  # default
        text_size = 16
    else:
        title = "Comparison - Averages per Game"
        barmode = "group"
        text_size = 14

    fig = px.bar(
        data,
        x="Statistic",
        y="Value",
        color="Player",
        barmode=barmode,
        text_auto=True,
        title=title
    )

    fig.update_layout(
        title_x=0.5,
        yaxis_title="Per Game",
        xaxis_title=""
    )
    fig.update_traces(textfont_size=text_size, textposition="outside")

    # Filename
    if len(players_list) == 1:
        p = players_list[0]
        filename = sanitize_filename(f'{p["name"]}_{p["season_label"]}.html')
    else:
        parts = [f'{p["name"]}{p["season_label"]}' for p in players_list]
        filename = sanitize_filename(f"{'_vs_'.join(parts)}.html")

    fig.write_html(filename)
    return filename



def make_multi_player_single_stat_career_graph(players_list: list[dict], stat_code: str):
    """
    Multi-player line chart across seasons with ONE stat.
    players_list items must include: {"name": str, "career_df": pd.DataFrame}
    stat_code: "ppg", "rpg", "apg", "spg", "bpg"
    Returns: filename
    """
    if not players_list:
        raise ValueError("players_list cannot be empty.")

    stat_code = stat_code.strip().lower()
    if stat_code not in CAREER_STAT_MAP:
        raise ValueError("Invalid stat code.")

    col, y_label = CAREER_STAT_MAP[stat_code]

    frames = []
    for p in players_list:
        # Check if column exists
        if col not in p["career_df"].columns:
            continue
            
        df = p["career_df"][["SEASON_ID", col]].copy()
        
        # Clean season format
        df["SEASON_ID"] = df["SEASON_ID"].astype(str).str.strip()
        
        # Drop NaN values for cleaner plotting
        df = df.dropna(subset=[col])
        
        if len(df) == 0:
            continue  # Skip players with no data for this stat
            
        df.rename(columns={"SEASON_ID": "Season", col: "Value"}, inplace=True)
        df["Player"] = p["name"]
        frames.append(df)

    if not frames:
        raise ValueError("No valid data to plot.")
        
    df_all = pd.concat(frames, ignore_index=True)
    
    # Get all unique seasons and sort them properly
    all_seasons = sorted(set(df_all['Season']))
    
    # Convert to categorical to preserve all seasons in plot
    df_all['Season_Cat'] = pd.Categorical(df_all['Season'], categories=all_seasons, ordered=True)
    
    # Sort by season and player
    df_all = df_all.sort_values(['Season_Cat', 'Player'])
    
    # Create the plot
    player_names = [p["name"] for p in players_list]
    title = f"{y_label}: {', '.join(player_names)}"
    fig = px.line(
        df_all,
        x="Season",
        y="Value",
        color="Player",
        markers=True,
        title=title
    )
    
    # Force all seasons to show by setting x-axis range
    fig.update_layout(
        title_x=0.5,
        xaxis_title="",
        yaxis_title=y_label,
        xaxis={'type': 'category'},
        xaxis_range=[-0.5, len(all_seasons) - 0.5]  # This prevents cutting off data
    )
    
    # Lines break at missing data (connectgaps=False)
    fig.update_traces(connectgaps=False)
    
    # Generate filename
    name_part = "_vs_".join([p["name"] for p in players_list])
    filename = sanitize_filename(f"{name_part}_{stat_code}_career.html")
    fig.write_html(filename)
    
    return filename