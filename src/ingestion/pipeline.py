import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.fetcher import get_all_teams, get_active_players, get_player_gamelog
from ingestion.transformer import transform_teams, transform_players, transform_gamelog
from ingestion.loader import load_teams, load_players, load_player_stats
from ingestion.validator import validate_teams_df, validate_players_df, validate_stats_df
from ingestion.logger import get_logger

logger = get_logger(__name__)

SEASONS = ['2023-24', '2024-25']
MAX_PLAYERS = 50

def run_pipeline(max_players=MAX_PLAYERS):
    logger.info("=" * 50)
    logger.info("Pipeline started")
    stats = {
        'players_processed': 0,
        'rows_loaded': 0,
        'errors': 0,
        'skipped': 0
    }

    logger.info("Step 1: Loading teams...")
    try:
        raw_teams = get_all_teams()
        teams_df = transform_teams(raw_teams)
        errors = validate_teams_df(teams_df)
        if not errors:
            load_teams(teams_df)
        else:
            logger.error(f"Skipping teams load due to validation errors: {errors}")
            stats['errors'] += 1
    except Exception as e:
        logger.error(f"Teams step failed: {e}")
        stats['errors'] += 1

    logger.info("Step 2: Loading players...")
    try:
        raw_players = get_active_players()
        players_df = transform_players(raw_players)
        errors = validate_players_df(players_df)
        if not errors:
            load_players(players_df)
        else:
            logger.error(f"Skipping players load due to validation errors: {errors}")
            stats['errors'] += 1
    except Exception as e:
        logger.error(f"Players step failed: {e}")
        stats['errors'] += 1

    logger.info("Step 3: Loading player game stats...")
    player_ids = players_df['player_id'].tolist()[:max_players]

    for season in SEASONS:
        logger.info(f"Fetching season {season}...")
        for i, player_id in enumerate(player_ids):
            logger.info(f"  Player {i+1}/{len(player_ids)} (id={player_id}) season={season}")
            try:
                raw_log = get_player_gamelog(player_id, season)
                if raw_log is None or len(raw_log) == 0:
                    stats['skipped'] += 1
                    continue
                stats_df = transform_gamelog(raw_log, player_id)
                validation_errors = validate_stats_df(stats_df, player_id)
                if stats_df is not None:
                    rows_loaded = load_player_stats(stats_df)
                    stats['rows_loaded'] += rows_loaded
                    stats['players_processed'] += 1
            except Exception as e:
                logger.error(f"Failed for player {player_id} season {season}: {e}")
                stats['errors'] += 1
                continue

    logger.info("=" * 50)
    logger.info(f"Pipeline complete.")
    logger.info(f"  Players processed : {stats['players_processed']}")
    logger.info(f"  Rows loaded       : {stats['rows_loaded']}")
    logger.info(f"  Skipped           : {stats['skipped']}")
    logger.info(f"  Errors            : {stats['errors']}")
    logger.info("=" * 50)
    return stats

if __name__ == "__main__":
    run_pipeline()
