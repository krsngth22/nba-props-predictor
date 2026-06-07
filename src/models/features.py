import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.logger import get_logger

logger = get_logger(__name__)

def load_raw_data(conn):
    query = """
        SELECT
            pgs.id,
            pgs.player_id,
            p.full_name,
            pgs.game_id,
            pgs.game_date,
            pgs.season,
            pgs.home_away,
            pgs.opponent_abbr,
            pgs.minutes_played,
            pgs.points,
            pgs.rebounds,
            pgs.assists,
            pgs.steals,
            pgs.blocks,
            pgs.turnovers,
            pgs.fg_made,
            pgs.fg_attempted,
            pgs.fg3_made,
            pgs.fg3_attempted,
            pgs.ft_made,
            pgs.ft_attempted
        FROM player_game_stats pgs
        JOIN players p ON pgs.player_id = p.player_id
        ORDER BY pgs.player_id, pgs.game_date ASC
    """
    df = pd.read_sql(query, conn)
    df['game_date'] = pd.to_datetime(df['game_date'])
    logger.info(f"Loaded {len(df)} raw rows for {df['player_id'].nunique()} players")
    return df

def load_opponent_stats(conn):
    query = """
        SELECT
            opponent_abbr,
            season,
            avg_pts_allowed,
            avg_reb_allowed,
            avg_ast_allowed
        FROM opponent_defensive_stats
    """
    df = pd.read_sql(query, conn)
    logger.info(f"Loaded opponent stats for {df['opponent_abbr'].nunique()} teams")
    return df

def add_rolling_features(df, windows=[5, 10, 20]):
    logger.info("Adding rolling average features...")
    result = []
    for player_id, group in df.groupby('player_id'):
        group = group.sort_values('game_date').copy()
        for stat in ['points', 'rebounds', 'assists', 'minutes_played', 'turnovers']:
            for window in windows:
                col_name = f'{stat}_roll_{window}'
                group[col_name] = (
                    group[stat]
                    .shift(1)
                    .rolling(window=window, min_periods=1)
                    .mean()
                )
        result.append(group)
    df = pd.concat(result, ignore_index=True)
    logger.info(f"Rolling features added. Shape: {df.shape}")
    return df

def add_lag_features(df, lags=[1, 2, 3]):
    logger.info("Adding lag features...")
    result = []
    for player_id, group in df.groupby('player_id'):
        group = group.sort_values('game_date').copy()
        for stat in ['points', 'rebounds', 'assists', 'minutes_played']:
            for lag in lags:
                col_name = f'{stat}_lag_{lag}'
                group[col_name] = group[stat].shift(lag)
        result.append(group)
    df = pd.concat(result, ignore_index=True)
    logger.info(f"Lag features added. Shape: {df.shape}")
    return df

def add_efficiency_features(df):
    logger.info("Adding efficiency features...")
    df['fg_pct'] = np.where(df['fg_attempted'] > 0, df['fg_made'] / df['fg_attempted'], 0)
    df['fg3_pct'] = np.where(df['fg3_attempted'] > 0, df['fg3_made'] / df['fg3_attempted'], 0)
    df['ft_pct'] = np.where(df['ft_attempted'] > 0, df['ft_made'] / df['ft_attempted'], 0)
    df['true_shooting_pct'] = np.where(
        (2 * (df['fg_attempted'] + 0.44 * df['ft_attempted'])) > 0,
        df['points'] / (2 * (df['fg_attempted'] + 0.44 * df['ft_attempted'])),
        0
    )
    df['assist_turnover_ratio'] = np.where(df['turnovers'] > 0, df['assists'] / df['turnovers'], df['assists'])
    df['points_per_minute'] = np.where(df['minutes_played'] > 0, df['points'] / df['minutes_played'], 0)
    logger.info(f"Efficiency features added. Shape: {df.shape}")
    return df

def add_game_context_features(df):
    logger.info("Adding game context features...")
    df['is_home'] = (df['home_away'] == 'home').astype(int)
    df['game_date'] = pd.to_datetime(df['game_date'])
    df['day_of_week'] = df['game_date'].dt.dayofweek
    df['month'] = df['game_date'].dt.month
    result = []
    for player_id, group in df.groupby('player_id'):
        group = group.sort_values('game_date').copy()
        group['days_rest'] = group['game_date'].diff().dt.days.fillna(3).clip(upper=10)
        group['is_back_to_back'] = (group['days_rest'] == 1).astype(int)
        group['game_number'] = range(1, len(group) + 1)
        result.append(group)
    df = pd.concat(result, ignore_index=True)
    logger.info(f"Context features added. Shape: {df.shape}")
    return df

def add_opponent_features(df, opponent_stats_df):
    logger.info("Adding opponent defensive features...")
    df = df.merge(
        opponent_stats_df.rename(columns={
            'avg_pts_allowed': 'opp_avg_pts_allowed',
            'avg_reb_allowed': 'opp_avg_reb_allowed',
            'avg_ast_allowed': 'opp_avg_ast_allowed'
        }),
        on=['opponent_abbr', 'season'],
        how='left'
    )
    for col in ['opp_avg_pts_allowed', 'opp_avg_reb_allowed', 'opp_avg_ast_allowed']:
        df[col] = df[col].fillna(df[col].mean())
    logger.info(f"Opponent features added. Shape: {df.shape}")
    return df

def build_feature_matrix(conn, target='points'):
    logger.info(f"Building feature matrix for target: {target}")
    df = load_raw_data(conn)
    opponent_stats = load_opponent_stats(conn)
    df = add_rolling_features(df)
    df = add_lag_features(df)
    df = add_efficiency_features(df)
    df = add_game_context_features(df)
    df = add_opponent_features(df, opponent_stats)
    df = df.dropna(subset=[f'{target}_lag_1'])
    feature_cols = (
        [c for c in df.columns if '_roll_' in c] +
        [c for c in df.columns if '_lag_' in c] +
        ['fg_pct', 'fg3_pct', 'ft_pct', 'true_shooting_pct',
         'assist_turnover_ratio', 'points_per_minute',
         'is_home', 'day_of_week', 'month',
         'days_rest', 'is_back_to_back', 'game_number',
         'opp_avg_pts_allowed', 'opp_avg_reb_allowed', 'opp_avg_ast_allowed']
    )
    feature_cols = [c for c in feature_cols if c in df.columns]
    logger.info(f"Feature matrix ready: {len(df)} rows, {len(feature_cols)} features")
    return df, feature_cols

if __name__ == "__main__":
    from db import get_connection
    conn = get_connection()
    df, feature_cols = build_feature_matrix(conn)
    print(f"\nFeature matrix shape: {df.shape}")
    print(f"Number of features: {len(feature_cols)}")
    print(f"\nFeature list:")
    for f in feature_cols:
        print(f"  {f}")
    print(f"\nSample (first 3 rows):")
    print(df[feature_cols].head(3).to_string())
