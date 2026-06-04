import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.fetcher import get_all_teams, get_active_players, get_player_gamelog
from ingestion.transformer import transform_teams, transform_players, transform_gamelog
from ingestion.loader import load_teams, load_players, load_player_stats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SEASONS = ['2023-24', '2024-25']
MAX_PLAYERS = 50

def run_pipeline(max_players=MAX_PLAYERS):
    logger.info("Pipeline started")

    logger.info("Step 1: Loading teams...")
    raw_teams = get_all_teams()
    teams_df = transform_teams(raw_teams)
    load_teams(teams_df)

    logger.info("Step 2: Loading players...")
    raw_players = get_active_players()
    players_df = transform_players(raw_players)
    load_players(players_df)

    logger.info("Step 3: Loading player game stats...")
    player_ids = players_df['player_id'].tolist()[:max_players]
    total_rows = 0

    for season in SEASONS:
        logger.info(f"Fetching season {season}...")
        for i, player_id in enumerate(player_ids):
            logger.info(f"  Player {i+1}/{len(player_ids)} (id={player_id}) season={season}")
            raw_log = get_player_gamelog(player_id, season)
            stats_df = transform_gamelog(raw_log, player_id)
            if stats_df is not None:
                rows_loaded = load_player_stats(stats_df)
                total_rows += rows_loaded

    logger.info(f"Pipeline complete. Total stat rows loaded: {total_rows}")

if __name__ == "__main__":
    run_pipeline()
