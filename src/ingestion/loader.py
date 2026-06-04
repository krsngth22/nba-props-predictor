import logging
import psycopg2
from psycopg2.extras import execute_values
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_connection

logger = logging.getLogger(__name__)

def load_teams(teams_df):
    conn = get_connection()
    cur = conn.cursor()
    rows = [
        (
            row['team_id'],
            row['abbreviation'],
            row['full_name'],
            row['city'],
            row['state']
        )
        for _, row in teams_df.iterrows()
    ]
    execute_values(cur, """
        INSERT INTO teams (team_id, abbreviation, full_name, city, state)
        VALUES %s
        ON CONFLICT (team_id) DO UPDATE SET
            abbreviation = EXCLUDED.abbreviation,
            full_name = EXCLUDED.full_name,
            city = EXCLUDED.city,
            state = EXCLUDED.state
    """, rows)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"Loaded {len(rows)} teams into database")

def load_players(players_df):
    conn = get_connection()
    cur = conn.cursor()
    rows = [
        (
            row['player_id'],
            row['full_name'],
            row['is_active']
        )
        for _, row in players_df.iterrows()
    ]
    execute_values(cur, """
        INSERT INTO players (player_id, full_name, is_active)
        VALUES %s
        ON CONFLICT (player_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            is_active = EXCLUDED.is_active
    """, rows)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"Loaded {len(rows)} players into database")

def load_player_stats(stats_df):
    if stats_df is None or len(stats_df) == 0:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    rows = [
        (
            row['player_id'],
            row['game_id'],
            row['game_date'],
            row['season'],
            row['matchup'],
            row['home_away'],
            row['minutes_played'],
            row['points'],
            row['rebounds'],
            row['assists'],
            row['steals'],
            row['blocks'],
            row['turnovers'],
            row['fg_attempted'],
            row['fg_made'],
            row['fg3_attempted'],
            row['fg3_made'],
            row['ft_attempted'],
            row['ft_made']
        )
        for _, row in stats_df.iterrows()
    ]
    execute_values(cur, """
        INSERT INTO player_game_stats (
            player_id, game_id, game_date, season, matchup, home_away,
            minutes_played, points, rebounds, assists, steals, blocks,
            turnovers, fg_attempted, fg_made, fg3_attempted, fg3_made,
            ft_attempted, ft_made
        )
        VALUES %s
        ON CONFLICT (player_id, game_id) DO UPDATE SET
            points = EXCLUDED.points,
            rebounds = EXCLUDED.rebounds,
            assists = EXCLUDED.assists,
            minutes_played = EXCLUDED.minutes_played
    """, rows)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"Loaded {len(rows)} stat rows for player {stats_df['player_id'].iloc[0]}")
    return len(rows)
