import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.logger import get_logger

logger = get_logger(__name__)

REQUIRED_STAT_COLUMNS = [
    'player_id', 'game_id', 'game_date', 'season',
    'points', 'rebounds', 'assists', 'minutes_played'
]

def validate_teams_df(df):
    errors = []
    if df is None or len(df) == 0:
        errors.append("Teams DataFrame is empty")
        return errors
    for col in ['team_id', 'abbreviation', 'full_name']:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    if df['team_id'].duplicated().any():
        errors.append("Duplicate team_ids found")
    if df['team_id'].isnull().any():
        errors.append("Null team_ids found")
    if errors:
        logger.warning(f"Teams validation failed: {errors}")
    else:
        logger.info(f"Teams validation passed: {len(df)} rows")
    return errors

def validate_players_df(df):
    errors = []
    if df is None or len(df) == 0:
        errors.append("Players DataFrame is empty")
        return errors
    for col in ['player_id', 'full_name']:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    if df['player_id'].duplicated().any():
        errors.append("Duplicate player_ids found")
    if df['player_id'].isnull().any():
        errors.append("Null player_ids found")
    if errors:
        logger.warning(f"Players validation failed: {errors}")
    else:
        logger.info(f"Players validation passed: {len(df)} rows")
    return errors

def validate_stats_df(df, player_id):
    errors = []
    if df is None or len(df) == 0:
        return errors
    for col in REQUIRED_STAT_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    if 'points' in df.columns:
        if (df['points'] < 0).any():
            errors.append(f"Negative points found for player {player_id}")
        if (df['points'] > 100).any():
            errors.append(f"Suspiciously high points (>100) for player {player_id}")
    if 'minutes_played' in df.columns:
        if (df['minutes_played'] < 0).any():
            errors.append(f"Negative minutes for player {player_id}")
        if (df['minutes_played'] > 60).any():
            errors.append(f"Minutes > 60 for player {player_id}")
    if 'rebounds' in df.columns:
        if (df['rebounds'] < 0).any():
            errors.append(f"Negative rebounds for player {player_id}")
    if 'game_id' in df.columns:
        if df['game_id'].duplicated().any():
            logger.warning(f"Duplicate game_ids for player {player_id} — will be handled by upsert")
    if errors:
        logger.warning(f"Stats validation warnings for player {player_id}: {errors}")
    else:
        logger.info(f"Stats validation passed for player {player_id}: {len(df)} rows")
    return errors
