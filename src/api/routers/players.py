from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from src.api.deps import get_db
from src.api.schemas import PlayerResponse, GameStatResponse

router = APIRouter(prefix="/players", tags=["players"])

@router.get("/", response_model=List[PlayerResponse])
def get_players(
    search: Optional[str] = Query(None, description="Search by player name"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    query = "SELECT player_id, full_name, is_active FROM players WHERE is_active = true"
    params = {}

    if search:
        query += " AND LOWER(full_name) LIKE :search"
        params['search'] = f"%{search.lower()}%"

    query += " ORDER BY full_name LIMIT :limit"
    params['limit'] = limit

    result = db.execute(text(query), params).fetchall()
    return [
        PlayerResponse(player_id=r[0], full_name=r[1], is_active=r[2])
        for r in result
    ]

@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT player_id, full_name, is_active FROM players WHERE player_id = :id"),
        {"id": player_id}
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")

    return PlayerResponse(player_id=result[0], full_name=result[1], is_active=result[2])

@router.get("/{player_id}/stats", response_model=List[GameStatResponse])
def get_player_stats(
    player_id: int,
    season: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    query = """
        SELECT game_date, matchup, home_away, points, rebounds,
               assists, minutes_played, opponent_abbr
        FROM player_game_stats
        WHERE player_id = :player_id
    """
    params = {"player_id": player_id}

    if season:
        query += " AND season = :season"
        params['season'] = season

    query += " ORDER BY game_date DESC LIMIT :limit"
    params['limit'] = limit

    result = db.execute(text(query), params).fetchall()

    if not result:
        raise HTTPException(status_code=404, detail=f"No stats found for player {player_id}")

    return [
        GameStatResponse(
            game_date=r[0],
            matchup=r[1],
            home_away=r[2],
            points=r[3],
            rebounds=r[4],
            assists=r[5],
            minutes_played=r[6],
            opponent_abbr=r[7]
        )
        for r in result
    ]
