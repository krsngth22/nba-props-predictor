import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_connection
from ingestion.logger import get_logger

logger = get_logger(__name__)

def run_health_check():
    print("\n" + "=" * 50)
    print("DATABASE HEALTH CHECK")
    print("=" * 50)
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM teams")
        teams_count = cur.fetchone()[0]
        print(f"Teams           : {teams_count}")

        cur.execute("SELECT COUNT(*) FROM players WHERE is_active = true")
        players_count = cur.fetchone()[0]
        print(f"Active players  : {players_count}")

        cur.execute("SELECT COUNT(*) FROM player_game_stats")
        stats_count = cur.fetchone()[0]
        print(f"Stat rows       : {stats_count}")

        cur.execute("SELECT COUNT(DISTINCT player_id) FROM player_game_stats")
        unique_players = cur.fetchone()[0]
        print(f"Players w/ data : {unique_players}")

        cur.execute("SELECT COUNT(DISTINCT season) FROM player_game_stats")
        seasons = cur.fetchone()[0]
        print(f"Seasons         : {seasons}")

        cur.execute("SELECT MIN(game_date), MAX(game_date) FROM player_game_stats")
        date_range = cur.fetchone()
        print(f"Date range      : {date_range[0]} → {date_range[1]}")

        cur.execute("""
            SELECT p.full_name, COUNT(*) as games,
                   ROUND(AVG(pgs.points)::numeric, 1) as avg_pts
            FROM player_game_stats pgs
            JOIN players p ON pgs.player_id = p.player_id
            GROUP BY p.full_name
            ORDER BY avg_pts DESC
            LIMIT 5
        """)
        print("\nTop 5 scorers in your database:")
        print(f"  {'Player':<25} {'Games':>6} {'Avg Pts':>8}")
        print(f"  {'-'*25} {'-'*6} {'-'*8}")
        for row in cur.fetchall():
            print(f"  {row[0]:<25} {row[1]:>6} {row[2]:>8}")

        cur.close()
        conn.close()
        print("\nHealth check passed.")

    except Exception as e:
        print(f"Health check FAILED: {e}")

    print("=" * 50 + "\n")

if __name__ == "__main__":
    run_health_check()
