import pandas as pd
import logging

logger = logging.getLogger(__name__)

def transform_teams(raw_teams):
    df = pd.DataFrame(raw_teams)
    transformed = pd.DataFrame({
        'team_id': df['id'],
        'abbreviation': df['abbreviation'],
        'full_name': df['full_name'],
        'city': df['city'],
        'state': df['state']
    })
    logger.info(f"Transformed {len(transformed)} teams")
    return transformed

def transform_players(raw_players):
    df = pd.DataFrame(raw_players)
    transformed = pd.DataFrame({
        'player_id': df['id'],
        'full_name': df['full_name'],
        'is_active': df['is_active']
    })
    logger.info(f"Transformed {len(transformed)} players")
    return transformed

def transform_gamelog(df, player_id):
    if df is None or len(df) == 0:
        return None
    try:
        transformed = pd.DataFrame({
            'player_id': player_id,
            'game_id': df['Game_ID'],
            'game_date': pd.to_datetime(df['GAME_DATE'], format='%b %d, %Y'),
            'season': df['SEASON_ID'],
            'matchup': df['MATCHUP'],
            'home_away': df['MATCHUP'].apply(lambda x: 'home' if 'vs.' in x else 'away'),
            'minutes_played': pd.to_numeric(df['MIN'], errors='coerce'),
            'points': pd.to_numeric(df['PTS'], errors='coerce').fillna(0).astype(int),
            'rebounds': pd.to_numeric(df['REB'], errors='coerce').fillna(0).astype(int),
            'assists': pd.to_numeric(df['AST'], errors='coerce').fillna(0).astype(int),
            'steals': pd.to_numeric(df['STL'], errors='coerce').fillna(0).astype(int),
            'blocks': pd.to_numeric(df['BLK'], errors='coerce').fillna(0).astype(int),
            'turnovers': pd.to_numeric(df['TOV'], errors='coerce').fillna(0).astype(int),
            'fg_attempted': pd.to_numeric(df['FGA'], errors='coerce').fillna(0).astype(int),
            'fg_made': pd.to_numeric(df['FGM'], errors='coerce').fillna(0).astype(int),
            'fg3_attempted': pd.to_numeric(df['FG3A'], errors='coerce').fillna(0).astype(int),
            'fg3_made': pd.to_numeric(df['FG3M'], errors='coerce').fillna(0).astype(int),
            'ft_attempted': pd.to_numeric(df['FTA'], errors='coerce').fillna(0).astype(int),
            'ft_made': pd.to_numeric(df['FTM'], errors='coerce').fillna(0).astype(int),
        })
        logger.info(f"Transformed {len(transformed)} game rows for player {player_id}")
        return transformed
    except Exception as e:
        logger.error(f"Transform failed for player {player_id}: {e}")
        return None
