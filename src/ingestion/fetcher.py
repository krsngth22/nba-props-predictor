import time
import logging
from nba_api.stats.endpoints import playergamelog, commonallplayers
from nba_api.stats.static import players, teams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEASONS = ['2023-24', '2024-25']
REQUEST_DELAY = 1.0

def get_all_teams():
    all_teams = teams.get_teams()
    logger.info(f"Fetched {len(all_teams)} teams")
    return all_teams

def get_active_players():
    all_players = players.get_active_players()
    logger.info(f"Fetched {len(all_players)} active players")
    return all_players

def get_player_gamelog(player_id, season, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(REQUEST_DELAY)
            gamelog = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=season
            )
            df = gamelog.get_data_frames()[0]
            logger.info(f"Fetched {len(df)} games for player {player_id} season {season}")
            return df
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for player {player_id}: {e}")
            time.sleep(2 ** attempt)
    logger.error(f"All retries failed for player {player_id} season {season}")
    return None

def get_players_gamelogs(player_ids, season):
    all_logs = []
    for i, player_id in enumerate(player_ids):
        logger.info(f"Fetching player {i+1}/{len(player_ids)} (id={player_id})")
        df = get_player_gamelog(player_id, season)
        if df is not None and len(df) > 0:
            df['PLAYER_ID'] = player_id
            all_logs.append(df)
    return all_logs
