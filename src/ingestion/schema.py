import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_connection

def create_tables():
    commands = [
        """
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY,
            abbreviation VARCHAR(10),
            full_name VARCHAR(100),
            city VARCHAR(100),
            state VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            full_name VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS player_game_stats (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(player_id),
            game_id VARCHAR(20),
            game_date DATE,
            season VARCHAR(10),
            matchup VARCHAR(30),
            home_away VARCHAR(5),
            minutes_played FLOAT,
            points INTEGER,
            rebounds INTEGER,
            assists INTEGER,
            steals INTEGER,
            blocks INTEGER,
            turnovers INTEGER,
            fg_attempted INTEGER,
            fg_made INTEGER,
            fg3_attempted INTEGER,
            fg3_made INTEGER,
            ft_attempted INTEGER,
            ft_made INTEGER,
            UNIQUE(player_id, game_id)
        )
        """
    ]
    conn = get_connection()
    cur = conn.cursor()
    for command in commands:
        cur.execute(command)
    conn.commit()
    cur.close()
    conn.close()
    print("All tables created successfully.")

if __name__ == "__main__":
    create_tables()
